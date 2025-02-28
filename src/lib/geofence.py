import math
import random

from src.lib.configuration import Configurable, ConfigurationException, Configuration


class Geofence(Configurable):
    """
    Represents a geofence defined by a series of x,y points.

    Defines methods of checking if a point is within the geofence.

    Initialise with a list of (x, y) points, the first and last
    points are assumed to be the same.
    """
    def __init__(self):
        Configurable.__init__(self, "Geofence")

        self.points: list[tuple[float, float]] = []
        self.min_x: float = 0.0
        self.max_x: float = 0.0
        self.min_y: float = 0.0
        self.max_y: float = 0.0

    def initialise(self, conf: Configuration = None):
        if conf is not None:
            self.set_conf(conf)
        x_points = self.conf.get_conf_list_f("Geofence", "points_x")
        y_points = self.conf.get_conf_list_f("Geofence", "points_y")
        self.points = list(zip(x_points, y_points))

        if self.points[0][0] != self.points[-1][0] or self.points[0][1] != self.points[-1][1] :
            raise ConfigurationException("[Geofence]: Geofence points must define a closed polygon.")
        
        for point in self.points:
            self.min_x = min(self.min_x, point[0])
            self.max_x = max(self.max_x, point[0])
            self.min_y = min(self.min_y, point[1])
            self.max_y = max(self.max_y, point[1])

    def inside_geofence(self, x: float, y: float) -> bool:
        """
        Determines whether a point is inside a geofence defined by a series of
        coordinate points using the ray-casting algorithm. The function calculates
        the number of times a horizontal ray emanating from the point intersects
        the edges of the polygon. If the number of intersections is odd, the point
        is considered inside; otherwise, it is outside.

        :param x: The x-coordinate of the point to test.
        :param y: The y-coordinate of the point to test.
        :return: A boolean indicating whether the point (x, y) is inside the geofence.
        """
        intersections = 0
        
        # Check with bounding box
        if x < self.min_x or x > self.max_x or y < self.min_y or y > self.max_y:
            return False
        
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]

            # Check if the ray intersects with the edge (x1, y1) -> (x2, y2) by
            # casting a horizontal ray in the +ve x-axis.
            if (y >= min(y1, y2)) and (y <= max(y1, y2)) and (x <= max(x1, x2)):
                if y1 != y2:  # Avoid division by zero
                    x_intersect = (y - y1) * (x2 - x1) / (y2 - y1) + x1
                else:
                    x_intersect = min(x1, x2)

                # Check for intersection
                if x <= x_intersect:
                    intersections += 1

        # Odd number of intersections means the point is inside
        return intersections % 2 == 1

    def distance_to_closest_wall(self, x: float, y: float, theta: float) -> tuple[float, float]:
        """
        Calculates the shortest distance from a point (x, y) at a specified angle theta
        to the closest wall in the geofence, returns the distance and the normal angle.
    
        :param x: The x-coordinate of the point.
        :param y: The y-coordinate of the point.
        :param theta: The angle in radians at which the ray is cast.
        :return: The shortest positive distance to the closest wall and the angle to the normal,
            or None if no valid distance is found.
        """
        min_distance = float('inf')
        index = 0

        # Traverse through each wall (x1, x2) -> (x2, y2)
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]

            # Compute denominator to avoid division by zero
            denominator = (y2 - y1) * math.sin(theta) - (x2 - x1) * math.cos(theta)

            if abs(denominator) < 1e-9:
                # Ray is parallel to the wall, skip
                continue

            # Compute the distance m using the formula
            numerator = (y2 - y1) * (x1 - x) - (x2 - x1) * (y1 - y)
            m = numerator / denominator

            # Consider only positive distances (in front of the ray)
            if 0 < m < min_distance:
                min_distance = m
                index = i

        # Return the minimum positive distance, or None if no valid distance was found
        if min_distance < float('inf'):
            return min_distance, self.normal_angle_to_wall(theta, self.points[index], self.points[index + 1])
        else:
            return 0, 0

    @staticmethod
    def normal_angle_to_wall(theta: float, vertex1: tuple[float, float], vertex2: tuple[float, float]) -> float:
        """
        Calculates the angle between the angle of incidence (theta) and the wall's normal vector.
        
        :param theta: Angle of incidence in radians.
        :param vertex1: Tuple (x1, y1) representing the first vertex of the wall.
        :param vertex2: Tuple (x2, y2) representing the second vertex of the wall.
        :return: Angle between the angle of incidence and the wall's normal vector in radians.
        """
        x1, y1 = vertex1
        x2, y2 = vertex2

        if x1 == x2 and y1 == y2:
            raise ValueError("[Geofence]: Calculating normal angle for two points that are the same.")

        # Calculate the components of the formula
        denominator = math.sqrt((y1 - y2) ** 2 + (x2 - x1) ** 2)
        numerator = math.cos(theta) * (y1 - y2) + math.sin(theta) * (x2 - x1)

        # Calculate the angle using arccos
        return math.acos(numerator / denominator)

    def get_random_position(self) -> tuple[float, float]:
        """
        Generate a random point within the geofence.
    
        :return: A tuple (x, y) representing a random point inside the geofence.
        """
        while True:
            x = random.uniform(self.min_x, self.max_x)
            y = random.uniform(self.min_y, self.max_y)
            if self.inside_geofence(x, y):
                return x, y

    def get_random_positions(self, n: int) -> list[tuple[float, float]]:
        """
        Generate n random points within the geofence.
    
        :param n: The number of random points to generate.
        :return: A list of tuples (x, y) representing random points inside the geofence.
        """
        return [self.get_random_position() for _ in range(n)]
