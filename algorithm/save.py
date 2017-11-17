"""
Utility functions for the anomaly detector to save the dataset.
"""

import sqlite3

import constant


def write_square_to_database(square, standard_deviations, differences):
    """Saves the given squares' properties to an SQLite database.

    Args:
        square: The square ID, as an int.
        standard_deviations: The standard deviations of the training data in form { day_number_as_int: { minutes: standard deviation, ...}, ... }.
        differences: The differences in form { day_number_as_int: { minutes: difference, ...}, ... }.
    """
    connection = sqlite3.connect(constant.DATABASE_NAME)
    cursor = connection.cursor()

    try:
        cursor.execute('CREATE TABLE squares (square integer, day integer, minutes integer, standard_deviations real, difference real)')
    except sqlite3.OperationalError as error:
        # Nothing to do, the table already exists
        pass

    for day, values in differences.items():
        for minutes, difference in values.items():
            cursor.execute("INSERT INTO squares VALUES (" + str(square) + ", " + str(day) + ", " + str(minutes) + "," + str(standard_deviations[day][minutes]) + "," + str(difference) + ")")

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
