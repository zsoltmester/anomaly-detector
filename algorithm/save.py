"""
Utility functions for the anomaly detector to save the dataset.
"""

import sqlite3

import constant


def write_differences_to_sqlite(square, differences):
    """Saves the given differences to an SQLite database.

    Args:
        square: The square ID of the differences, as an int.
        differences: The differences in form { day_number_as_int: { minutes: difference, ...}, ... }.
    """
    connection = sqlite3.connect(constant.DIFFERENCES_DB)
    cursor = connection.cursor()

    try:
        cursor.execute('CREATE TABLE differences (square integer, day integer, minutes integer, difference real)')
    except sqlite3.OperationalError as error:
        # Nothing to do, the table already exists
        pass

    for day, values in differences.items():
        for minutes, difference in values.items():
            cursor.execute("INSERT INTO differences VALUES (" + str(square) + ", " + str(day) + ", " + str(minutes) + "," + str(difference) + ")")

    connection.commit()
    connection.close()


def read_differences_from_sqlite():
    """ Reads the differences from the constant.DIFFERENCES_DB and print each row.
    """
    connection = sqlite3.connect(constant.DIFFERENCES_DB)
    cursor = connection.cursor()
    for row in cursor.execute('SELECT * FROM differences ORDER BY square, day, minutes'):
        print(row)
    connection.close()
