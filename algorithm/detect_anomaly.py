"""
The main script for the algorithm.
"""

import math
from time import time

import numpy as np

import constant
import initialise
import interpolate
import preprocess
import save


def get_difference_for_day(testing_day_data, training_day_data, unique_timestamps):
    """Return the difference between the given testing and training day for each timestamp.

    Args:
        testing_day_data: The testing day's features, as a list of floats.
        training_day_data: The training day's features, as a list of floats.
        unique_timestamps: The unique timestamps for a day.

    Returns:
        A dictinary, where the keys are the timestamps (as ints) and the values are the differences (as floats).
    """
    differences = {}
    for timestamp_index, timestamp in enumerate(unique_timestamps):
        difference = testing_day_data[timestamp_index] - training_day_data[timestamp_index]
        difference = math.fabs(difference)
        differences[int(timestamp)] = difference
    return differences


if __name__ == '__main__':
    algorithm_start_time = time()

    print('Initialize the algorithm...')
    start_time = time()
    action, training_files, testing_files, squares, features = initialise.initialise()
    if action == constant.ACTION_SAVE:
        preprocess.cache_data(training_files, None, is_training=True)
        preprocess.cache_data(testing_files, None, is_training=False)
    else:
        preprocess.cache_data(training_files, squares[0], is_training=True)
        preprocess.cache_data(testing_files, squares[0], is_training=False)
    print('Done to initialze the algorithm. Time: ', round(time() - start_time, 3), ' sec')

    for square in squares:
        if square > 3333:  # FIXME for optimization purpose
            continue

        print('*** SQUARE ' + str(square) + ' ***')

        print('Preprocess the datasets...')
        start_time = time()
        # preprocess the training and testing datasets
        training_data = preprocess.preprocess_dataset(square, features, is_training=True)
        testing_data = preprocess.preprocess_dataset(square, features, is_training=False)
        preprocess.reset_scaler()

        # sorted and unique timestamps for a day, in minutes
        unique_timestamps = np.unique(training_data[constant.WEEKDAYS][constant.TIMESTAMPS])

        # create the training_features_mean for each timestamp and group the testing data by day
        training_features_mean = {constant.WEEKDAYS: None, constant.WEEKENDS: None}
        testing_data_grouped_by_day = {constant.WEEKDAYS: None, constant.WEEKENDS: None}
        for category in [constant.WEEKDAYS, constant.WEEKENDS]:
            training_features_mean[category] = preprocess.features_mean_for_each_timestamps(training_data[category])
            testing_data_grouped_by_day[category] = preprocess.group_data_by_day(testing_data[category])
        print('Done to preprocess the datasets. Time: ', round(time() - start_time, 3), ' sec')

        if action == constant.ACTION_VISUALIZE:
            import display

            print('Generate the polinomials...')
            start_time = time()
            training_interpolation_polynomial = {constant.WEEKDAYS: None, constant.WEEKENDS: None}
            testing_interpolation_polynomials = {constant.WEEKDAYS: None, constant.WEEKENDS: None}
            for category in [constant.WEEKDAYS, constant.WEEKENDS]:
                # create training interpolation polinomials
                training_interpolation_polynomial[category] = interpolate.create_interpolation_polynomial(unique_timestamps, training_features_mean[category])
                # create testing interpolation polinomials
                testing_interpolation_polynomials[category] = interpolate.create_interpolation_polinomials(testing_data_grouped_by_day[category])
            print('Done to generate the polinomials. Time: ', round(time() - start_time, 3), ' sec')

            print('Display the polinomials...')
            for category in [constant.WEEKDAYS, constant.WEEKENDS]:
                for index, interpolation_polynomial in enumerate(testing_interpolation_polynomials[category]):
                    differences = get_difference_for_day(testing_data_grouped_by_day[category][index][constant.FEATURES], training_features_mean[category], unique_timestamps)
                    day = testing_data_grouped_by_day[category][index][constant.DAY]
                    print('Differences for day ', day, ':', differences)

                    display.display_polinomials(training_data[category], unique_timestamps, training_features_mean[category], training_interpolation_polynomial[category], testing_data_grouped_by_day[category][index], interpolation_polynomial)
        else:
            print('Calulate the difference for each timestamp in each testing day...')
            start_time = time()
            differences = {}
            for category in [constant.WEEKDAYS, constant.WEEKENDS]:
                for testing_day_data in testing_data_grouped_by_day[category]:
                    differences_for_current_day = get_difference_for_day(testing_day_data[constant.FEATURES], training_features_mean[category], unique_timestamps)
                    differences[testing_day_data[constant.DAY]] = differences_for_current_day
            print('Done to calculate the differences. Time: ', round(time() - start_time, 3), ' sec')

            print('Save the differences to the database...')
            start_time = time()
            save.write_differences_to_sqlite(square, differences)
            # save.read_differences_from_sqlite()  # for testing purpose
            print('Done to save the differences to the database. Time: ', round(time() - start_time, 3), ' sec')

    print('The algorithm finished. Time: ', round(time() - algorithm_start_time, 3), ' sec')
