# Amit az algoritmus megvalósít:
# Egy négyzetet tud elemezni és annak indexét paraméterként kapja. Összeállít egy átlagos novemberi napot az adott négyzeten. Egy görbe, amit egy regresszor hoz létre, lesz az átlagos nap.
# - Végigmegy a training data összes napjának adott négyzetén és minden timestampre csinál egy targetet (nevezzük activitynek). Úgy hozza létre a activityt, hogy veszi az SMS in/out és call in/out adatok (tehát 4 különböző, de összehasonlítható) átlagát.
# - Kirajzolja ezeket az értékeket.

# TODO Hogyan kéne még fejleszteni a tranininget:
# - Használni az internet trafficot is, mint targetet (beleszámolni az activitybe, mint a többi adatot). Ehhez már kell a feature scaling, mert az internet traffic nem összehasonlítható a többivel.
# - Ahelyett, hogy az összes feture-t aggregáljuk (és lesz belőle az activity), minden feature-t külön kéne kezelni.
# - Kiszűrni a training databól az outlinerket, hisz egy átlagos napot akarunk megkapni.
# - Parameter optimizerel a paramétereit a modelnek a legjobbra lőni.
# - Az SVR helyett más regresszort is kipróbálni.

# TODO Kérdések:
# - A country code-al érdemes lenne foglalkozni? Jelenleg kidobom.

from argparse import ArgumentParser
from os import walk
from os.path import join
from csv import DictReader
from time import time
from datetime import datetime
import matplotlib.pyplot as plot
import numpy as np
from sklearn.svm import SVR

# parse the arguments
parser = ArgumentParser(description='The machine learning algorithm for the anomaly detector.')
parser.add_argument('--training', help='Path to the root directory of the training dataset.', required=True)
parser.add_argument('--testing', help='Path to the root directory of the testing dataset.', required=True)
parser.add_argument('-s','--square', type=int, help='The square to analyze.', required=True)
args = vars(parser.parse_args())
trainingFilesRoot = args['training']
testingFilesRoot = args['testing']
square = args['square']

# preprocess the dataset under the given root and return the features and the targets
def preprocessDataset(datasetRoot, isTesting=False):
    startTime = time()

    # collect the dataset's files
    datasetFiles = []
    for (dirPath, dirNames, fileNames) in walk(datasetRoot):
        datasetFiles.extend([join(dirPath, fileName) for fileName in fileNames])

    # walk through the dataset's files and read the data for the given square
    fieldNames=('square_id', 'time_interval', 'country_code', 'sms_in', 'sms_out', 'call_in', 'call_out', 'internet_traffic')
    rawData = []
    for datasetFile in datasetFiles:
        with open(datasetFile) as tsvFile:
            tsvReader = DictReader(tsvFile, delimiter='\t', fieldnames=fieldNames)
            for row in tsvReader:
                if int(row['square_id']) == square:
                    rawData.append(row)
                elif int(row['square_id']) > square: # assume that the square id is increasing in each file
                    break

    # drop country code and the internet traffic and aggregate the rest
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
                'call_out' : float(row['call_out']) if row['call_out'] != '' else float(0)
            }

    # collect the features and the targets
    features = np.array([])
    targets = np.array([])
    for timestamp, properties in cleanData.items():
        date = datetime.fromtimestamp(float(timestamp) / 1000.0)
        minutes = 60 * date.hour + date.minute
        if isTesting:
            minutes += 24 * 60 * (date.day - 1)
        features = np.append(features, minutes)
        average = (properties['sms_in'] + properties['sms_out'] + properties['call_in'] + properties['call_out']) / 4
        targets = np.append(targets, average)

    # sort the arrays by the timestamp
    order = np.argsort(features)
    features = np.array(features)[order]
    targets = np.array(targets)[order]

    features = features.reshape(-1, 1) # required by sklearn

    print('Time for preprocess a dataset: ', round(time() - startTime, 3), ' sec')
    return targets, features

# preprocess the training dataset
targetsForTraining, featuresForTraining = preprocessDataset(trainingFilesRoot)
print('Targets for training: ', targetsForTraining)
print('Features for training: ', featuresForTraining)

# preprocess the testing dataset
targetsForTesting, featuresForTesting = preprocessDataset(testingFilesRoot, isTesting=True)
print('Targets for testing: ', targetsForTesting)
print('Features for testing: ', featuresForTesting)

# create the regression line
def createRegressionLine(features, targets):
    start_time = time()
    model = SVR(kernel='rbf')
    model = model.fit(features, targets)
    line = model.predict(features)
    score = model.score(features, targets)
    print('Create regression line time: ', round(time() - start_time, 3), ' sec')
    return line, score

# create the regression line based on the training data
regressionLine, regressionLineScore = createRegressionLine(featuresForTraining, targetsForTraining)

# draw the day's data into the plot and show it
def drawDayIntoThePlotAndShow(day, dayFeatures, dayTargets):
    dayRegressionLine, dayRegressionLineScore = createRegressionLine(dayFeatures, dayTargets)
    plot.scatter(featuresForTraining, targetsForTraining, color='0.8', label='training data')
    plot.plot(featuresForTraining, regressionLine, color='b', label=('trained regression line (' + str(regressionLineScore) + ')'))
    plot.scatter(dayFeatures, dayTargets, color='k', label='day data')
    plot.plot(dayFeatures, dayRegressionLine, color='r', label='current day regression line (' + str(dayRegressionLineScore) + ')')
    plot.xlabel('time in minutes')
    plot.ylabel('activity')
    plot.title('The Average Day in November vs day ' + str(day) + ' in December')
    plot.legend()
    plot.show()

# walk through each day in the testing dataset and draw the regression line
currentDayFeatures = None
currentDayTargets = None
currentDay = 0
for index, minutes in enumerate(featuresForTesting):
    day = int(int(minutes[0]) / int(24 * 60) + 1)
    if currentDay < day: # if we collected all data for a day (assume that the minutes are in ascending order)
        if currentDay > 0: # skip day zero
            currentDayFeatures = currentDayFeatures.reshape(-1, 1) # required by sklearn
            drawDayIntoThePlotAndShow(currentDay, currentDayFeatures, currentDayTargets)
        # prepare for the new day
        currentDay = day
        currentDayFeatures = np.array([])
        currentDayTargets = np.array([])
    # collect the day's data
    currentDayFeatures = np.append(currentDayFeatures, minutes[0] - (day - 1) * 24 * 60)
    currentDayTargets = np.append(currentDayTargets, targetsForTesting[index])
