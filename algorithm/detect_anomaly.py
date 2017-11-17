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


def get_standard_deviations_for_day(training_standard_deviations, timestamps):
    """Return the standard deviations of the training data for each timestamp.

    Args:
        training_standard_deviations: The training day's standard deviations, as a list of floats.
        timestamps: The timestamps for a day.

    Returns:
        A dictinary, where the keys are the timestamps (as ints) and the values are the standard deviations (as floats).
    """
    standard_deviations = {}
    for timestamp_index, timestamp in enumerate(timestamps):
        standard_deviations[int(timestamp)] = training_standard_deviations[timestamp_index]
    return standard_deviations


def drop_unknown_values(testing_timestamps, training_timestamps, training_features, training_standard_deviations):
    """Drops the those training features and standard deviations, whose timestamps are not in the the testing timestamps.

    Args:
        testing_timestamps: The testing day's timestamps, as a list of ints.
        training_timestamps: The training day's timestamps, as a list of ints.
        training_features: The training day's features, as a list of floats.
        training_standard_deviations: The training day's standard deviations, as a list of floats.

    Returns:
        1. The filtered training features as a new array of floats.
        2. The filtered standard deviations as a new array of floats.
    """
    filtered_training_features = []
    filtered_training_standard_deviations = []
    for testing_timestamp in testing_timestamps:
        testing_timestamp_index_in_training_timestamps = np.where(training_timestamps == testing_timestamp)[0]
        filtered_training_features.append(training_features[testing_timestamp_index_in_training_timestamps][0])
        filtered_training_standard_deviations.append(training_standard_deviations[testing_timestamp_index_in_training_timestamps][0])
    return filtered_training_features, filtered_training_standard_deviations


if __name__ == '__main__':
    algorithm_start_time = time()

    print('Initialize the algorithm...')
    start_time = time()
    action, training_files, testing_files, squares, features = initialise.initialise()
    if action == constant.ACTION_SAVE:
        preprocess.cache_data(training_files, squares, is_training=True)
        preprocess.cache_data(testing_files, squares, is_training=False)
    else:
        preprocess.cache_data(training_files, squares, is_training=True)
        preprocess.cache_data(testing_files, squares, is_training=False)
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

        # create the training_features_mean for each timestamp
        training_features_mean = {constant.WEEKDAYS: None, constant.WEEKENDS: None}
        for category in [constant.WEEKDAYS, constant.WEEKENDS]:
            training_features_mean[category] = preprocess.features_mean_for_each_timestamps(training_data[category])

        # create the training_features_standard_deviation for each timestamp
        training_features_standard_deviation = {constant.WEEKDAYS: None, constant.WEEKENDS: None}
        for category in [constant.WEEKDAYS, constant.WEEKENDS]:
            training_features_standard_deviation[category] = preprocess.features_standard_deviation_for_each_timestamps(training_data[category])

        # group the testing data by day
        testing_data_grouped_by_day = {constant.WEEKDAYS: None, constant.WEEKENDS: None}
        for category in [constant.WEEKDAYS, constant.WEEKENDS]:
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
                    filtered_training_features, filtered_training_standard_deviations = drop_unknown_values(testing_data_grouped_by_day[category][index][constant.TIMESTAMPS], training_timestamps[category], training_features_mean[category], training_features_standard_deviation[category])

                    standard_deviations = get_standard_deviations_for_day(filtered_training_standard_deviations, testing_data_grouped_by_day[category][index][constant.TIMESTAMPS])
                    print('Standard deviations in day', testing_data_grouped_by_day[category][index], ':', standard_deviations)

                    display.display_polinomials(training_data[category], filtered_training_features, np.add(filtered_training_features, training_features_standard_deviation[category]), np.subtract(filtered_training_features, training_features_standard_deviation[category]), training_interpolation_polynomial[category], testing_data_grouped_by_day[category][index], interpolation_polynomial)
        else:

            print('Collect the results for each timestamp in each testing day...')

            start_time = time()

            mean_activities = {}
            actual_activities = {}
            standard_deviations = {}

            for category in [constant.WEEKDAYS, constant.WEEKENDS]:
                for testing_day_data in testing_data_grouped_by_day[category]:

                    filtered_training_features, filtered_training_standard_deviations = drop_unknown_values(testing_day_data[constant.TIMESTAMPS], training_timestamps[category], training_features_mean[category], training_features_standard_deviation[category])

                    current_mean_activities = {}
                    current_actual_activities = {}
                    current_standard_deviations = {}
                    for timestamp_index, timestamp in enumerate(testing_day_data[constant.TIMESTAMPS]):
                        current_mean_activities[int(timestamp)] = filtered_training_features[timestamp_index]
                        current_actual_activities[int(timestamp)] = testing_day_data[constant.FEATURES][timestamp_index]
                        current_standard_deviations[int(timestamp)] = filtered_training_standard_deviations[timestamp_index]

                    mean_activities[testing_day_data[constant.DAY]] = current_mean_activities
                    actual_activities[testing_day_data[constant.DAY]] = current_actual_activities
                    standard_deviations[testing_day_data[constant.DAY]] = current_standard_deviations

            print('Done to collect the results. Time: ', round(time() - start_time, 3), ' sec')

            print('Save the results to the database...')
            start_time = time()
            save.write_square_to_database(square, mean_activities, actual_activities, standard_deviations)
            # save.read_database()  # for testing purpose
            print('Done to save the results to the database. Time: ', round(time() - start_time, 3), ' sec')

    print('The algorithm finished. Time: ', round(time() - algorithm_start_time, 3), ' sec')
