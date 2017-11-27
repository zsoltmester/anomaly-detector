//
// **********
// Properties
// **********
//

const COOKIE_ID_SELECTED_SQUARES_FOR_MAP = "selected_squares_for_map"
const COOKIE_ID_SELECTED_SQUARE_FOR_CHART = "selected_squares_for_chart"

const DEFAULT_SELECTED_SQUARES_ON_MAP = "5636,5637,5638,5736,5737,5738,5836,5837,5838"
const DEFAULT_SELECTED_SQUARE_ON_CHART = "5855"

//
// *********
// Functions
// *********
//

function getSelectedSquaresFromCookieForMap() {

	let selectedSquares = Cookies.get(COOKIE_ID_SELECTED_SQUARES_FOR_MAP)

	if (!selectedSquares) {
		selectedSquares = DEFAULT_SELECTED_SQUARES_ON_MAP
		Cookies.set(COOKIE_ID_SELECTED_SQUARES_FOR_MAP, selectedSquares, { expires: 365 })
	}

	return selectedSquares.split(',').map(Number)
}

function getSelectedSquareFromCookieForChart() {

	let selectedSquare = Cookies.get(COOKIE_ID_SELECTED_SQUARE_FOR_CHART)

	if (!selectedSquare) {
		selectedSquare = DEFAULT_SELECTED_SQUARE_ON_CHART
		Cookies.set(COOKIE_ID_SELECTED_SQUARE_FOR_CHART, selectedSquare, { expires: 365 })
	}

	return [parseInt(selectedSquare)]
}

function setSelectedSquaresToCookieForMap(squares) {

	Cookies.set(COOKIE_ID_SELECTED_SQUARES_FOR_MAP, squares.toString(), { expires: 365 })
}

function setSelectedSquareToCookieForChart(square) {

	Cookies.set(COOKIE_ID_SELECTED_SQUARE_FOR_CHART, square.toString(), { expires: 365 })
}
