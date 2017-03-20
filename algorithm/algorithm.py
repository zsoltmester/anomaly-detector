# Amit ar algoritmus megvalósít:
# Egy négyzetet tud elemezni és annak indexét paraméterként kapja. Összeállít egy átlagos novemberi napot az adott négyzeten. Egy görbe, amit egy regresszor hoz létre, lesz az átlagos nap.
# - Végigmegy a training data összes napjának adott négyzetén és minden timestampre csinál egy targetet (nevezzük activitynek). Úgy hozza létre a activityt, hogy veszi az SMS in/out és call in/out adatok (tehát 4 különböző, de összehasonlítható) átlagát.
# - Kirajzolja ezeket az értékeket.

# TODO Hogyan kéne még fejleszteni a tranininget:
# - Használni az internet trafficot is, mint targetet (beleszámolni az activitybe, mint a többi adatot). Ehhez már kell a feature scaling, mert az internet traffic nem összehasonlítható a többivel.
# - Ahelyett, hogy az összes feture-t aggregáljuk (és lesz belőle az activity), minden feature-t külön kéne kezelni.
# - Kiszűrni a training databól az outlinerket, hisz egy átlagos napot akarunk megkapni.
# - Parameter optimizerel a paramétereit a modelnek a legjobbra lőni.
# - Az SVR helyett már regresszort is kipróbálni.

# TODO Hova tovább:
# - Tesztelni az egészet a decemberi adatokon-

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
parser.add_argument('-t','--training', help='Path to the root directory of the training data.', required=True)
parser.add_argument('-s','--square', type=int, help='The square to analyze.', required=True)
args = vars(parser.parse_args())
trainingFilesRoot = args['training']
square = args['square']

# list the training files
trainingFiles = []
for (dirPath, dirNames, fileNames) in walk(trainingFilesRoot):
    trainingFiles.extend([join(dirPath, fileName) for fileName in fileNames])
print('Training files:')
print('\n'.join(trainingFiles))

# walk through the files and read the data for the given square
start_time = time()
fieldNames=('square-id', 'time-interval', 'country-code', 'sms-in', 'sms-out', 'call-in', 'call-out', 'internet-traffic')
trainingData = []
for trainingFile in trainingFiles:
    with open(trainingFile) as tsvFile:
        tsvReader = DictReader(tsvFile, delimiter='\t', fieldnames=fieldNames)
        for row in tsvReader:
            if int(row['square-id']) == square:
                trainingData.append(row)
            elif int(row['square-id']) > square: # assume that the square id is increasing in each file
                break
print('Reading time:', round(time() - start_time, 3), ' sec')

# drop country code and the internet traffic and aggregate the rest
start_time = time()
cleanData = {}
for row in trainingData:
    if row['time-interval'] in cleanData:
        for key in cleanData[row['time-interval']]:
            cleanData[row['time-interval']][key] += float(row[key]) if row[key] != '' else float(0)
    else:
        cleanData[row['time-interval']] = {
            'sms-in' : float(row['sms-in']) if row['sms-in'] != '' else float(0),
            'sms-out' : float(row['sms-out']) if row['sms-out'] != '' else float(0),
            'call-in' : float(row['call-in']) if row['call-in'] != '' else float(0),
            'call-out' : float(row['call-out']) if row['call-out'] != '' else float(0)
        }
print('Cleaning time:', round(time() - start_time, 3), ' sec')

# collect the features and the targets in arrays. aggregate all the targets into one
start_time = time()
featuresForTraining = np.array([])
targetsForTraining = np.array([])
for timestamp, targets in cleanData.items():
    date = datetime.fromtimestamp(float(timestamp) / 1000.0)
    featuresForTraining = np.append(featuresForTraining, 60 * date.hour + date.minute)

    numOfValidData = float(0)
    for target in targets:
        if target != 0:
            numOfValidData += 1
    aggregatedTargets = (targets['sms-in'] + targets['sms-out'] + targets['call-in'] + targets['call-out']) / numOfValidData if numOfValidData != 0 else 0
    targetsForTraining = np.append(targetsForTraining, aggregatedTargets)

order = np.argsort(featuresForTraining)
featuresForTraining = np.array(featuresForTraining)[order]
targetsForTraining = np.array(targetsForTraining)[order]

featuresForTraining = featuresForTraining.reshape(-1, 1)

print('Aggregating time:', round(time() - start_time, 3), ' sec')
print('Targets: ', targetsForTraining)
print('Features: ', featuresForTraining)

# train the model
start_time = time()
model = SVR(kernel='rbf')
model = model.fit(featuresForTraining, targetsForTraining)
print('Training time:', round(time() - start_time, 3), ' sec')

# predict the model to the training data
start_time = time()
regressionLine = model.predict(featuresForTraining)
print('Prediction time:', round(time() - start_time, 3), ' sec')

# draw the training data
start_time = time()
plot.scatter(featuresForTraining, targetsForTraining, color='g', label='data')
plot.plot(featuresForTraining, regressionLine, color='r', label='regression line')
plot.xlabel('time in minutes')
plot.ylabel('activity')
plot.title('The Average Day in November')
plot.legend()
print('Drawing time:', round(time() - start_time, 3), ' sec')
plot.show()
