"""
Utility functions for the anomaly detector to preprocess the dataset.
"""

import csv
from datetime import datetime

import numpy as np
from sklearn import preprocessing

import common_function
import constant

"""
IDs of the columns of the data, ordered as the input data rows.
"""
_COLUMNS = (constant.FEATURE_SQUARE_ID, constant.FEATURE_TIME_INTERVAL, constant.FEATURE_COUNTRY_CODE, constant.FEATURE_SMS_IN, constant.FEATURE_SMS_OUT, constant.FEATURE_CALL_IN, constant.FEATURE_CALL_OUT, constant.FEATURE_INTERNET_TRAFFIC)

"""
The scaler for the feature scaling.
"""
_SCALER = None

def _read_files(files, squares):
    """Reades the given files and collect the data for the specified squares.

    Args:
        files: Paths to the files. It must be an iterable on strings.
        squares: The squares to read. It must be a collection of ints.

    Returns:
        The list of the read rows, where each item is a dictinary, where the keys are specified in the _COLUMNS constant.
    """
    data = []
    for file in files:
        # FIXME a hack to fasten the file reader
        with open(file) as tsv_file:
            tsv_reader = csv.DictReader(tsv_file, delimiter='\t', fieldnames=_COLUMNS)
            last_read_square_id = -1
            counter = -1
            for row in tsv_reader:
                if last_read_square_id != int(row[constant.FEATURE_SQUARE_ID]): # assume that the values for a square are groupped together
                    counter += 1
                    if counter < len(squares):
                        last_read_square_id = int(row[constant.FEATURE_SQUARE_ID])
                    else:
                        break
                data.append(row)
        # FIXME this should be the implementation, but it requires much more time to run. i can optimize this a little
        # with open(file) as tsv_file:
        #     print('Reading ' + file)
        #     tsv_reader = csv.DictReader(tsvFile, delimiter='\t', fieldnames=_COLUMNS)
        #     for row in tsv_reader:
        #         for square in squares:
        #             if int(row[constant.FEATURE_SQUARE_ID]) == square:
        #                 data.append(row)
    return data

def _group_data_by_time_interval(data):
    """Group the given data by the timestamps.

    It summarises the values for each property for the same timestamp, except the country code. Instead of the country
    code, it calculates the activities for the foreign countries.

    Args:
        data: The data as a list of dictionaries, where the keys are the FEATURE_* constants.

    Returns:
        The grouped data as a dictinary, where the keys are the timestamps and the values are the properties for a timestamp as a dictinary. The latter's keys are the following globals: constant.FEATURE_SMS_IN, constant.FEATURE_SMS_OUT, constant.FEATURE_CALL_IN, constant.FEATURE_CALL_OUT, constant.FEATURE_INTERNET_TRAFFIC, constant.FEATURE_FOREIGN.
    """
    grouped_data = {}
    for row in data:
        time_interval = row[constant.FEATURE_TIME_INTERVAL]
        if time_interval in grouped_data:
            for prop in grouped_data[time_interval]:
                grouped_data[time_interval][prop] += float(row[prop]) if row[prop] else 0.
        else:
            grouped_data[time_interval] = {
                constant.FEATURE_SMS_IN : float(row[constant.FEATURE_SMS_IN]) if row[constant.FEATURE_SMS_IN] else 0.,
                constant.FEATURE_SMS_OUT : float(row[constant.FEATURE_SMS_OUT]) if row[constant.FEATURE_SMS_OUT] else 0.,
                constant.FEATURE_CALL_IN : float(row[constant.FEATURE_CALL_IN]) if row[constant.FEATURE_CALL_IN] else 0.,
                constant.FEATURE_CALL_OUT : float(row[constant.FEATURE_CALL_OUT]) if row[constant.FEATURE_CALL_OUT] else 0.,
                constant.FEATURE_INTERNET_TRAFFIC : float(row[constant.FEATURE_INTERNET_TRAFFIC]) if row[constant.FEATURE_INTERNET_TRAFFIC] else 0.,
            }
            # TODO add constant.FEATURE_FOREIGN
    return grouped_data

def _split_data_for_timestamps_and_features(data):
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
        new_row = [properties[constant.FEATURE_SMS_IN], properties[constant.FEATURE_SMS_OUT], properties[constant.FEATURE_CALL_IN], properties[constant.FEATURE_CALL_OUT], properties[constant.FEATURE_INTERNET_TRAFFIC]]
        features = common_function.add_row_to_matrix(features, new_row)
    return timestamps, features

def _split_data_for_weekdays_and_weekends(timestamps, features):
    """Split the data for weekdays and weekends.

    Args:
        timestamps: The timestamps as a numpy array of strings.
        features: The features as a numpy array of numpy arrays (a matrix), where each column represents a feature.

    Returns:
        A tuple, where the first element corresponds for the weekdays and the second for the weekends. Each element is a list, with the following items.
        - 1.: The timestamps as a numpy array of strings. (as given)
        - 2.: The features as a numpy array of numpy arrays (a matrix), where each column represents a feature. (as given)
    """
    weekday_timestamps = np.array([])
    weekend_timestamps = np.array([])
    weekday_features = None
    weekend_features = None
    for index, timestamp in enumerate(timestamps):
        date = datetime.fromtimestamp(float(timestamp) / 1000.)
        if date.weekday() < 5:
            weekday_timestamps = np.append(weekday_timestamps, timestamp)
            weekday_features = common_function.add_row_to_matrix(weekday_features, features[index])
        else:
            weekend_timestamps = np.append(weekend_timestamps, timestamp)
            weekend_features = common_function.add_row_to_matrix(weekend_features, features[index])
    return { constant.TIMESTAMPS: weekday_timestamps, constant.FEATURES: weekday_features }, { constant.TIMESTAMPS: weekend_timestamps, constant.FEATURES: weekend_features }

def _scale_features(features):
    """Scale the features with a min-max scaler. It is saving the firstly created scaler and use it as a transformer every time.

    Args:
        features: The features as a numpy array of numpy arrays (a matrix), where each column represents a feature.

    Returns:
        - 1.: The scaled features.
    """
    global _SCALER
    if _SCALER is None:
        _SCALER = preprocessing.MinMaxScaler().fit(features)
    return _SCALER.transform(features)

def _translate_matrix_to_mean_vector(matrix):
    """Translate each row in the matrix to their mean values.

    Args:
        features: The features as a numpy array of numpy arrays (a matrix), where each column represents a feature.

    Returns:
        - 1.: The vector of the mean values.
    """
    mean_vector = np.array([])
    for row in matrix:
        mean_vector = np.append(mean_vector, np.mean(row))
    return mean_vector

def preprocess_dataset(dataset_files, squares, isTraining = False):
    """Preprocess the given dataset.

    1. Reads the files.
    2. Group by time interval.
    3. Split to timestamps and features.
    4. Split to weekdays and weekends.
    5. Scale.
    6. Select and convert the specified features.
    7. If it's a training dataset, convert timestamps to the passed minutes each day.
    8. Sort the arrays based on the timestamps.
    If the dataset is large, it will run for a while.

    Args:
        dataset_files: List of the paths of the dataset files.
        squares: The squares to read.
        isTraining: Indicates if it's a training dataset or not. False by default.

    Returns:
        The processed dataset as a dictionary, with the following schema:
        {
            constant.WEEKDAYS: { constant.TIMESTAMPS: [ ... ], constant.FEATURES: [ ... ] },
            constant.WEEKENDS: { constant.TIMESTAMPS: [ ... ], constant.FEATURES: [ ... ] }
        }
    """
    data = _read_files(dataset_files, squares)
    data = _group_data_by_time_interval(data)
    timestamps, features = _split_data_for_timestamps_and_features(data)
    weekdays, weekends = _split_data_for_weekdays_and_weekends(timestamps, features)
    categories = { constant.WEEKDAYS: weekdays, constant.WEEKENDS: weekends }
    for category_name, category in categories.items():
        category[constant.FEATURES] = _scale_features(category[constant.FEATURES])
        category[constant.FEATURES] = _translate_matrix_to_mean_vector(category[constant.FEATURES]) # TODO this should depend on an input parameter
        if isTraining:
            category[constant.TIMESTAMPS] = common_function.get_minutes(category[constant.TIMESTAMPS])
        category[constant.TIMESTAMPS], category[constant.FEATURES] = common_function.sort_arrays_based_on_the_first(category[constant.TIMESTAMPS], category[constant.FEATURES])
    return categories
