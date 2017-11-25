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

		const square_data = yield Database
			.select('square', 'mean_activity', 'actual_activity', 'standard_deviations')
			.from('squares')
			.whereIn('square', squares)
			.where('day', day)
			.where('minutes', minutes)

		response.send(square_data)
	}
}

module.exports = AnomalyDetectorController
