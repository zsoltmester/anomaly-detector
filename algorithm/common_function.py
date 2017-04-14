"""
Common utility functions.
"""

from datetime import datetime
import os

import numpy as np

import constant

def collect_files_in_dir(dir):
    """Collects the files in the given directory.

    Args:
        dir: Directory.

    Returns:
        The list of the collected files' paths.
    """

    files = []
    for (dir_path, dir_names, file_names) in os.walk(dir):
        files.extend([os.path.join(dir_path, file_name) for file_name in file_names])
    return files

def get_minutes(timestamps):
    """Calculates how many minutes passed on that day.

    Args:
        timestamps: The timestamp (milliseconds).

    Returns:
        The number of minutes that passed on that day.
    """
    minutes = np.array([])
    for timestamp in timestamps:
        date = datetime.fromtimestamp(float(timestamp) / 1000.0)
        minutes_passed = constant.MINUTES_PER_HOUR * date.hour + date.minute
        minutes = np.append(minutes, minutes_passed)
    return minutes

def sort_arrays_based_on_the_first(first_array, second_array):
    """Sort the first array then the second in the same order as the first.

    Args:
        first_array: The first array to sort.
        second_arrays: The second array to sort.

    Returns:
        A tuple with the sorted first and second array.
    """
    order = np.argsort(first_array)
    first_array = np.array(first_array)[order]
    second_array = np.array(second_array)[order]
    return first_array, second_array


def add_row_to_matrix(matrix, new_row):
    """Add the new_row to the matrix.

    Args:
        matrix: The matrix to extend.
        new_row: The new row to add the end of the matrix.

    Returns:
        The extended matrix.
    """
    if matrix is None:
        matrix = np.array(new_row)
    else:
        matrix = np.vstack([matrix, new_row])
    return matrix
