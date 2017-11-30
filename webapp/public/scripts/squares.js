//
// **********
// Properties
// **********
//

var map

var squares

var parent
var selectedSquares

//
// **************
// Initialization
// **************
//

parent = $('#parent').text()
selectedSquares = parent == 'map' ? getSelectedSquaresFromCookieForMap() : getSelectedSquareFromCookieForChart()

//
// *********
// Functions
// *********
//

function initMap() {

	map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 45.461895, lng: 9.159832},
        zoom: 12,
        streetViewControl: false,
		fullscreenControl: false
    })

	loadGeoJson(function(status, response) {

		if (status != '200') {
			return
		}

		let geoJson = JSON.parse(response)
		parseSquaresFromGeoJson(geoJson)

		updateSquareViews()
	})
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

function parseSquaresFromGeoJson(geoJson) {

    squares = []

	for (var squareId = 1; squareId <= 10000; squareId++) {

		var squareCoordinates = []

		for (let squareCoordinate of geoJson.features[parseInt(squareId) - 1].geometry.coordinates[0]) {

			squareCoordinates.push({lat: squareCoordinate[1], lng: squareCoordinate[0]})
		}

		squares.push({id: squareId, coordinates: squareCoordinates})
	}
}

function updateSquareViews() {

    createSquareViewsFromSquares()
    displaySquareViews()
}

function createSquareViewsFromSquares() {

    squareViews = []

    for (square of squares) {

        let squareView = createSquareView(square)
        squareViews.push(squareView)
    }
}

function createSquareView(square) {

	let isSelected = selectedSquares.indexOf(square.id) > -1

	let squareView = new google.maps.Polygon({
	  paths: square.coordinates,
	  strokeColor: '#000000',
	  strokeOpacity: 0.75,
	  strokeWeight: 2,
	  fillColor: isSelected ? '#ff0000' : '#000000',
	  fillOpacity: 0.5
	})

	let clickedSquare = square

	squareView.addListener('click', function (event) {

		onSquareViewClick(event, clickedSquare)
	})

	return squareView
}

function displaySquareViews() {

    for (squareView of squareViews) {

        squareView.setMap(map)
    }
}

function onSquareViewClick(event, square) {

	if (parent == 'map') {
		handleSelectionForMap(square)
	} else {
		handleSelectionForChart(square)
	}
}

function handleSelectionForMap(square) {

	let isSelected = selectedSquares.indexOf(square.id) > -1

	if (isSelected) {
		if (selectedSquares.length > 1) {
			selectedSquares.splice(selectedSquares.indexOf(square.id), 1);
			squareViews[square.id - 1].setOptions({fillColor: '#000000'})
		}
	} else {
		selectedSquares.push(square.id)
		squareViews[square.id - 1].setOptions({fillColor: '#ff0000'})
	}

	setSelectedSquaresToCookieForMap(selectedSquares)
}

function handleSelectionForChart(square) {

	let isSelected = selectedSquares.indexOf(square.id) > -1

	if (!isSelected) {
		squareViews[selectedSquares[0] - 1].setOptions({fillColor: '#000000'})
		squareViews[square.id - 1].setOptions({fillColor: '#ff0000'})
		selectedSquares = [square.id]
	}

	setSelectedSquareToCookieForChart(selectedSquares)
}
