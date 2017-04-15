# TODO Hogyan kéne még fejleszteni a tranininget:
# - A kódminőséget javítani ezek szerint: https://www.python.org/dev/peps/pep-0008/, https://www.python.org/dev/peps/pep-0257/, https://google.github.io/styleguide/pyguide.html, pylint. (Package vs module vs class.) Ezekkel együtt modularizálni az algoritmust:
#   * A kód csak azokat a hibákat kezeli le, amiket ki is tud javítani. Ha valamit nem tud, vagy olyan állapotba kerül, hogy biztos nem fog tudni értelmes outputot létrehozni, akkor != 0 exit kóddal kilép.
# - A country code segítségével csinálni egy új feature-t.
# - Ahelyett, hogy az összes feature-t aggregáljuk (és lesz belőle az activity), minden feature-t külön kéne kezelni.
# - PCA-t használni.

from datetime import datetime
from time import time

import matplotlib.pyplot as plot
import numpy as np

import constant
import initialise
import interpolate
import preprocess

print('Initialize the algorithm...')
start_time = time()
training_files, testing_files, squares = initialise.initialise()
print('Done to initialze the algorithm. Time: ', round(time() - start_time, 3), ' sec')

print('Preprocess the training dataset...')
start_time = time()
training_data = preprocess.preprocess_dataset(training_files, squares, isTraining=True)
print('Done to preprocess the training dataset. Time: ', round(time() - start_time, 3), ' sec')

xTraining = training_data[constant.WEEKDAYS][constant.TIMESTAMPS]
yTraining = training_data[constant.WEEKDAYS][constant.FEATURES]
xWeekendTraining = training_data[constant.WEEKENDS][constant.TIMESTAMPS]
yWeekendTraining = training_data[constant.WEEKENDS][constant.FEATURES]

# remove the duplicates from the trainig x vectors
xTrainingUnique = np.unique(xTraining)
xWeekendTrainingUnique = np.unique(xWeekendTraining)

OUTLIER_CONTROL = 2

# drop the outliers from the given dataset
def dropOutliers(dataset):
    difference = abs(dataset - np.mean(dataset))
    standardDeviation = np.std(dataset)
    maxAllowedDifference = OUTLIER_CONTROL * standardDeviation
    return dataset[difference < maxAllowedDifference]

# create an average value for each timestamp and return them in a vector
def createAverageForEachTimestamp(timestamps, values):
    yTrainingAverage = np.array([])
    currentTimstamp = 0
    yCurrentValues = np.array([])
    for index, timestamp in enumerate(timestamps):
        if currentTimstamp < timestamp:
            # add the average of the collected y values
            yCurrentValues = dropOutliers(yCurrentValues)
            yTrainingAverage = np.append(yTrainingAverage, np.average(yCurrentValues))
            # prepare for the new timestamp
            currentTimstamp = timestamp
            yCurrentValues = np.array([])
        yCurrentValues = np.append(yCurrentValues, values[index])
    yTrainingAverage = np.append(yTrainingAverage, np.average(yCurrentValues))
    return yTrainingAverage

# create the average y values for each timestamp in the traning dataset
yTrainingAverage = createAverageForEachTimestamp(xTraining, yTraining)
yWeekendTrainingAverage = createAverageForEachTimestamp(xWeekendTraining, yWeekendTraining)

# create the interpolation polynomials based on the training dataset
training_weekday_interpolation_polynomial = interpolate.create_interpolation_polynomial(xTrainingUnique, yTrainingAverage)
training_weekend_interpolation_polynomial = interpolate.create_interpolation_polynomial(xWeekendTrainingUnique, yWeekendTrainingAverage)

# show the given day's data and the November's avarage data in a plot
def showPlotForDay(xTraining, yTraining, xTrainingUnique, yTrainingAverage, training_interpolation_polynomial, day, xDay, yDay):
    plot.scatter(xTraining, yTraining, color='silver', label='data points for November')
    plot.scatter(xTrainingUnique, yTrainingAverage, color='gray', label='avarage data points for November')
    plot.plot(training_interpolation_polynomial[constant.X], training_interpolation_polynomial[constant.Y], color='black', label='interpolation polynomial for November')

    plot.scatter(xDay, yDay, color='salmon', label='data points for December '+str(day))
    day_interpolation_polynomial = interpolate.create_interpolation_polynomial(xDay, yDay)
    plot.plot(day_interpolation_polynomial[constant.X], day_interpolation_polynomial[constant.Y], color='red', label='interpolation polynomial for December ' + str(day))

    plot.xlabel('time in minutes')
    plot.ylabel('activity')
    plot.title('The Average Day in November vs day ' + str(day) + ' in December')
    plot.legend()
    plot.show()

# plot the results
def plotResults(xTesting, yTesting, xTraining, yTraining, xTrainingUnique, yTrainingAverage, training_interpolation_polynomial):
    xDay = None
    yDay = None
    currentDay = 0
    for index, minutes in enumerate(xTesting):
        date = datetime.fromtimestamp(float(minutes) / 1000.0)
        minutes = constant.MINUTES_PER_HOUR * date.hour + date.minute
        minutes += constant.MINUTES_PER_DAY * (date.day - 1)
        day = int(int(minutes) / int(24 * 60) + 1)
        if currentDay < day: # if we collected all data for a day (assume that the minutes are in ascending order)
            if currentDay > 0: # skip day zero
                showPlotForDay(xTraining, yTraining, xTrainingUnique, yTrainingAverage, training_interpolation_polynomial, currentDay, xDay, yDay)
            # prepare for the new day
            currentDay = day
            xDay = np.array([])
            yDay = np.array([])
        # collect the day's data
        xDay = np.append(xDay, minutes - (day - 1) * constant.MINUTES_PER_DAY)
        yDay = np.append(yDay, yTesting[index])


testing_data = preprocess.preprocess_dataset(testing_files, squares)
xTesting = testing_data[constant.WEEKDAYS][constant.TIMESTAMPS]
yTesting = testing_data[constant.WEEKDAYS][constant.FEATURES]
xWeekendTesting = testing_data[constant.WEEKENDS][constant.TIMESTAMPS]
yWeekendTesting = testing_data[constant.WEEKENDS][constant.FEATURES]

# walk through each day in the testing dataset and show each day's data and the November's avarage data in a plot
plotResults(xTesting, yTesting, xTraining, yTraining, xTrainingUnique, yTrainingAverage, training_weekday_interpolation_polynomial)
plotResults(xWeekendTesting, yWeekendTesting, xWeekendTraining, yWeekendTraining, xWeekendTrainingUnique, yWeekendTrainingAverage, training_weekend_interpolation_polynomial)
