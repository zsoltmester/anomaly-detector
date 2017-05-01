"""
Functions that display the results.
"""

import matplotlib.pyplot as plot

import constant


def display_polinomials(training_data, training_feature_mean, training_interpolation_polynomial, day_data, day_interpolation_polynomial):
    """Display the given polinomials.

    It blocks the main thread while displaying a polinomial.
    """
    plot.scatter(training_data[constant.TIMESTAMPS], training_data[constant.FEATURES], color='silver', label='data points for November')
    plot.scatter(day_data[constant.TIMESTAMPS], training_feature_mean, color='gray', label='avarage data points for November')
    plot.plot(training_interpolation_polynomial[constant.X], training_interpolation_polynomial[constant.Y], color='black', label='interpolation polynomial for November')
    plot.scatter(day_data[constant.TIMESTAMPS], day_data[constant.FEATURES], color='salmon', label='data points for December ' + str(day_data[constant.DAY]))
    plot.plot(day_interpolation_polynomial[constant.X], day_interpolation_polynomial[constant.Y], color='red', label='interpolation polynomial for December ' + str(day_data[constant.DAY]))
    plot.xlabel('time in minutes')
    plot.ylabel('activity')
    plot.title('The Average Day in November vs day ' + str(day_data[constant.DAY]) + ' in December')
    plot.legend()
    plot.show()
