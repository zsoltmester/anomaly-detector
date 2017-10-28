var map
function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 45.465055, lng: 9.186954},
        zoom: 13
    })
    // map.data.loadGeoJson('/assets/milano-grid.geojson')
}

//
// **********
// Properties
// **********
//

let areaInput = $('#areaInput')

let daySelect = $('#daySelect')
let hourSelect = $('#hourSelect')
let minuteSelect = $('#minuteSelect')

let fromDayText = $('#fromDayText')
let fromHourText = $('#fromHourText')
let fromMinuteText = $('#fromMinuteText')

let controlButton = $('#controlButton')
let infoText = $('#infoText')
let isSimulationRunning = false

//
// **************
// Initialization
// **************
//

// from and to date
daySelect.change(onToDateChanged)
hourSelect.change(onToDateChanged)
minuteSelect.change(onToDateChanged)
updateTheFromDate()

// control button
controlButton.click(onControlButtonClick)

//
// *********
// Functions
// *********
//

function onToDateChanged(event) {

    if (daySelect.val() == 1 && hourSelect.val() == 0 && minuteSelect.val() == 0) {
        minuteSelect.val(10)
    }

    updateTheFromDate();
}

function updateTheFromDate() {

    let minute = parseInt(minuteSelect.val()) - 10
    var hour = parseInt(hourSelect.val())
    var day = parseInt(daySelect.val())

    if (minute < 0) {

        minute = 50
        hour -= 1

        if (hour < 0) {

            hour = 23
            day -= 1
        }
    }

    if (minute == 0) {
        minute = '00'
    }

    fromMinuteText.text(minute)
    fromHourText.text(hour)
    fromDayText.text(day)
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
            infoText.text('Couldn\'t load the squares.')
            return
        }

        var geoJson = JSON.parse(response)
        processData()
    })
}

function continueSimulation() {

    incrementTheToDate()
    updateTheFromDate()
    processData()
}

function processData() {

    if (!isSimulationRunning) {
        return
    }

    infoText.text('Processing data...')
    setTimeout(waitForNextRound, 2500)
}

function waitForNextRound() {

    if (!isSimulationRunning) {
        return
    }

    if (!(daySelect.val() == 31 && hourSelect.val() == 23 && minuteSelect.val() == 50)) {

        infoText.text('Waiting for the next pack of data...')
        setTimeout(continueSimulation, 5000)

    } else {

        onControlButtonClick()
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
