'use strict'

const Database = use('Database')

class AnomalyDetectorController {

	*
	getDataForMap(request, response) {

		var squares = request.input('squares').split(',')
		var day = request.input('day')
		var hour = request.input('hour')
		var minute = request.input('minute')

		var minutes = parseInt(hour) * 60 + parseInt(minute)

		const squares_data = yield Database
			.select('square', 'mean_activity', 'actual_activity', 'standard_deviation')
			.from('squares')
			.whereIn('square', squares)
			.where('day', day)
			.where('minutes', minutes)

		response.send(squares_data)
	}

	*
	getDataForChart(request, response) {

		var square = request.input('square')
		var day = request.input('day')

		const square_data = yield Database
			.select('minutes', 'mean_activity', 'actual_activity', 'standard_deviation')
			.from('squares')
			.where('square', square)
			.where('day', day)

		response.send(square_data)
	}
}

module.exports = AnomalyDetectorController
