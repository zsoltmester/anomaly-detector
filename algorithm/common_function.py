"""
Common utility functions.
"""

from datetime import datetime
import os

import numpy as np

import constant


def collect_files_in_dir(directory):
    """Collects the files in the given directory.

    Args:
        directory: Directory.

    Returns:
        The list of the collected files' paths.
    """
    files = []
    for (dir_path, _, file_names) in os.walk(directory):
        files.extend([os.path.join(dir_path, file_name) for file_name in file_names])
    return files


def get_minute(timestamp):
    """Calculates how many minutes passed on that day.

    Args:
        timestamp: The timestamp as a string.

    Returns:
        The number of minutes that passed on that day.
    """
    date = date_from_timestamp(timestamp)
    minutes_passed = constant.MINUTES_PER_HOUR * date.hour + date.minute
    return minutes_passed


def get_minutes(timestamps):
    """Calculates how many minutes passed on that days.

    Args:
        timestamps: Array of strings.

    Returns:
        The number of minutes that passed on that days.
    """
    minutes = np.array([])
    for timestamp in timestamps:
        minutes_passed = get_minute(timestamp)
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


def date_from_timestamp(timestamp):
    """Converts the given timestamp to a date object.

    Args:
        timestamp: The timestamp as a string.

    Return:
        The date object
    """
    date = datetime.fromtimestamp(float(timestamp) / 1000.0)
    return date
