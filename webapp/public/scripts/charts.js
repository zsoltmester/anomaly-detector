//
// **********
// Properties
// **********
//

let chartView = $("#chartView")
var chart

let squareInput = $('#squareInput')
let daySelect = $('#daySelect')

let showButton = $('#showButton')
let infoText = $('#infoText')

var currentDownloadNumber = 0

//
// **************
// Initialization
// **************
//

showButton.click(onShowButtonClick)
onShowButtonClick()

//
// *********
// Functions
// *********
//

function onShowButtonClick() {

    currentDownloadNumber++
	downloadData()
}


function downloadData() {

	infoText.text('Processing data...')

	let savedDownloadNumber = currentDownloadNumber

	co(function*() {

		Promise.resolve(

				$.ajax({
					url: '/getdataforchart',
					method: 'GET',
					data: {
						'square': squareInput.val(),
						'day': daySelect.val()
					}
				})

			).then(function(response) {

	            if (savedDownloadNumber !== currentDownloadNumber) {
                    return
                }

				infoText.text('')
				initChart(response)

			})

			.catch(function(error) {

	            if (savedDownloadNumber !== currentDownloadNumber) {
                    return
                }

				console.log('Error while accessing getdataforchart service: ')
				console.log(error)
				infoText.text('Something unexpected happened.')
			})

	}.bind(this))
}

function initChart(data) {

	data = data.reduce(function(map, object) {
	    map[object.minutes] = {
			'meanActivity' : object.mean_activity,
			'actualActivity' : object.actual_activity,
			'standardDeviation' : object.standard_deviation,
		}
	    return map
	}, {})

	let minutes = Object.keys(data).sort(function(a, b) {
		return a - b
	})

	let meanActivities = []
	let meanActivitiesPlusStandardDeviations = []
	let meanActivitiesMinusStandardDeviations = []
	let actualActivities = []
	for (minute of minutes) {
		meanActivities.push(data[minute].meanActivity)
		meanActivitiesPlusStandardDeviations.push(data[minute].meanActivity + data[minute].standardDeviation)
		meanActivitiesMinusStandardDeviations.push(data[minute].meanActivity - data[minute].standardDeviation)
		actualActivities.push(data[minute].actualActivity)
	}

	if (chart) {
		chart.destroy()
	}

	chart = new Chart(chartView, {

		type: 'line',

	    data: {
	        labels: minutes,
	        datasets: [{
	            label: "Mean activity in November",
	            backgroundColor: 'rgb(0, 0, 0)',
	            borderColor: 'rgb(0, 0, 0)',
	            data: meanActivities,
				fill: false
	        }, {
	            label: "Mean activity, plus its standard deviation in November",
	            backgroundColor: 'rgb(128, 128, 128)',
	            borderColor: 'rgb(128, 128, 128)',
	            data: meanActivitiesPlusStandardDeviations,
				fill: false
	        }, {
	            label: "Mean activity, minus its standard deviation in November",
	            backgroundColor: 'rgb(128, 128, 128)',
	            borderColor: 'rgb(128, 128, 128)',
	            data: meanActivitiesMinusStandardDeviations,
				fill: false,
				hidden: true
	        }, {
	            label: "Actual activity",
	            backgroundColor: 'rgb(255, 0, 0)',
	            borderColor: 'rgb(255, 0, 0)',
	            data: actualActivities,
				fill: false
	        }]
	    },

	    options: {
			tooltips: {
	            mode: 'index',
				intersect: false
	        }
		}
	});
}
