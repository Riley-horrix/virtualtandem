from numpy import random

from src.messages import NavigationEstimate, SonarReading, MessageId, MoveEstimate
from src.message import Consumer, Producer, Message, MessageHub
from src.lib.configuration import Configurable, ConfigurationException

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


class NormalParticle(Particle):
    """
    Represents a normally distributed particle in a 2D coordinate space.

    This class extends the functionality of a generic Particle by incorporating
    attributes and behavior specific to particles modeled based on a normal
    distribution. It allows defining parameters like mean and standard deviation
    for both positional and directional characteristics, offering greater control
    over particle simulations or modeling.
    """
    def __init__(self,  means: tuple[float, float, float], stds: tuple[float, float, float], initial_weight: float):
        super().__init__((random.normal(means[0], stds[0]), random.normal(means[1], stds[1]), random.normal(means[2], stds[2])), initial_weight)

    def move_std(self, x: float, y: float, theta: float, stds: tuple[float, float, float]):
        """
        Move the particle based on the provided standard deviations.

        :param x: Mean of the normal distribution in the x-axis.
        :param y: Mean of the normal distribution in the y-axis.
        :param theta: Mean of the normal distribution of the rotation angle in radians.
        :param stds: The standard deviations for each of the positional and
            directional components.
        """
        self.position += (random.normal(x, stds[0]), random.normal(y, stds[1]), random.normal(theta, stds[2]))


class MonteCarloPositionEstimator(Consumer, Producer, Configurable):
    def __init__(self, hub: MessageHub):
        super().__init__(hub)

        self.std_x = self.conf.get_conf_num_f("MCPositionEstimator", "std_x")
        self.std_y = self.conf.get_conf_num_f("MCPositionEstimator", "std_y")
        self.std_theta = self.conf.get_conf_num_f("MCPositionEstimator", "std_theta")

        self.localisation = self.conf.get_conf_str("MCPositionEstimator", "localisation")

        if self.localisation == "continuous":
            self.start_x = self.conf.get_conf_num_f("MCPositionEstimator", "start_x")
            self.start_y = self.conf.get_conf_num_f("MCPositionEstimator", "start_y")
            self.start_theta = self.conf.get_conf_num_f("MCPositionEstimator", "start_theta")

        self.num_particles = self.conf.get_conf_num("MCPositionEstimator", "num_particles")

        # Initialise particles
        self.particles = []
        for _ in range(self.num_particles):
            if self.localisation == "continuous":
                self.particles.append(NormalParticle((self.start_x, self.start_y, self.start_theta), (self.std_x, self.std_y, self.std_theta), 1.0 / self.num_particles))
            elif self.localisation == "global":
                self.particles.append(NormalParticle(self.__get_random_location(), (self.std_x, self.std_y, self.std_theta), 1.0 / self.num_particles))
            else:
                raise ConfigurationException("[MCPositionEstimator] Invalid localisation option - must be 'continuous' or 'global'.")

    def __get_random_location(self) -> tuple[float, float, float]:
        """
        Get a random location within the map.

        :return: A tuple containing the x, y, and theta coordinates of the random location.
        """
        return (0.0, 0.0, 0.0)

    def handle_move_estimate(self, move_request: MoveEstimate):
        pass

    def handle_sonar_reading(self, sonar_reading: SonarReading):
        pass

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