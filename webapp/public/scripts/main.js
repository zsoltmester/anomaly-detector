//
// **********
// Properties
// **********
//

var map
let areaInput = $('#areaInput')
var squares
var squareViews
var infoView

let daySelect = $('#daySelect')
let hourSelect = $('#hourSelect')
let minuteSelect = $('#minuteSelect')

let controlButton = $('#controlButton')
let infoText = $('#infoText')
var isSimulationRunning = false

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

    areaInput.prop('disabled', isSimulationRunning)
    daySelect.prop('disabled', isSimulationRunning)
    hourSelect.prop('disabled', isSimulationRunning)
    minuteSelect.prop('disabled', isSimulationRunning)

    if (isSimulationRunning) {
        startSimulation()
    } else {
        infoText.text('')
    }
}

function startSimulation() {

    infoText.text('Loading the map...')

    loadGeoJson(function(status, response) {

        if (status != '200') {
            onControlButtonClick()
            infoText.text('Couldn\'t load the squares.')
            return
        }

        if (!isSimulationRunning) {
            return
        }

        let geoJson = JSON.parse(response)
        let squareIds = parseSquareIdsFromAreaInput()
        parseSquaresFromGeoJson(geoJson, squareIds)
        updateSquareViews()

        downloadData()
    })
}

function continueSimulation() {

    if (!isSimulationRunning) {
        return
    }

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

        Promise.resolve(

                $.ajax({
                    url: '/detectanomaly',
                    method: 'GET',
                    data: {
                        'squares': squaresIds,
                        'day': daySelect.val(),
                        'hour': hourSelect.val(),
                        'minute': minuteSelect.val()
                    }
                })

            ).then(function(response) {

                if (!isSimulationRunning) {
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

                if (!isSimulationRunning) {
                    return
                }

                console.log('Error while accessing detectanomaly service: ')
                console.log(error)
                onControlButtonClick()
                infoText.text('Something unexpected happened.')
            })

    }.bind(this))
}

function calculateAnomalyProbability(squareData) {

    let difference = Math.abs(squareData.mean_activity - squareData.actual_activity)

    if (difference > 3 * squareData.standard_deviations) {
        return 1
    } else if (difference > 2 * squareData.standard_deviations) {
        return 0.75
    } else if (difference > squareData.standard_deviations) {
        return 0.5
    } else {
        return 0
    }
}

function waitForNextRound() {

    if (!(daySelect.val() == 31 && hourSelect.val() == 23 && minuteSelect.val() == 50)) {

        infoText.text('Waiting for the next pack of data...')
        setTimeout(continueSimulation, 5000)

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

function parseSquareIdsFromAreaInput() {

    var squareIds = []
    let input = areaInput.val().split(',')

    for (rawSquareId of input) {

        squareIds.push(parseInt(rawSquareId.trim()))
    }

    return squareIds
}

function onSquareViewClick(event, square) {

    var infoText = '<p>Square: ' + String(square.id) + '</p>'
    infoText += '<p>Time: day ' + String(daySelect.val()) + ', at ' + (String(hourSelect.val()) == '0' ? '00' : String(hourSelect.val())) + ':' + (String(minuteSelect.val()) == '0' ? '00' : String(minuteSelect.val())) + '</p><br/>'
    if (square.data) {
        infoText += '<p>Anomaly probability: ' + String(square.anomaly_probability) + '</p><br/>'
        infoText += '<p>Actual activity: ' + String(square.data.actual_activity) + '</p>'
        infoText += '<p>Mean activity in November: ' + String(square.data.mean_activity) + '</p>'
        infoText += '<p>Activity standard deviation in November: ' + String(square.data.standard_deviations) + '</p>'
    } else {
        infoText += '<p>No data available yet.</p>'
    }

    infoView.setContent(infoText)
    infoView.setPosition(event.latLng)
    infoView.open(map)
}
