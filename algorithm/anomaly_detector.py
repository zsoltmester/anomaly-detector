# TODO Hogyan kéne még fejleszteni a tranininget:
# - A kódminőséget javítani ezek szerint: https://www.python.org/dev/peps/pep-0008/, https://www.python.org/dev/peps/pep-0257/, https://google.github.io/styleguide/pyguide.html, pylint. (Package vs module vs class.) Ezekkel együtt modularizálni az algoritmust:
#   * A kód csak azokat a hibákat kezeli le, amiket ki is tud javítani. Ha valamit nem tud, vagy olyan állapotba kerül, hogy biztos nem fog tudni értelmes outputot létrehozni, akkor != 0 exit kóddal kilép.
#   * Preprocessor module. A preprocessDataset function feladatait veszi át.
#   * ...
# - A country code segítségével csinálni egy új feature-t.
# - Ahelyett, hogy az összes feature-t aggregáljuk (és lesz belőle az activity), minden feature-t külön kéne kezelni.
# - PCA-t használni.

import initialise
import preprocess
import constant

import matplotlib.pyplot as plot
import numpy as np
from datetime import datetime
from scipy.interpolate import splev
from scipy.interpolate import splrep
from time import time

# parameters
SPLINE_DEGREE = 3
SPLINE_X_SAMPLES = 1440
OUTLIER_CONTROL = 2

trainingFiles, testingFiles, squares = initialise.initialise()

# preprocess the given dataset and return the x and the y values
def preprocessDataset(datasetFiles):
    startTime = time()
    rawData = preprocess.read_files(datasetFiles, squares)
    cleanData = preprocess.group_data_by_time_interval(rawData)
    timestamps, features = preprocess.split_data_for_timestamps_and_features(cleanData)
    weekdays, weekends = preprocess.split_data_for_weekdays_and_weekends(timestamps, features)
    categories = { constant.WEEKDAYS: weekdays, constant.WEEKENDS: weekends }
    for category_name, category in categories.items():
        category[constant.FEATURES] = preprocess.scale_features(category[constant.FEATURES])
        category[constant.FEATURES] = preprocess.translate_matrix_to_mean_vector(category[constant.FEATURES]) # TODO this should depend on an input parameter
    print('Time for preprocess a dataset: ', round(time() - startTime, 3), ' sec')
    return categories

trainingData = preprocessDataset(trainingFiles)
for category_name, category in trainingData.items():
    category[constant.TIMESTAMPS] = preprocess.get_minutes(category[constant.TIMESTAMPS])
    category[constant.TIMESTAMPS], category[constant.FEATURES] = preprocess.sort_arrays_based_on_the_first(category[constant.TIMESTAMPS], category[constant.FEATURES])

testingData = preprocessDataset(testingFiles)
for category_name, category in testingData.items():
    category[constant.TIMESTAMPS], category[constant.FEATURES] = preprocess.sort_arrays_based_on_the_first(category[constant.TIMESTAMPS], category[constant.FEATURES])

xTraining = trainingData[constant.WEEKDAYS][constant.TIMESTAMPS]
yTraining = trainingData[constant.WEEKDAYS][constant.FEATURES]
xWeekendTraining = trainingData[constant.WEEKENDS][constant.TIMESTAMPS]
yWeekendTraining = trainingData[constant.WEEKENDS][constant.FEATURES]

xTesting = testingData[constant.WEEKDAYS][constant.TIMESTAMPS]
yTesting = testingData[constant.WEEKDAYS][constant.FEATURES]
xWeekendTesting = testingData[constant.WEEKENDS][constant.TIMESTAMPS]
yWeekendTesting = testingData[constant.WEEKENDS][constant.FEATURES]

# remove the duplicates from the trainig x vectors
xTrainingUnique = np.unique(xTraining)
xWeekendTrainingUnique = np.unique(xWeekendTraining)

# create a interpolation polynomial based on the given x and y values
def createInterpolationPolynomial(x, y):
    interpolationPolynomial = splrep(x, y, k=SPLINE_DEGREE)
    x = np.linspace(np.amin(x), np.amax(x), SPLINE_X_SAMPLES)
    y = splev(x, interpolationPolynomial)
    return x, y

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
xTrainingInterpolationPolynomial, yTrainingInterpolationPolynomial = createInterpolationPolynomial(xTrainingUnique, yTrainingAverage)
xWeekendTrainingInterpolationPolynomial, yWeekendTrainingInterpolationPolynomial = createInterpolationPolynomial(xWeekendTrainingUnique, yWeekendTrainingAverage)

# show the given day's data and the November's avarage data in a plot
def showPlotForDay(xTraining, yTraining, xTrainingUnique, yTrainingAverage, xTrainingInterpolationPolynomial, yTrainingInterpolationPolynomial, day, xDay, yDay):
    plot.scatter(xTraining, yTraining, color='silver', label='data points for November')
    plot.scatter(xTrainingUnique, yTrainingAverage, color='gray', label='avarage data points for November')
    plot.plot(xTrainingInterpolationPolynomial, yTrainingInterpolationPolynomial, color='black', label='interpolation polynomial for November')

    plot.scatter(xDay, yDay, color='salmon', label='data points for December '+str(day))
    xDayInterpolationPolynomial, yDayInterpolationPolynomial = createInterpolationPolynomial(xDay, yDay)
    plot.plot(xDayInterpolationPolynomial, yDayInterpolationPolynomial, color='red', label='interpolation polynomial for December '+str(day))

    plot.xlabel('time in minutes')
    plot.ylabel('activity')
    plot.title('The Average Day in November vs day ' + str(day) + ' in December')
    plot.legend()
    plot.show()

# plot the results
def plotResults(xTesting, yTesting, xTraining, yTraining, xTrainingUnique, yTrainingAverage, xTrainingInterpolationPolynomial, yTrainingInterpolationPolynomial):
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
                showPlotForDay(xTraining, yTraining, xTrainingUnique, yTrainingAverage, xTrainingInterpolationPolynomial, yTrainingInterpolationPolynomial, currentDay, xDay, yDay)
            # prepare for the new day
            currentDay = day
            xDay = np.array([])
            yDay = np.array([])
        # collect the day's data
        xDay = np.append(xDay, minutes - (day - 1) * constant.MINUTES_PER_DAY)
        yDay = np.append(yDay, yTesting[index])

# walk through each day in the testing dataset and show each day's data and the November's avarage data in a plot
plotResults(xTesting, yTesting, xTraining, yTraining, xTrainingUnique, yTrainingAverage, xTrainingInterpolationPolynomial, yTrainingInterpolationPolynomial)
plotResults(xWeekendTesting, yWeekendTesting, xWeekendTraining, yWeekendTraining, xWeekendTrainingUnique, yWeekendTrainingAverage, xWeekendTrainingInterpolationPolynomial, yWeekendTrainingInterpolationPolynomial)
