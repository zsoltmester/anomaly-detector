# TODO Hogyan kéne még fejleszteni a tranininget:
# - A country code segítségével csinálni egy új feature-t.
# - Ahelyett, hogy az összes feature-t aggregáljuk (és lesz belőle az activity), minden feature-t külön kéne kezelni.
# - PCA-t használni.

import matplotlib.pyplot as plot
import numpy as np

from argparse import ArgumentParser
from csv import DictReader
from datetime import datetime
from os import walk
from os.path import join
from scipy.interpolate import splev
from scipy.interpolate import splrep
from sklearn.preprocessing import MinMaxScaler
from time import time

# constants
MINUTES_PER_HOUR = 60
MINUTES_PER_DAY = 24 * MINUTES_PER_HOUR

# parameters
SPLINE_DEGREE = 3
SPLINE_X_SAMPLES = 1440
OUTLIER_CONTROL = 2

# parse the arguments
parser = ArgumentParser(description='The machine learning algorithm for the anomaly detector application.')
parser.add_argument('--training', help='Path to the root directory of the training dataset.', required=True)
parser.add_argument('--testing', help='Path to the root directory of the testing dataset.', required=True)
parser.add_argument('-s','--squares', type=int, help='The number of square to analyze.', required=True)
args = vars(parser.parse_args())
trainingFilesRoot = args['training']
testingFilesRoot = args['testing']
squares = args['squares']

# extend the given y matrix with the provided data
def extendYMatrixWithData(yMatrix, data):
    yNewRow = [data['sms_in'], data['sms_out'], data['call_in'], data['call_out'], data['internet_traffic']]
    if yMatrix is None:
        yMatrix = np.array(yNewRow)
    else:
        yMatrix = np.vstack([yMatrix, yNewRow])
    return yMatrix

# scale the given features to make them comparable
def scaleFeatures(featureMatrix):
    return MinMaxScaler().fit_transform(featureMatrix)

# translate the rows of the given matrix into their mean values
def translateRowsToTheirAverages(matrix):
    meanVector = np.array([])
    for row in matrix:
        meanVector = np.append(meanVector, np.average(row))
    return meanVector

# sort the first array, then the second with the same order as the first
def sortArraysBasedOnTheFirst(first, second):
    order = np.argsort(first)
    first = np.array(first)[order]
    second = np.array(second)[order]
    return first, second

# preprocess the dataset under the given root and return the x and the y values
def preprocessDataset(datasetRoot, isTesting=False):
    startTime = time()

    # collect the dataset's files
    datasetFiles = []
    for (dirPath, dirNames, fileNames) in walk(datasetRoot):
        datasetFiles.extend([join(dirPath, fileName) for fileName in fileNames])

    # walk through the dataset's files and read the data for the given number of squares
    fieldNames=('square_id', 'time_interval', 'country_code', 'sms_in', 'sms_out', 'call_in', 'call_out', 'internet_traffic')
    rawData = []
    for datasetFile in datasetFiles:
        with open(datasetFile) as tsvFile:
            tsvReader = DictReader(tsvFile, delimiter='\t', fieldnames=fieldNames)
            lastSquareId = -1
            counter = -1
            for row in tsvReader:
                if lastSquareId != int(row['square_id']): # assume that the values for a square are groupped together
                    counter += 1
                    if counter < squares:
                        lastSquareId = int(row['square_id'])
                    else:
                        break
                rawData.append(row)

    # create the data dictionary, where the keys are the time intervals and the values are the dictinary with the data. also we drop the country code
    cleanData = {}
    for row in rawData:
        if row['time_interval'] in cleanData:
            for key in cleanData[row['time_interval']]:
                cleanData[row['time_interval']][key] += float(row[key]) if row[key] != '' else float(0)
        else:
            cleanData[row['time_interval']] = {
                'sms_in' : float(row['sms_in']) if row['sms_in'] != '' else float(0),
                'sms_out' : float(row['sms_out']) if row['sms_out'] != '' else float(0),
                'call_in' : float(row['call_in']) if row['call_in'] != '' else float(0),
                'call_out' : float(row['call_out']) if row['call_out'] != '' else float(0),
                'internet_traffic' : float(row['internet_traffic']) if row['internet_traffic'] != '' else float(0)
            }

    # collect the x values and the y values for each row
    x = np.array([])
    xWeekend = np.array([])
    yMatrix = None
    yMatrixWeekend = None
    for timestamp, properties in cleanData.items():
        date = datetime.fromtimestamp(float(timestamp) / 1000.0)

        minutes = MINUTES_PER_HOUR * date.hour + date.minute
        if isTesting:
            minutes += MINUTES_PER_DAY * (date.day - 1)

        if date.weekday() < 5 and (not ((not isTesting) and date.day == 1)): # november 1 is a public holiday in Italy
            x = np.append(x, minutes)
            yMatrix = extendYMatrixWithData(yMatrix, properties)
        else:
            xWeekend = np.append(xWeekend, minutes)
            yMatrixWeekend = extendYMatrixWithData(yMatrixWeekend, properties)

    # scale the y metrices into (0,1) by column
    yMatrix = scaleFeatures(yMatrix)
    yMatrixWeekend = scaleFeatures(yMatrixWeekend)

    # reduce the columns in the y matrices to 1, by calculating the average of each row
    y = translateRowsToTheirAverages(yMatrix)
    yWeekend = translateRowsToTheirAverages(yMatrixWeekend)

    # sort the values by the timestamp
    x, y = sortArraysBasedOnTheFirst(x, y)
    xWeekend, yWeekend = sortArraysBasedOnTheFirst(xWeekend, yWeekend)

    print('Time for preprocess a dataset: ', round(time() - startTime, 3), ' sec')
    return x, y, xWeekend, yWeekend

# preprocess the training dataset
xTraining, yTraining, xWeekendTraining, yWeekendTraining = preprocessDataset(trainingFilesRoot)

# preprocess the testing dataset
xTesting, yTesting, xWeekendTesting, yWeekendTesting = preprocessDataset(testingFilesRoot, isTesting=True)

# create a interpolation polynomial based on the given x and y values
def createInterpolationPolynomial(x, y):
    interpolationPolynomial = splrep(x, y, k=SPLINE_DEGREE)
    x = np.linspace(np.amin(x), np.amax(x), SPLINE_X_SAMPLES)
    y = splev(x, interpolationPolynomial)
    return x, y

# remove the duplicates from the trainig x vectors
xTrainingUnique = np.unique(xTraining)
xWeekendTrainingUnique = np.unique(xWeekendTraining)

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
            yTrainingAverage = np.append(yTrainingAverage, np.mean(yCurrentValues))
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
        day = int(int(minutes) / int(24 * 60) + 1)
        if currentDay < day: # if we collected all data for a day (assume that the minutes are in ascending order)
            if currentDay > 0: # skip day zero
                showPlotForDay(xTraining, yTraining, xTrainingUnique, yTrainingAverage, xTrainingInterpolationPolynomial, yTrainingInterpolationPolynomial, currentDay, xDay, yDay)
            # prepare for the new day
            currentDay = day
            xDay = np.array([])
            yDay = np.array([])
        # collect the day's data
        xDay = np.append(xDay, minutes - (day - 1) * MINUTES_PER_DAY)
        yDay = np.append(yDay, yTesting[index])

# walk through each day in the testing dataset and show each day's data and the November's avarage data in a plot
plotResults(xTesting, yTesting, xTraining, yTraining, xTrainingUnique, yTrainingAverage, xTrainingInterpolationPolynomial, yTrainingInterpolationPolynomial)
plotResults(xWeekendTesting, yWeekendTesting, xWeekendTraining, yWeekendTraining, xWeekendTrainingUnique, yWeekendTrainingAverage, xWeekendTrainingInterpolationPolynomial, yWeekendTrainingInterpolationPolynomial)
