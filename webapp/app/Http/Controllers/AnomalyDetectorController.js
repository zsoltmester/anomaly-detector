'use strict'

class AnomalyDetectorController {

	*
	detectAnomaly(request, response) {

		var square = request.input('square')
		var day = request.input('day')
		var hour = request.input('hour')
		var minute = request.input('minute')

		console.log('square: ' + square);
		console.log('day: ' + day);
		console.log('hour: ' + hour);
		console.log('minute: ' + minute);

		var anomaly = Math.random()
		if (anomaly < 0.25) {
			anomaly = -1
		}

		response.send(anomaly)
	}
}

module.exports = AnomalyDetectorController
