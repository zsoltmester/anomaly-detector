"""
Utility functions for the anomaly detector to initialise the algorithm.
"""

import argparse

import numpy as np

import constant
import common_function


def initialise():
    """Initialises the algorithm's parameters.

    Parses the script's arguments. Based on that, it returns the initial parameters of the alogrithm.

    Returns:
        A tuple, with the following elements.
        - 1.: What action to perform. It can be constant.ACTION_VISUALIZE or constant.ACTION_SAVE.
        - 2.: List of the paths (as strings) of the training files.
        - 3.: List of the paths (as strings) of the testing files.
        - 4.: List of squares (as ints) to analyze.
        - 5.: List of the features to combine. The valid values are the constant.FEATURE_* global constants.
    """

    parser = argparse.ArgumentParser(description='The algorithm for the anomaly detector application.')
    action_choices = [constant.ACTION_VISUALIZE, constant.ACTION_SAVE]
    parser.add_argument('-a', '--action', help='Which action to perform. The vizualization will display the polinoms. The save will insert the results to a database.', choices=action_choices, required=True)
    parser.add_argument('--training', help='Path to the root directory of the training dataset.', required=True)
    parser.add_argument('--testing', help='Path to the root directory of the testing dataset.', required=True)
    parser.add_argument('-s', '--square', help='The square to analyze, for visualization. It can be a value from 1 to 10000. If you run with the save action, it will saves all the squares and this parameter has no effect.', required=False)
    feature_choices = [constant.FEATURE_SMS_IN, constant.FEATURE_SMS_OUT, constant.FEATURE_CALL_IN, constant.FEATURE_CALL_OUT, constant.FEATURE_INTERNET]
    parser.add_argument('-f', '--features', help='Which features to use to generate the polinomials. Also, comma separated values are valid, which means it will combine the given features. By default, it combines all the features.', choices=feature_choices, nargs='+', required=False, default=feature_choices)

    args = vars(parser.parse_args())

    action = args['action']
    features = args['features']

    square = args['square']
    if action == constant.ACTION_VISUALIZE:
        if square.isdigit():
            square = int(square)
            if not (1 <= square <= 10000):
                print('Invalid arguments! The square must be a number between 1 to 10000 for visualization.')
                exit(1)
            squares = [square]
        else:
            print('Invalid arguments! The square must be a number between 1 to 10000 for visualization.')
            exit(1)
    else:
        if square:
            print('Square parameter has no effect in save mode.')
        squares = list(range(1, 10001))

    training_files_root = args['training']
    training_files = common_function.collect_files_in_dir(training_files_root)

    testing_files_root = args['testing']
    testing_files = common_function.collect_files_in_dir(testing_files_root)

    return action, training_files, testing_files, squares, features
