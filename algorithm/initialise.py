"""
Utility functions for the anomaly detector to initialise the algorithm.
"""

import argparse
import os

def _collect_files_in_dir(dir):
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

def initialise():
    """Initialises the algorithm's parameters.

    Parses the script's arguments. Based on that, it returns the initial parameters of the alogrithm.

    Returns:
        A tuple, with the following elements.
        - 1.: List of the paths (as strings) of the training files.
        - 2.: List of the paths (as strings) of the testing files.
        - 3.: List of the squares (as ints) to analyze.
    """

    parser = argparse.ArgumentParser(description='The algorithm for the anomaly detector application.')
    parser.add_argument('--training', help='Path to the root directory of the training dataset.', required=True)
    parser.add_argument('--testing', help='Path to the root directory of the testing dataset.', required=True)
    parser.add_argument('-s','--squares', type=int, help='The number of squares to analyze, from 1 to the given value.', required=True)

    args = vars(parser.parse_args())

    training_files_root = args['training']
    training_files = _collect_files_in_dir(training_files_root)

    testing_files_root = args['testing']
    testing_files = _collect_files_in_dir(testing_files_root)

    number_of_squares = args['squares']
    squares = list(range(1, number_of_squares + 1))

    return training_files, testing_files, squares
