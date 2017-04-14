"""
Utility functions for the anomaly detector to preprocess the dataset.
"""

import csv
from datetime import datetime

import numpy as np
from sklearn import preprocessing

import constant

"""
ID for the square ID column.
"""
COLUMN_SQUARE_ID = 'square_id'

"""
ID for the time interval column.
"""
COLUMN_TIME_INTERVAL = 'time_interval'

"""
ID for the country code column.
"""
COLUMN_COUNTRY_CODE = 'country_code'

"""
ID for the incoming SMS column.
"""
COLUMN_SMS_IN = 'sms_in'

"""
ID for the outgoing SMS column.
"""
COLUMN_SMS_OUT = 'sms_out'

"""
ID for the incoming call column.
"""
COLUMN_CALL_IN = 'call_in'

"""
ID for the outgoing call column.
"""
COLUMN_CALL_OUT = 'call_out'

"""
ID for the internet traffic column.
"""
COLUMN_INTERNET_TRAFFIC = 'internet_traffic'

"""
ID for the foreign activity column.
"""
COLUMN_FOREIGN = 'foreign'

"""
IDs of the columns of the data, ordered as the input data rows.
"""
COLUMNS = (COLUMN_SQUARE_ID, COLUMN_TIME_INTERVAL, COLUMN_COUNTRY_CODE, COLUMN_SMS_IN, COLUMN_SMS_OUT, COLUMN_CALL_IN, COLUMN_CALL_OUT, COLUMN_INTERNET_TRAFFIC)

"""
The scaler for the feature scaling.
"""
_SCALER = None

def read_files(files, squares):
    """Reades the given files and collect the data for the specified squares.

    Args:
        files: Paths to the files. It must be an iterable on strings.
        squares: The squares to read. It must be a collection of ints.

    Returns:
        The list of the read rows, where each item is a dictinary, where the keys are specified in the COLUMNS constant.
    """
    data = []
    for file in files:
        # FIXME a hack to fasten the file reader
        with open(file) as tsv_file:
            tsv_reader = csv.DictReader(tsv_file, delimiter='\t', fieldnames=COLUMNS)
            last_read_square_id = -1
            counter = -1
            for row in tsv_reader:
                if last_read_square_id != int(row[COLUMN_SQUARE_ID]): # assume that the values for a square are groupped together
                    counter += 1
                    if counter < len(squares):
                        last_read_square_id = int(row[COLUMN_SQUARE_ID])
                    else:
                        break
                data.append(row)
        # FIXME this should be the implementation, but it requires much more time to run. i can optimize this a little
        # with open(file) as tsv_file:
        #     print('Reading ' + file)
        #     tsv_reader = csv.DictReader(tsvFile, delimiter='\t', fieldnames=COLUMNS)
        #     for row in tsv_reader:
        #         for square in squares:
        #             if int(row[COLUMN_SQUARE_ID]) == square:
        #                 data.append(row)
    return data

def group_data_by_time_interval(data):
    """Group the given data by the timestamps.

    It summarises the values for each property for the same timestamp, except the country code. Instead of the country
    code, it calculates the activities for the foreign countries.

    Args:
        data: The data as a list of dictionaries, where the keys are the COLUMN_* globals.

    Returns:
        The grouped data as a dictinary, where the keys are the timestamps and the values are the properties for a timestamp as a dictinary. The latter's keys are the following globals: COLUMN_SMS_IN, COLUMN_SMS_OUT, COLUMN_CALL_IN, COLUMN_CALL_OUT, COLUMN_INTERNET_TRAFFIC, COLUMN_FOREIGN.
    """
    grouped_data = {}
    for row in data:
        time_interval = row[COLUMN_TIME_INTERVAL]
        if time_interval in grouped_data:
            for prop in grouped_data[time_interval]:
                grouped_data[time_interval][prop] += float(row[prop]) if row[prop] else 0.
        else:
            grouped_data[time_interval] = {
                COLUMN_SMS_IN : float(row[COLUMN_SMS_IN]) if row[COLUMN_SMS_IN] else 0.,
                COLUMN_SMS_OUT : float(row[COLUMN_SMS_OUT]) if row[COLUMN_SMS_OUT] else 0.,
                COLUMN_CALL_IN : float(row[COLUMN_CALL_IN]) if row[COLUMN_CALL_IN] else 0.,
                COLUMN_CALL_OUT : float(row[COLUMN_CALL_OUT]) if row[COLUMN_CALL_OUT] else 0.,
                COLUMN_INTERNET_TRAFFIC : float(row[COLUMN_INTERNET_TRAFFIC]) if row[COLUMN_INTERNET_TRAFFIC] else 0.,
            }
            # TODO add COLUMN_FOREIGN
    return grouped_data

def _add_row(matrix, new_row):
    """Add the new_row to the matrix.

    Args:
        matrix: The matrix to extend.
        new_row: The new row to add the end of the matrix.

    Returns:
        The extended matrix.
    """
    if matrix is None:
        matrix = np.array(new_row)
    else:
        matrix = np.vstack([matrix, new_row])
    return matrix

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
        new_row = [properties[COLUMN_SMS_IN], properties[COLUMN_SMS_OUT], properties[COLUMN_CALL_IN], properties[COLUMN_CALL_OUT], properties[COLUMN_INTERNET_TRAFFIC]]
        features = _add_row(features, new_row)
    return timestamps, features

def split_data_for_weekdays_and_weekends(timestamps, features):
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
            weekday_features = _add_row(weekday_features, features[index])
        else:
            weekend_timestamps = np.append(weekend_timestamps, timestamp)
            weekend_features = _add_row(weekend_features, features[index])
    return { constant.TIMESTAMPS: weekday_timestamps, constant.FEATURES: weekday_features }, { constant.TIMESTAMPS: weekend_timestamps, constant.FEATURES: weekend_features }

def scale_features(features):
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

def translate_matrix_to_mean_vector(matrix):
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

def drop_outliers(timestamps, features):
    """Drop the outliers from the features. Also drops the related timestamps.

    Args:
        timestamps: The related timestamps.
        features: The features as a numpy array of numpy arrays (a matrix), where each column represents a feature.

    Returns:
        A tuple, with the following items.
        - 1.: The timestamps without the dropped rows' timestamps.
        - 2.: The features without the outliers.
    """
    # TODO
    return timestamps, features

def get_minutes(timestamps):
    """Calculates how many minutes passed that day.

    Args:
        timestamps: The timestamp (milliseconds).

    Returns:
        The number of minutes that passed that day.
    """
    minutes = np.array([])
    for timestamp in timestamps:
        date = datetime.fromtimestamp(float(timestamp) / 1000.0)
        minutes_passed_that_day = constant.MINUTES_PER_HOUR * date.hour + date.minute
        minutes = np.append(minutes, minutes_passed_that_day)
    return minutes

def sort_arrays_based_on_the_first(first_array, second_array):
    """Sort the first array then the second in the same order as the first.

    Args:
        first_array: The first array to sort.
        second_arrays: The second array to sort.

    Returns:
        A tuple with the sorted first and second array.
    """
    order = np.argsort(first_array)
    first_array = np.array(first_array)[order]
    second_array = np.array(second_array)[order]
    return first_array, second_array
