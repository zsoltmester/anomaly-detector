//
// **********
// Properties
// **********
//

var map
var squares
var squareViews
var infoView

let daySelect = $('#daySelect')
let hourSelect = $('#hourSelect')
let minuteSelect = $('#minuteSelect')

let controlButton = $('#controlButton')
let infoText = $('#infoText')
var isSimulationRunning = false
var currentSessionNumber = 0

//
// **************
// Initialization
// **************
//

// from and to date
daySelect.change(onToDateChanged)
hourSelect.change(onToDateChanged)
minuteSelect.change(onToDateChanged)

// control button
controlButton.click(onControlButtonClick)

//
// *********
// Functions
// *********
//

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 45.47771, lng: 9.115242},
        zoom: 16
    })
    infoView = new google.maps.InfoWindow
}

function onToDateChanged(event) {

    if (daySelect.val() == 1 && hourSelect.val() == 0 && minuteSelect.val() == 0) {
        minuteSelect.val(10)
    }
}

function incrementTheToDate() {

    let minute = parseInt(minuteSelect.val()) + 10
    var hour = parseInt(hourSelect.val())
    var day = parseInt(daySelect.val())

    if (minute > 50) {

        minute = 0
        hour += 1

        if (hour > 23) {

            hour = 0
            day += 1
        }
    }

    minuteSelect.val(minute)
    hourSelect.val(hour)
    daySelect.val(day)
}

function onControlButtonClick() {

    var classToRemove = isSimulationRunning ? 'btn-danger' : 'btn-success'
    var classToAdd = isSimulationRunning ? 'btn-success' : 'btn-danger'
    var label = isSimulationRunning ? 'Run' : 'Stop'

    controlButton.removeClass(classToRemove)
    controlButton.addClass(classToAdd)
    controlButton.text(label)

    isSimulationRunning = !isSimulationRunning

    daySelect.prop('disabled', isSimulationRunning)
    hourSelect.prop('disabled', isSimulationRunning)
    minuteSelect.prop('disabled', isSimulationRunning)

    if (isSimulationRunning) {
        currentSessionNumber++
        startSimulation()
    } else {
        infoText.text('')
    }
}

function startSimulation() {

    infoText.text('Loading the map...')

    let savedSessionNumber = currentSessionNumber

    loadGeoJson(function(status, response) {

        if (status != '200') {
            onControlButtonClick()
            infoText.text('Couldn\'t load the squares.')
            return
        }

        if (!isSimulationRunning || currentSessionNumber !== savedSessionNumber) {
            return
        }

        let geoJson = JSON.parse(response)
        let squareIds = getSelectedSquaresFromCookieForMap()
        parseSquaresFromGeoJson(geoJson, squareIds)
        updateSquareViews()

        downloadData()
    })
}

function continueSimulation() {

    incrementTheToDate()
    downloadData()
}

function downloadData() {

    infoText.text('Processing data...')

    for (square of squares) {

        square.data = null
        square.anomaly_probability = null
    }

    updateSquareViews()

    var squaresIds = ""

    for (square of squares) {

        if (squaresIds.length > 0) {
            squaresIds += ","
        }

        squaresIds += String(square.id)
    }

    co(function*() {

        let savedSessionNumber = currentSessionNumber

        Promise.resolve(

                $.ajax({
                    url: '/getdataformap',
                    method: 'GET',
                    data: {
                        'squares': squaresIds,
                        'day': daySelect.val(),
                        'hour': hourSelect.val(),
                        'minute': minuteSelect.val()
                    }
                })

            ).then(function(response) {

                if (!isSimulationRunning || savedSessionNumber !== currentSessionNumber) {
                    return
                }

                for (squareData of response) {

                    for (square of squares) {

                        if (square.id == parseInt(squareData.square)) {

                            square.data = squareData
                            square.anomaly_probability = calculateAnomalyProbability(squareData)
                        }
                    }
                }

                updateSquareViews()
                waitForNextRound()

            })

            .catch(function(error) {

                let savedSessionNumber = currentSessionNumber

                if (!isSimulationRunning || savedSessionNumber !== currentSessionNumber) {
                    return
                }

                console.log('Error while accessing getdataformap service: ')
                console.log(error)
                onControlButtonClick()
                infoText.text('Something unexpected happened.')
            })

    }.bind(this))
}

function calculateAnomalyProbability(squareData) {

    return Math.abs(squareData.mean_activity - squareData.actual_activity) / (2 * squareData.standard_deviation)
}

function waitForNextRound() {

    if (!(daySelect.val() == 31 && hourSelect.val() == 23 && minuteSelect.val() == 50)) {

        infoText.text('Waiting for the next pack of data...')

        let savedSessionNumber = currentSessionNumber

        setTimeout(function() {

            if (!isSimulationRunning || savedSessionNumber !== currentSessionNumber) {
                return
            }

            continueSimulation()
        }, 5000)

    } else {

        onControlButtonClick()
        infoText.text('No more data available')
    }
}

function loadGeoJson(callback) {

    var request = new XMLHttpRequest()
    request.overrideMimeType('application/json')
    request.open('GET', '/assets/milano-grid.geojson', true)

    request.onreadystatechange = function () {

        if (request.readyState == 4) {
            callback(request.status, request.responseText)
        }
    }

    request.send(null)
}

function parseSquaresFromGeoJson(geoJson, squareIds) {

    squares = []

    for (squareId of squareIds) {

        var squareCoordinates = []

        for (let squareCoordinate of geoJson.features[parseInt(squareId) - 1].geometry.coordinates[0]) {

            squareCoordinates.push({lat: squareCoordinate[1], lng: squareCoordinate[0]})
        }

        squares.push({id: squareId, coordinates: squareCoordinates, anomaly_probability: null, data: null})
    }
}

function updateSquareViews() {

    infoView.setMap(null)
    removeSquareViews()
    createSquareViewsFromSquares()
    displaySquareViews()
}

function createSquareViewsFromSquares() {

    squareViews = []

    for (square of squares) {

        let squareView = new google.maps.Polygon({
          paths: square.coordinates,
          strokeColor: square.anomaly_probability ? '#FF0000' : '#FFFFFF',
          strokeOpacity: 0.75,
          strokeWeight: 2,
          fillColor: square.anomaly_probability ? '#FF0000' : '#FFFFFF',
          fillOpacity: square.anomaly_probability ? square.anomaly_probability : 0.5
        })

        let clickedSquare = square

        squareView.addListener('click', function (event) {

            onSquareViewClick(event, clickedSquare)
        })

        squareViews.push(squareView)
    }
}

function displaySquareViews() {

    if (!$.isArray(squareViews)) {

        return
    }

    for (squareView of squareViews) {

        squareView.setMap(map)
    }
}

function removeSquareViews() {

    if (!$.isArray(squareViews)) {

        return
    }

    for (squareView of squareViews) {

        squareView.setMap(null)
    }
}

function onSquareViewClick(event, square) {

    var infoText = '<p>Square: ' + String(square.id) + '</p>'
    infoText += '<p>Time: day ' + String(daySelect.val()) + ', at ' + (String(hourSelect.val()) == '0' ? '00' : String(hourSelect.val())) + ':' + (String(minuteSelect.val()) == '0' ? '00' : String(minuteSelect.val())) + '</p><br/>'
    if (square.data) {
        infoText += '<p>Anomaly probability: ' + String(square.anomaly_probability) + '</p><br/>'
        infoText += '<p>Actual activity: ' + String(square.data.actual_activity) + '</p>'
        infoText += '<p>Mean activity in November: ' + String(square.data.mean_activity) + '</p>'
        infoText += '<p>Activity standard deviation in November: ' + String(square.data.standard_deviation) + '</p>'
    } else {
        infoText += '<p>No data available yet.</p>'
    }

    infoView.setContent(infoText)
    infoView.setPosition(event.latLng)
    infoView.open(map)
}
