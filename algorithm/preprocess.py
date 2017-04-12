"""
Utility functions for the anomaly detector to preprocess the dataset.
"""

import csv

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
            # add COLUMN_FOREIGN
    return grouped_data
