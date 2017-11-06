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


def get_difference_for_day(testing_day_data, training_day_data, timestamps):
    """Return the difference between the given testing and training day for each timestamp.

    Args:
        testing_day_data: The testing day's features, as a list of floats.
        training_day_data: The training day's features, as a list of floats.
        timestamps: The timestamps for a day.

    Returns:
        A dictinary, where the keys are the timestamps (as ints) and the values are the differences (as floats).
    """
    differences = {}
    for timestamp_index, timestamp in enumerate(timestamps):
        difference = testing_day_data[timestamp_index] - training_day_data[timestamp_index]
        difference = math.fabs(difference)
        differences[int(timestamp)] = difference
    return differences


def drop_unknown_values(testing_timestamps, training_timestamps, training_features):
    """Drops the those training features, whose timestamps are not in the the testing timestamps.

    Args:
        testing_timestamps: The testing day's timestamps, as a list of ints.
        training_timestamps: The training day's timestamps, as a list of ints.
        training_features: The training day's features, as a list of floats.

    Returns:
        The filtered training features as a new array of floats.
    """
    filtered_training_features = []
    for testing_timestamp in testing_timestamps:
        testing_timestamp_index_in_training_timestamps = np.where(training_timestamps == testing_timestamp)[0]
        filtered_training_features.append(training_features[testing_timestamp_index_in_training_timestamps][0])
    return filtered_training_features


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
        print('*** SQUARE ' + str(square) + ' ***')

        print('Preprocess the datasets...')
        start_time = time()
        try:
            # preprocess the training and testing datasets
            training_data = preprocess.preprocess_dataset(square, features, is_training=True)
            testing_data = preprocess.preprocess_dataset(square, features, is_training=False)
        except Exception:
            print('No data for square (' + str(square) + '), skip.')
            continue
        preprocess.reset_scaler()

        # sorted and unique training timestamps for a day, in minutes
        training_timestamps = {constant.WEEKDAYS: None, constant.WEEKENDS: None}
        for category in [constant.WEEKDAYS, constant.WEEKENDS]:
            training_timestamps[category] = np.unique(training_data[category][constant.TIMESTAMPS])

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
                training_interpolation_polynomial[category] = interpolate.create_interpolation_polynomial(training_timestamps[category], training_features_mean[category])
                # create testing interpolation polinomials
                testing_interpolation_polynomials[category] = interpolate.create_interpolation_polinomials(testing_data_grouped_by_day[category])
            print('Done to generate the polinomials. Time: ', round(time() - start_time, 3), ' sec')

            print('Display the polinomials...')
            for category in [constant.WEEKDAYS, constant.WEEKENDS]:
                for index, interpolation_polynomial in enumerate(testing_interpolation_polynomials[category]):
                    filtered_training_features = drop_unknown_values(testing_data_grouped_by_day[category][index][constant.TIMESTAMPS], training_timestamps[category], training_features_mean[category])

                    differences = get_difference_for_day(testing_data_grouped_by_day[category][index][constant.FEATURES], filtered_training_features, testing_data_grouped_by_day[category][index][constant.TIMESTAMPS])
                    print('Differences in day', testing_data_grouped_by_day[category][index], ':', differences)

                    display.display_polinomials(training_data[category], filtered_training_features, training_interpolation_polynomial[category], testing_data_grouped_by_day[category][index], interpolation_polynomial)
        else:
            print('Calulate the difference for each timestamp in each testing day...')
            start_time = time()
            differences = {}
            for category in [constant.WEEKDAYS, constant.WEEKENDS]:
                for testing_day_data in testing_data_grouped_by_day[category]:
                    filtered_training_features = drop_unknown_values(testing_day_data[constant.TIMESTAMPS], training_timestamps[category], training_features_mean[category])
                    differences_for_current_day = get_difference_for_day(testing_day_data[constant.FEATURES], filtered_training_features, testing_day_data[constant.TIMESTAMPS])
                    differences[testing_day_data[constant.DAY]] = differences_for_current_day
            print('Done to calculate the differences. Time: ', round(time() - start_time, 3), ' sec')

            print('Save the differences to the database...')
            start_time = time()
            save.write_differences_to_sqlite(square, differences)
            # save.read_differences_from_sqlite()  # for testing purpose
            print('Done to save the differences to the database. Time: ', round(time() - start_time, 3), ' sec')

    print('The algorithm finished. Time: ', round(time() - algorithm_start_time, 3), ' sec')
