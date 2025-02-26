import random
import math
import time
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
        self.position = list(position)
        self.weight = initial_weight

    def move(self, x: float, y: float, theta: float):
        """
        Move the particle based on the provided displacements.

        :param x: The displacement in the x-axis.
        :param y: The displacement in the y-axis.
        :param theta: The rotation angle in radians.
        """
        self.position[0] += x
        self.position[1] += y
        self.position[2] += theta

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

    def move_std(self, distance: float, stds: tuple[float, float]):
        """
        Move the particle based on the provided standard deviations.

        :param distance: How far the particle moved.
        :param stds: The standard deviations for each of the positional and directional components.
        """
        distance = random.normalvariate(distance, stds[0])
        self.position[2] += random.normalvariate(0, stds[1])
        self.position[0] += math.sin(self.position[2]) * distance
        self.position[1] += math.cos(self.position[2]) * distance



class LocalisationMethod(Enum):
    CONTINUOUS: int = 1
    GLOBAL: int = 2

    @staticmethod
    def from_str(string):
        if string.lower() == "continuous":
            return LocalisationMethod.CONTINUOUS
        elif string.lower() == "global":
            return LocalisationMethod.GLOBAL
        else:
            raise ConfigurationException("[MCPositionEstimator] Invalid localisation option - must be 'continuous' or 'global'.")

class MonteCarloPositionEstimator(Consumer, Producer, Configurable):
    """
    MonteCarloPositionEstimator is responsible for estimating position using the Monte Carlo
    Localization algorithm. It utilizes particles to represent potential positions and combines sensory
    readings to refine the position estimate. The class integrates with defined message mechanisms
    to handle configuration, sensory data, and movement updates.

    Through particle filter techniques, it predicts positions based on a probabilistic approach.
    Its main goals are initialization of particles, estimation of the position, handling sensory
    messages, and particle resampling. It also maintains adherence to geofence constraints ensuring
    particles are within a defined boundary during estimation.

    :ivar localisation_str: Localisation mode as a string.
    :ivar localisation: Localisation mode as an enumeration.
    :ivar start_x: Starting x-coordinate of the estimation.
    :ivar start_y: Starting y-coordinate of the estimation.
    :ivar start_theta: Starting theta (angle) of the estimation.

    :ivar num_particles: Number of particles used in the estimation.
    :ivar particles: List of particles used in the estimation.
    :ivar geofence: Geofence object to constrain particles within boundaries.

    :ivar navigation_estimate: Navigation estimate message storing calculated position and orientation.
    """
    def __init__(self, hub: MessageHub):
        Consumer.__init__(self, hub)
        Producer.__init__(self, hub)
        Configurable.__init__(self, "MCPositionEstimator")
        self.localisation_str: str = "global"
        self.localisation: LocalisationMethod = LocalisationMethod.GLOBAL

        self.start_x: float = 0.0
        self.start_y: float = 0.0
        self.start_theta: float = 0.0

        self.num_particles: int = 0
        self.particles: list[NormalParticle] = []

        self.geofence: Geofence = Geofence()
        self.navigation_estimate: NavigationEstimate = NavigationEstimate(self.start_x, self.start_y, self.start_theta)

    def initialise(self, conf: Configuration = None):
        if conf is not None:
            self.set_conf(conf)

        self.localisation_str = self.conf.get_conf_str("MCPositionEstimator", "localisation")
        self.localisation: LocalisationMethod = LocalisationMethod.from_str(self.localisation_str)

        if self.localisation == LocalisationMethod.CONTINUOUS:
            self.start_x = self.conf.get_conf_num_f("MCPositionEstimator", "start_x")
            self.start_y = self.conf.get_conf_num_f("MCPositionEstimator", "start_y")
            start_theta_deg = self.conf.get_conf_num_f("MCPositionEstimator", "start_hed")
            self.start_theta = math.radians(start_theta_deg)

        self.num_particles = self.conf.get_conf_num("MCPositionEstimator", "num_particles")

        self.geofence.initialise(conf)
        self.navigation_estimate: NavigationEstimate = NavigationEstimate(self.start_x, self.start_y, self.start_theta)
        self.initialise_particles()

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
        # Allowing the motor to define the variations allows it to give its own
        # variation estimations
        distance_std: float = move_estimate.distance_std
        theta_std: float = move_estimate.theta_std

        print("----- Particles -----")
        for p in self.particles:
            print(p.position)

        # Update particle positions
        for particle in self.particles:
            particle.move_std(distance, (distance_std, theta_std))

        # Remove particles not in the bounding box
        self.particles = [particle for particle in self.particles if self.geofence.inside_geofence(particle.position[0], particle.position[1])]
        if len(self.particles) != self.num_particles:
            # Update weights to sum to zero
            self.normalise_weights()

        estimate: tuple[float, float, float] = self.estimate_position()
        self.navigation_estimate.x = estimate[0]
        self.navigation_estimate.y = estimate[1]
        self.navigation_estimate.theta = estimate[2]
        self.deliver(self.navigation_estimate)

    def estimate_position(self) -> tuple[float, float, float]:
        estimate: list[float] = [0.0, 0.0, 0.0]
        for particle in self.particles:
            estimate[0] += particle.get_x() * particle.weight
            estimate[1] += particle.get_y() * particle.weight
            estimate[2] += particle.get_theta() * particle.weight
        return estimate[0], estimate[1], estimate[2]

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
        cumulative_weights: list[float] = [self.particles[0].weight]
        for i, particle in enumerate(self.particles[1:]):
            cumulative_weights.append(cumulative_weights[i - 1] + particle.weight)

        new_particles: list[NormalParticle] = []
        for _ in range(self.num_particles):
            rand = random.uniform(0, cumulative_weights[-1])
            # TODO Binary search
            found = 0
            while rand > cumulative_weights[found]:
                found += 1

            new_particles.append(NormalParticle(self.particles[found].position, 1.0 / self.num_particles))

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