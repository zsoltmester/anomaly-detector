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

def create_interpolation_polynomial(x, y):
    """Create the interpolation polynomial based on the given x and y values.

    It is using spline interpolation.

    Args:
        x: The x values as a list of ints.
        y: The y values as a list of ints.
        len(x) == len(y)

    Returns:
        The x and y values in a dictionraly that represent the interpolation polynomial. It looks like this:
        { constant.X: x, constant.Y: y}
    """
    interpolation_polynomial = interpolate.splrep(x, y, k=_SPLINE_TYPE)
    x = np.linspace(np.amin(x), np.amax(x), len(x) * _SPLINE_X_SAMPLES_MULTIPLIER)
    y = interpolate.splev(x, interpolation_polynomial)
    return { constant.X: x, constant.Y: y}
