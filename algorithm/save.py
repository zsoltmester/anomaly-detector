"""
Utility functions for the anomaly detector to save the dataset.
"""

import sqlite3

import constant


def write_square_to_database(square, mean_activities, actual_activities, standard_deviations):
    """Saves the given square's properties to an SQLite database.

    Args:
        square: The square ID, as an int.
        mean_activities: The mean activities based on the training data in form { day_number_as_int: { minutes: mean activity, ...}, ... }.
        actual_activities: The actual activities in form { day_number_as_int: { minutes: actual activity, ...}, ... }.
        standard_deviations: The standard deviations of the training data in form { day_number_as_int: { minutes: standard deviation, ...}, ... }.
    """
    connection = sqlite3.connect(constant.DATABASE_NAME)
    cursor = connection.cursor()

    try:
        cursor.execute('CREATE TABLE squares (square integer, day integer, minutes integer, mean_activity real, actual_activity real, standard_deviation real)')
    except sqlite3.OperationalError as error:
        # Nothing to do, the table already exists
        pass

    for day, values in mean_activities.items():
        for minutes, mean_activity in values.items():
            cursor.execute("INSERT INTO squares VALUES (" + str(square) + ", " + str(day) + ", " + str(minutes) + ", " + str(mean_activity) + "," + str(actual_activities[day][minutes]) + "," + str(standard_deviations[day][minutes]) + ")")

    connection.commit()
    connection.close()


def read_database():
    """ Reads the database named constant.DATABASE_NAME and print each row.
    """
    connection = sqlite3.connect(constant.DATABASE_NAME)
    cursor = connection.cursor()
    for row in cursor.execute('SELECT * FROM squares ORDER BY square, day, minutes'):
        print(row)
    connection.close()
