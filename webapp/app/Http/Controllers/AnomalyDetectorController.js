'use strict'

const Database = use('Database')

class AnomalyDetectorController {

	*
	detectAnomaly(request, response) {

		var square = request.input('square')
		var day = request.input('day')
		var hour = request.input('hour')
		var minute = request.input('minute')

		var minutes = hour * 60 + minute

		const anomaly = yield Database
			.select('difference')
			.from('differences')
			.where('square', square)
			.where('day', day)
			.where('minutes', minutes)
			.limit(1)

		if (anomaly == null) {
			response.send(-1)
			return
		}

		response.send(anomaly[0].difference)
	}
}

module.exports = AnomalyDetectorController
