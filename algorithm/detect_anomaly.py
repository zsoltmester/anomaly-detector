"""
The main script for the algorithm.
"""

from time import time

import numpy as np

import constant
import display
import initialise
import interpolate
import preprocess
import save

if __name__ == '__main__':
    algorithm_start_time = time()

    print('Initialize the algorithm...')
    start_time = time()
    action, training_files, testing_files, squares, features = initialise.initialise()
    print('Done to initialze the algorithm. Time: ', round(time() - start_time, 3), ' sec')

    for square in squares:
        if int(square) > 2000:
            continue
        print('*** SQUARE ' + str(square) + ' ***')
        print('Preprocess the datasets...')
        start_time = time()
        # preprocess the training and testing datasets
        training_data = preprocess.preprocess_dataset(training_files, square, features, is_training=True)
        testing_data = preprocess.preprocess_dataset(testing_files, square, features)

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
                    display.display_polinomials(training_data[category], unique_timestamps, training_features_mean[category], training_interpolation_polynomial[category], testing_data_grouped_by_day[category][index], interpolation_polynomial)
        else:
            print('Calulate the difference for each timestamp in each testing day...')
            start_time = time()
            differences = {}
            for category in [constant.WEEKDAYS, constant.WEEKENDS]:
                for testing_day_data in testing_data_grouped_by_day[category]:
                    differences[testing_day_data[constant.DAY]] = {}
                    for timestamp_index, timestamp in enumerate(unique_timestamps):
                        difference = testing_day_data[constant.FEATURES][timestamp_index] - training_features_mean[category][timestamp_index]
                        differences[testing_day_data[constant.DAY]][int(timestamp)] = difference
            print('Done to calculate the differences. Time: ', round(time() - start_time, 3), ' sec')

            print('Save the differences to the database...')
            start_time = time()
            save.write_differences_to_sqlite(square, differences);
            # save.read_differences_from_sqlite(); # for testing purpose
            print('Done to save the differences to the database. Time: ', round(time() - start_time, 3), ' sec')

    print('The algorithm finished. Time: ', round(time() - algorithm_start_time, 3), ' sec')
