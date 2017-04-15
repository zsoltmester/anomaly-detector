"""
Functions for the interpolation.
"""

import numpy as np
from scipy import interpolate

import constant

"""
The type of the spline interpolation.
"""
_SPLINE_TYPE = 3

"""
Controls how many samples points should it return from the polinomial. It multiplies the len(x).
"""
_SPLINE_X_SAMPLES_MULTIPLIER = 20


def create_interpolation_polynomial(x_points, y_points):
    """Create the interpolation polynomial based on the given x and y points.

    It is using spline interpolation.

    Args:
        x_points: The x points as a list of ints.
        y_points: The y points as a list of ints.
        len(x_points) == len(y_points)

    Returns:
        The x and y points in a dictionary that represent the interpolation polynomial. It looks like this:
        { constant.X: x, constant.Y: y}
    """
    interpolation_polynomial = interpolate.splrep(x_points, y_points, k=_SPLINE_TYPE)
    x_points = np.linspace(np.amin(x_points), np.amax(x_points), len(x_points) * _SPLINE_X_SAMPLES_MULTIPLIER)
    y_points = interpolate.splev(x_points, interpolation_polynomial)
    return {constant.X: x_points, constant.Y: y_points}


def create_interpolation_polinomials(dataset):
    """It runs the create_interpolation_polynomial function for each data in the given array.

    For more information, please check the create_interpolation_polynomial function's documentation.

    Args:
        data: An array of dictionaries with the following form: { constant.TIMESTAMPS: [ ... ], constant.FEATURES: [ ... ] }.

    Returns:
        An array of interpolated polinomials.
    """
    interpolation_polynomials = np.array([])
    for data in dataset:
        interpolation_polynomial = create_interpolation_polynomial(data[constant.TIMESTAMPS], data[constant.FEATURES])
        interpolation_polynomials = np.append(interpolation_polynomials, interpolation_polynomial)
    return interpolation_polynomials
