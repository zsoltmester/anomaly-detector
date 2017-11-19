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

if __name__ == '__main__':

    algorithm_start_time = time()

    print('Initialize the algorithm...')
    start_time = time()

    action, training_files, testing_files, squares, features = initialise.initialise()

    squares_training_data = preprocess.load_squares(training_files, squares)
    squares_testing_data = preprocess.load_squares(testing_files, squares)

    print('Done to initialze the algorithm. Time: ', round(time() - start_time, 3), ' sec')

    for square in squares:

        print('*** SQUARE ' + str(square) + ' ***')

        if (square not in squares_training_data) or (square not in squares_testing_data):
            print('No data for square (' + str(square) + '), skip.')
            continue

        print('Preprocess the datasets...')
        start_time = time()

        training_data = preprocess.preprocess_square(squares_training_data[square], features, True)
        testing_data = preprocess.preprocess_square(squares_testing_data[square], features, False)
        preprocess.reset_scaler()

        # sorted and unique training timestamps for a day, in minutes
        training_timestamps = {constant.WEEKDAYS: None, constant.WEEKENDS: None}
        for category in [constant.WEEKDAYS, constant.WEEKENDS]:
            training_timestamps[category] = np.unique(training_data[category][constant.TIMESTAMPS])

        # create the training features' mean for each timestamp
        training_features_mean = {constant.WEEKDAYS: None, constant.WEEKENDS: None}
        for category in [constant.WEEKDAYS, constant.WEEKENDS]:
            training_features_mean[category] = preprocess.features_mean_for_each_timestamps(training_data[category])

        # create the training features' standard deviation for each timestamp
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

                for interpolation_polynomial_index, interpolation_polynomial in enumerate(testing_interpolation_polynomials[category]):

                    filtered_training_features = [
                        training_features_mean[category][timestamp_index]
                        for timestamp_index, timestamp in enumerate(testing_data_grouped_by_day[category][interpolation_polynomial_index][constant.TIMESTAMPS].astype(int))
                    ]

                    filtered_training_standard_deviations = [
                        training_features_standard_deviation[category][timestamp_index]
                        for timestamp_index, timestamp in enumerate(testing_data_grouped_by_day[category][interpolation_polynomial_index][constant.TIMESTAMPS].astype(int))
                    ]

                    training_features_standard_deviation_upper_bound = np.add(filtered_training_features, training_features_standard_deviation[category])
                    training_features_standard_deviation_lower_bound = np.subtract(filtered_training_features, training_features_standard_deviation[category])

                    display.display_polinomials(training_data[category], filtered_training_features, training_features_standard_deviation_upper_bound, training_features_standard_deviation_lower_bound, training_interpolation_polynomial[category], testing_data_grouped_by_day[category][interpolation_polynomial_index], interpolation_polynomial)

        else:

            print('Collect the results for each timestamp in each testing day...')

            start_time = time()

            mean_activities = {}
            actual_activities = {}
            standard_deviations = {}

            for category in [constant.WEEKDAYS, constant.WEEKENDS]:

                for testing_day_data in testing_data_grouped_by_day[category]:

                    filtered_training_features = [
                        training_features_mean[category][timestamp_index]
                        for timestamp_index, timestamp in enumerate(testing_day_data[constant.TIMESTAMPS].astype(int))
                    ]

                    filtered_training_standard_deviations = [
                        training_features_standard_deviation[category][timestamp_index]
                        for timestamp_index, timestamp in enumerate(testing_day_data[constant.TIMESTAMPS].astype(int))
                    ]

                    mean_activities[testing_day_data[constant.DAY]] = dict(zip(testing_day_data[constant.TIMESTAMPS], filtered_training_features))
                    actual_activities[testing_day_data[constant.DAY]] = dict(zip(testing_day_data[constant.TIMESTAMPS], testing_day_data[constant.FEATURES]))
                    standard_deviations[testing_day_data[constant.DAY]] = dict(zip(testing_day_data[constant.TIMESTAMPS], filtered_training_standard_deviations))

            print('Done to collect the results. Time: ', round(time() - start_time, 3), ' sec')

            print('Save the results to the database...')
            start_time = time()

            save.write_square_to_database(square, mean_activities, actual_activities, standard_deviations)
            save.read_database()  # for testing purpose

            print('Done to save the results to the database. Time: ', round(time() - start_time, 3), ' sec')

    print('The algorithm finished. Time: ', round(time() - algorithm_start_time, 3), ' sec')
