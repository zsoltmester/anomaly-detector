"""
Utility functions for the anomaly detector to preprocess the dataset.
"""

import csv
from datetime import datetime
from time import time

import numpy as np
from sklearn import preprocessing

import common_function
import constant

"""
The scaler for the feature scaling.
"""
_SCALER = None

"""
A constant that controls how many outliers we will drop.
"""
_OUTLIER_CONTROL = 1.75


def load_squares(files, squares):
    """Returns the given squares from the given files.

    Args:
        files: Paths to the files. It must be an iterable on strings.
        squares: The squares to load. It must be a list of integers.

    Returns:
        A dictionary, where the keys are the squares (as ints) and the values are the features with values, as dictionaries.
    """
    print('Loading the squares...')
    start_time = time()

    data = {}

    for file in files:

        if 'sms-call-internet-mi-2014-01-01.txt' in file:  # if this inconsitency exists on the dataset, skip this file
            continue

        with open(file) as tsv_file:

            print('Reading', file, '...')

            squares_found = 0
            last_found_square = None

            for line in tsv_file:

                values = line.split('\t')

                current_square = int(values[0])
                if current_square in squares:
                    if current_square != last_found_square:
                        squares_found += 1
                        last_found_square = current_square
                elif squares_found == len(squares):
                    break
                else:
                    continue

                data_point = {
                    constant.FEATURE_TIME_INTERVAL: values[1],
                    constant.FEATURE_SMS_IN: values[3],
                    constant.FEATURE_SMS_OUT: values[4],
                    constant.FEATURE_CALL_IN: values[5],
                    constant.FEATURE_CALL_OUT: values[6],
                    constant.FEATURE_INTERNET: values[7]
                }

                if current_square not in data:
                    data[current_square] = []
                data[current_square].append(data_point)

    print('Done to loading the squares. Time: ', round(time() - start_time, 3), ' sec')
    return data


def preprocess_square(square_data, features, convert_timestamps):
    """Preprocess the given square using the given features.

    1. Group by time interval.
    2. Split to timestamps and features.
    3. Split to weekdays and weekends.
    4. Scale the features.
    5. Calculates features mean value.
    6. Removes the unknown data points.
    7. Convert timestamps to the passed minutes each day, if the given parameter is true.
    8. Sort the arrays based on the timestamps.

    Args:
        square_data: The square data to preprocess. A dictionary, where the values are the constant.FEATURE_* global constants.
        features: Which features to use. The valid values are the constant.FEATURE_* global constants.
        covert_timestamps: Should convert the timestamps to the passed minutes on day or not.

    Returns:
        The processed dataset as a dictionary, with the following schema:
        {
            constant.WEEKDAYS: { constant.TIMESTAMPS: [ ... ], constant.FEATURES: [ ... ] },
            constant.WEEKENDS: { constant.TIMESTAMPS: [ ... ], constant.FEATURES: [ ... ] }
        }
    """
    grouped_square_data = group_data_by_time_interval(square_data, features)
    timestamps, features = split_data_for_timestamps_and_features(grouped_square_data)
    categories = split_data_for_weekdays_and_weekends(timestamps, features)

    for category_id in [constant.WEEKDAYS, constant.WEEKENDS]:
        category = categories[category_id]

        category[constant.FEATURES] = scale_features(category[constant.FEATURES])
        category[constant.FEATURES] = translate_matrix_to_mean_vector(category[constant.FEATURES])

        category[constant.TIMESTAMPS], category[constant.FEATURES] = remove_invalid_values(category[constant.TIMESTAMPS], category[constant.FEATURES])

        if convert_timestamps:
            minutes_passed_on_day = np.array([])
            for timestamp in category[constant.TIMESTAMPS]:
                minutes_passed_on_day = np.append(minutes_passed_on_day, common_function.passed_minutes_on_day(timestamp))
            category[constant.TIMESTAMPS] = minutes_passed_on_day

        category[constant.TIMESTAMPS], category[constant.FEATURES] = common_function.sort_arrays_based_on_the_first(category[constant.TIMESTAMPS], category[constant.FEATURES])

    return categories


def group_data_by_time_interval(data, features):
    """Group the given data by the timestamps with the given features.

    It summarises the values for each feature for the same timestamp.

    Args:
        data: The data as a list of dictionaries, where the keys are the constant.FEATURE_* global constants.
        features: The ID of the features to keep.

    Returns:
        The grouped data as a dictinary, where the keys are the timestamps and the values are the properties for a timestamp as a dictinary. The latter's keys are the given features.
    """
    grouped_data = {}
    for row in data:
        time_interval = row[constant.FEATURE_TIME_INTERVAL]
        if time_interval in grouped_data:
            for prop in grouped_data[time_interval]:
                grouped_data[time_interval][prop] += get_value_from_row(row, prop)
        else:
            grouped_data[time_interval] = {}
            for prop in row:
                if prop in features:
                    grouped_data[time_interval][prop] = get_value_from_row(row, prop)
    return grouped_data


def get_value_from_row(row, value_id):
    """Returns the value for the given ID from the given row as a float.

    If the value is missing from the row, it returns 0.

    Args:
        row: The row as a dictionary of the features.
        value_id: The ID of the value to get as a string.

    Returns:
        The value for the given ID as a float.
    """
    try:
        return float(row[value_id])
    except ValueError:
        return 0.


def split_data_for_timestamps_and_features(data):
    """Split the data for timestamps and features.

    Args:
        data: The data as a dictinary, where the keys are the timestamps and the values are the features for a timestamp as a dictionary.

    Returns:
        A tuple, with the following items.
        - 1.: The timestamps as a numpy array of strings.
        - 2.: The features as a numpy array of numpy arrays (a matrix), where each column represents a feature.
    """
    timestamps = np.array([])
    features = None
    for timestamp, properties in data.items():
        timestamps = np.append(timestamps, timestamp)
        new_row = []
        for _, value in properties.items():
            new_row.append(value)
        features = common_function.add_row_to_matrix(features, new_row)
    return timestamps, features


def split_data_for_weekdays_and_weekends(timestamps, features):
    """Split the data for weekdays and weekends.

    Args:
        timestamps: The timestamps as a numpy array of strings.
        features: The features as a numpy array of numpy arrays (a matrix), where each column represents a feature.

    Returns:
        The splitted dataset as a dictionary, with the following schema:
        {
            constant.WEEKDAYS: { constant.TIMESTAMPS: [ ... ], constant.FEATURES: [ ... ] },
            constant.WEEKENDS: { constant.TIMESTAMPS: [ ... ], constant.FEATURES: [ ... ] }
        }
    """
    weekday_timestamps = np.array([])
    weekend_timestamps = np.array([])
    weekday_features = None
    weekend_features = None
    for timestamp_index, timestamp in enumerate(timestamps):
        date = datetime.fromtimestamp(float(timestamp) / 1000.)
        if date.weekday() < 5:
            weekday_timestamps = np.append(weekday_timestamps, timestamp)
            weekday_features = common_function.add_row_to_matrix(weekday_features, features[timestamp_index])
        else:
            weekend_timestamps = np.append(weekend_timestamps, timestamp)
            weekend_features = common_function.add_row_to_matrix(weekend_features, features[timestamp_index])
    return {
        constant.WEEKDAYS: {constant.TIMESTAMPS: weekday_timestamps, constant.FEATURES: weekday_features}, constant.WEEKENDS: {constant.TIMESTAMPS: weekend_timestamps, constant.FEATURES: weekend_features}
    }


def scale_features(features):
    """Scale the features with a min-max scaler. It is saving the firstly created scaler and use it as a transformer every time.

    Args:
        features: The features as a numpy array of numpy arrays (a matrix), where each column represents a feature.

    Returns:
        The scaled features.
    """
    global _SCALER
    if _SCALER is None:
        _SCALER = preprocessing.MinMaxScaler().fit(features)
    return _SCALER.transform(features)


def translate_matrix_to_mean_vector(matrix):
    """Translate each row in the matrix to their mean values.

    Args:
        features: The features as a numpy array of numpy arrays (a matrix), where each column represents a feature.

    Returns:
        The vector of the mean values.
    """
    mean_vector = np.array([])
    for row in matrix:
        valid_value = 0
        sum_value = 0.
        for value in row:
            if value:
                valid_value += 1
                sum_value += value
        mean_value = sum_value / valid_value if valid_value else 0
        mean_vector = np.append(mean_vector, mean_value)
    return mean_vector


def remove_invalid_values(timestamps, features):
    """Removes the invalid values from both the features and the timestamps.

    It searches for the features with 0 value, and remove them and their timestamps too.

    Args:
        timestamps: The timestamp as a list.
        features: The features as a list of numbers.

    Return:
        A tuple, with the filtered timestamps and features.
    """
    invalid_data_points = []
    for index, feature_value in enumerate(features):
        if feature_value == 0:
            invalid_data_points.append(index)
    timestamps = np.delete(timestamps, invalid_data_points)
    features = np.delete(features, invalid_data_points)
    return timestamps, features


def drop_outliers(vector):
    """Drops the outliers from the given vector.

    It calculates each value's difference from the mean. It will drop a value, if the difference is greater than the _OUTLIER_CONTROL * standard deviation of the vector.

    Args:
        vector: The vector, as a numpy array of numbers.

    Returns:
        The vector without the outliers.
    """
    difference_from_mean = abs(vector - np.mean(vector))
    standard_deviation = np.std(vector)
    allowed_difference = _OUTLIER_CONTROL * standard_deviation
    return vector[difference_from_mean <= allowed_difference]


def features_mean_for_each_timestamps(data):
    """Calculates the features' mean for each timestamp.

    Also drops the outliers with the drop_outliers_from_vector function.

    Args:
        data: A dictionary with the following form: { constant.TIMESTAMPS: [ ... ], constant.FEATURES: [ ... ] }.

    Returns:
        An array with the features' mean for each timestamp in order.
    """
    features_mean = np.array([])
    current_timestamp = data[constant.TIMESTAMPS][0]
    current_values = np.array([])
    for index in range(0, len(data[constant.TIMESTAMPS])):
        current_values = np.append(current_values, data[constant.FEATURES][index])
        if index == len(data[constant.TIMESTAMPS]) - 1 or current_timestamp < data[constant.TIMESTAMPS][index + 1]:
            # add the mean value
            current_values = drop_outliers(current_values)
            features_mean = np.append(features_mean, np.average(current_values))
            # prepare for the next iteration
            if index != len(data[constant.TIMESTAMPS]) - 1:
                current_timestamp = data[constant.TIMESTAMPS][index + 1]
                current_values = np.array([])
    return features_mean


def features_standard_deviation_for_each_timestamps(data):
    """Calculates the features' standard deviation for each timestamp.

    Args:
        data: A dictionary with the following form: { constant.TIMESTAMPS: [ ... ], constant.FEATURES: [ ... ] }.

    Returns:
        An array with the features' standard deviation for each timestamp in order.
    """
    features_standard_deviation = np.array([])
    current_timestamp = data[constant.TIMESTAMPS][0]
    current_values = np.array([])
    for index in range(0, len(data[constant.TIMESTAMPS])):
        current_values = np.append(current_values, data[constant.FEATURES][index])
        if index == len(data[constant.TIMESTAMPS]) - 1 or current_timestamp < data[constant.TIMESTAMPS][index + 1]:
            # add the standard deviation for this timestamp
            features_standard_deviation = np.append(features_standard_deviation, np.std(current_values))
            # prepare for the next iteration
            if index != len(data[constant.TIMESTAMPS]) - 1:
                current_timestamp = data[constant.TIMESTAMPS][index + 1]
                current_values = np.array([])
    return features_standard_deviation


def group_data_by_day(data):
    """Group the given data by day.

    It assumes that the timestamps are in ascending order.

    Args:
        data: A dictionary with the following form: { constant.TIMESTAMPS: [ ... ], constant.FEATURES: [ ... ] }.

    Returns:
        An array, where each element is a dictionary with the following form: { constant.DAY: day, constant.TIMESTAMPS: [ ... ], constant.FEATURES: [ ... ] }.
    """
    days = np.array([])
    current_day = common_function.date_from_timestamp(data[constant.TIMESTAMPS][0]).day
    current_timestamps = np.array([])
    current_features = np.array([])
    for index, timestamp in enumerate(data[constant.TIMESTAMPS]):
        if index != len(data[constant.TIMESTAMPS]) - 1:
            next_day = common_function.date_from_timestamp(data[constant.TIMESTAMPS][index + 1]).day
        current_timestamps = np.append(current_timestamps, common_function.passed_minutes_on_day(timestamp))
        current_features = np.append(current_features, data[constant.FEATURES][index])
        if index == len(data[constant.TIMESTAMPS]) - 1 or current_day < next_day:
            # add the current day's data
            day_data = {constant.DAY: current_day, constant.TIMESTAMPS: current_timestamps, constant.FEATURES: current_features}
            days = np.append(days, day_data)
            # prepare for the next iteration
            if index != len(data[constant.TIMESTAMPS]) - 1:
                current_day = next_day
                current_timestamps = np.array([])
                current_features = np.array([])
    return days


def reset_scaler():
    """ Reset the global _SCALER instance.
    """
    global _SCALER
    _SCALER = None
