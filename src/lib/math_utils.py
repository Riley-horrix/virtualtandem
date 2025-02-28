import numpy as np

def distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

def unit_vector(vector):
    """ Returns the unit vector of the vector."""
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """
    Returns the angle in radians between vectors v1 and v2.
    :param v1: First vector.
    :param v2: Second vector.
    :return: The angle in radians.
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def signed_angle_between(v1, v2) -> float:
    """
    Returns the signed angle in radians from vector v1 to v2.

    :param v1: First vector.
    :param v2: Second vector.
    :return: The signed angle in radians.
    """
    return angle_between(v1, v2) * (-1 if np.cross(v1, v2) > 0 else 1)