"""
Utility functions for the anomaly detector to initialise the algorithm.
"""

import argparse

import numpy as np

import common_function


def initialise():
    """Initialises the algorithm's parameters.

    Parses the script's arguments. Based on that, it returns the initial parameters of the alogrithm.

    Returns:
        A tuple, with the following elements.
        - 1.: List of the paths (as strings) of the training files.
        - 2.: List of the paths (as strings) of the testing files.
        - 3.: List of the squares (as ints) to analyze.
        - 4.: List of the features to combine. The valid values are the constant.FEATURE_* global constants.
    """

    parser = argparse.ArgumentParser(description='The algorithm for the anomaly detector application.')
    parser.add_argument('--training', help='Path to the root directory of the training dataset.', required=True)
    parser.add_argument('--testing', help='Path to the root directory of the testing dataset.', required=True)
    parser.add_argument('-s', '--squares', type=int, help='The number of squares to analyze, from 1 to the given value.', required=True)
    feature_choices = ['sms-in', 'sms-out', 'call-in', 'call-out', 'internet']
    parser.add_argument('-f', '--features', help='Which features to use to generate the polinomials. Also, comma separated values are valid, which means it will combine the given features. By default, it combines all the features.', choices=feature_choices, nargs='+', required=False, default=feature_choices)

    args = vars(parser.parse_args())

    training_files_root = args['training']
    training_files = common_function.collect_files_in_dir(training_files_root)

    testing_files_root = args['testing']
    testing_files = common_function.collect_files_in_dir(testing_files_root)

    number_of_squares = args['squares']
    squares = list(range(1, number_of_squares + 1))  # FIXME this is here just for optimization purpose

    features = args['features']

    return training_files, testing_files, squares, features
