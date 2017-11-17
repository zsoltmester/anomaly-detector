"""
Functions that display the results.
"""

import matplotlib.pyplot as plot

import constant


def display_polinomials(training_data, training_features_mean, training_features_standard_deviation_upper_bound, training_features_standard_deviation_lower_bound, training_interpolation_polynomial, day_data, day_interpolation_polynomial):
    """Display the given polinomials.

    It blocks the main thread while displaying a polinomial.
    """
    plot.scatter(training_data[constant.TIMESTAMPS], training_data[constant.FEATURES], color='silver', label='activity in November')
    plot.scatter(day_data[constant.TIMESTAMPS], training_features_mean, color='gray', label='avarage activity November')
    plot.scatter(day_data[constant.TIMESTAMPS], training_features_standard_deviation_upper_bound, color='orange', label='avarage activity, plus the standard deviation in November')
    plot.scatter(day_data[constant.TIMESTAMPS], training_features_standard_deviation_lower_bound, color='orange', label='avarage activity, minus the standard deviation in November')
    plot.plot(training_interpolation_polynomial[constant.X], training_interpolation_polynomial[constant.Y], color='black', label='interpolation polynomial on the avarage activity in November')
    plot.scatter(day_data[constant.TIMESTAMPS], day_data[constant.FEATURES], color='salmon', label='activity in December ' + str(day_data[constant.DAY]))
    plot.plot(day_interpolation_polynomial[constant.X], day_interpolation_polynomial[constant.Y], color='red', label='interpolation polynomial on the activity in December ' + str(day_data[constant.DAY]))
    plot.xlabel('time in minutes')
    plot.ylabel('activity')
    plot.title('The Average Day in November vs day ' + str(day_data[constant.DAY]) + ' in December')
    plot.legend()
    plot.show()
