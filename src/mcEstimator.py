import random
import math
from statistics import NormalDist
from enum import Enum

from src.lib.geofence import Geofence
from src.messages import NavigationEstimate, SonarReading, MessageId, MoveEstimate
from src.message import Consumer, Producer, Message, MessageHub
from src.lib.configuration import Configurable, ConfigurationException, Configuration


class Particle:
    """
    Represents a particle in a 2D space.

    This class is designed to encapsulate the properties and attributes
    of a particle in three-dimensional Cartesian coordinates.

    :ivar position: The 2D coordinates of the particle in the form of a
        tuple (x, y, theta), where x, y, and theta are float values representing
        the respective Cartesian components and the direction of the particle.
    :ivar weight: The weight of the particle, representing its probability of
        being in its current position.
    """
    def __init__(self, position: tuple[float, float, float], initial_weight: float):
        self.position = position
        self.weight = initial_weight

    def move(self, x: float, y: float, theta: float):
        """
        Move the particle based on the provided displacements.

        :param x: The displacement in the x-axis.
        :param y: The displacement in the y-axis.
        :param theta: The rotation angle in radians.
        """
        self.position += (x, y, theta)

    def get_x(self):
        return self.position[0]

    def get_y(self):
        return self.position[1]

    def get_theta(self):
        return self.position[2]


class NormalParticle(Particle):
    """
    Represents a normally distributed particle in a 2D coordinate space.

    This class extends the functionality of a generic Particle by incorporating
    attributes and behavior specific to particles modeled based on a normal
    distribution. It allows defining parameters like mean and standard deviation
    for both positional and directional characteristics, offering greater control
    over particle simulations or modeling.
    """
    def __init__(self,  position: tuple[float, float, float], initial_weight: float):
        super().__init__(position, initial_weight)

    def move_std(self, distance: float, theta: float, stds: tuple[float, float]):
        """
        Move the particle based on the provided standard deviations.

        :param distance: How far the particle moved.
        :param theta: The direction of travel in radians.
        :param stds: The standard deviations for each of the positional and directional components.
        """
        distance = random.normalvariate(distance, stds[0])
        theta = random.normalvariate(theta, stds[1])

        self.position += (math.cos(theta) * distance, math.sin(theta) * distance, theta)


class LocalisationMethod(Enum):
    CONTINUOUS: int = 1
    GLOBAL: int = 2

    @staticmethod
    def from_str(string):
        if string.upper() == "continuous":
            return LocalisationMethod.CONTINUOUS
        elif string.upper() == "global":
            return LocalisationMethod.GLOBAL
        else:
            raise ConfigurationException("[MCPositionEstimator] Invalid localisation option - must be 'continuous' or 'global'.")

class MonteCarloPositionEstimator(Consumer, Producer, Configurable):
    def __init__(self, hub: MessageHub):
        super().__init__(hub)
        self.std_x: float = 0.0
        self.std_y: float = 0.0
        self.std_theta: float = 0.0

        self.localisation_str: str = "global"
        self.localisation: LocalisationMethod = LocalisationMethod.GLOBAL

        self.start_x: float = 0.0
        self.start_y: float = 0.0
        self.start_theta: float = 0.0

        self.num_particles: int = 100
        self.particles: list[NormalParticle] = []
        self.initialise_particles()

        self.geofence: Geofence = Geofence()

    def initialise(self, conf: Configuration = None):
        if conf is not None:
            self.set_conf(conf)

        self.localisation_str = self.conf.get_conf_str("MCPositionEstimator", "localisation")
        self.localisation: LocalisationMethod = LocalisationMethod.from_str(self.localisation_str)

        if self.localisation == LocalisationMethod.CONTINUOUS:
            self.start_x = self.conf.get_conf_num_f("MCPositionEstimator", "start_x")
            self.start_y = self.conf.get_conf_num_f("MCPositionEstimator", "start_y")
            self.start_theta = self.conf.get_conf_num_f("MCPositionEstimator", "start_theta")

        self.num_particles = self.conf.get_conf_num("MCPositionEstimator", "num_particles")

        self.geofence.initialise()

    def initialise_particles(self) -> None:
        # Initialise particles
        self.particles = []
        for _ in range(self.num_particles):
            if self.localisation == LocalisationMethod.CONTINUOUS:
                self.particles.append(NormalParticle((self.start_x, self.start_y, self.start_theta), 1.0 / self.num_particles))
            elif self.localisation == LocalisationMethod.GLOBAL:
                positions: list[tuple[float, float]] = self.geofence.get_random_positions(self.num_particles)
                thetas: list[float] = [random.uniform(0, 2 * math.pi) for _ in range(self.num_particles)]

                # TODO Make this use numpy
                particles: list[tuple[float, float, float]] = [(part[0][0], part[0][1], part[1]) for part in zip(positions, thetas)]
                self.particles = [NormalParticle(particle, 1.0 / self.num_particles) for particle in particles]

    def handle_move_estimate(self, move_estimate: MoveEstimate):
        distance: float = move_estimate.distance
        theta: float = move_estimate.theta

        # Allowing the motor to define the variations allows it to give its own
        # variation estimations
        distance_std: float = move_estimate.distance_std
        theta_std: float = move_estimate.theta_std

        # Update particle positions
        for particle in self.particles:
            particle.move_std(distance, theta, (distance_std, theta_std))

        # Remove particles not in the bounding box
        self.particles = [particle for particle in self.particles if self.geofence.inside_geofence(particle.position[0], particle.position[1])]
        if len(self.particles) != self.num_particles:
            # Update weights to sum to zero
            self.normalise_weights()

    def normalise_weights(self):
        total_weight: float = sum(particle.weight for particle in self.particles)

        if total_weight == 0:
            for particle in self.particles:
                particle.weight = 1.0 / self.num_particles
        else:
            for particle in self.particles:
                particle.weight /= total_weight

    def handle_sonar_reading(self, sonar_reading: SonarReading):
        reading: float = sonar_reading.reading_m
        std: float = sonar_reading.std
        constant_std: float = sonar_reading.constant_std
        normal_std: float = sonar_reading.normal_std

        inv_normal = NormalDist(0, normal_std).inv_cdf

        # Update weights according to the probability of the sonar reading and
        # the normal angle to the wall
        for particle in self.particles:
            geo_result = self.geofence.distance_to_closest_wall(particle.get_x(), particle.get_y(), particle.get_theta())
            if geo_result is not None:
                distance, normal = geo_result
                likelihood: float = math.exp(-(distance - reading) * (distance - reading) / (2 * std * std))
                likelihood *= inv_normal(normal)
                likelihood += constant_std
                particle.weight *= likelihood

        self.normalise_weights()

    def resample_particles(self):
        # Build cumulative list with indexes
        cumulative_weights: list[tuple[float, float]] = [(self.particles[0].weight, 0)]
        for i, particle in enumerate(self.particles[1:]):
            cumulative_weights.append((cumulative_weights[i - 1][0] + particle.weight, i + 1))

        new_particles: list[NormalParticle] = []
        for _ in range(self.num_particles):
            rand = random.uniform(0, cumulative_weights[-1][0])

            # Binary search
            low, high = 0, len(cumulative_weights) - 1
            while low < high:
                mid = (low + high) // 2
                if cumulative_weights[mid][0] < rand:
                    low = mid + 1
                else:
                    high = mid
            index = low
            new_particles.append(NormalParticle(self.particles[index].position, 1.0 / self.num_particles))

    def send(self, message: Message):
        if isinstance(message, SonarReading):
            self.handle_sonar_reading(message)
        elif isinstance(message, MoveEstimate):
            self.handle_move_estimate(message)

    def get_consumed(self) -> list[MessageId]:
        return [
            MessageId.SONAR_READING,
            MessageId.MOVE_ESTIMATE
        ]