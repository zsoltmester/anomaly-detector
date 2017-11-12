'use strict'

const Database = use('Database')

class AnomalyDetectorController {

	*
	detectAnomaly(request, response) {

		var squares = request.input('squares').split(',')
		var day = request.input('day')
		var hour = request.input('hour')
		var minute = request.input('minute')

		var minutes = hour * 60 + minute

		const differences = yield Database
			.select('square', 'difference')
			.from('differences')
			.whereIn('square', squares)
			.where('day', day)
			.where('minutes', minutes)

		response.send(differences)
	}
}

module.exports = AnomalyDetectorController
