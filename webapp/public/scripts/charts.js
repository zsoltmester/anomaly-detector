var chartView = $("#chart");
var chart = new Chart(chartView, {
    // The type of chart we want to create
    type: 'line',

    // The data for our dataset
    data: {
        labels: ["January", "February", "March", "April", "May", "June", "July"],
        datasets: [{
            label: "My First dataset",
            backgroundColor: 'rgb(255, 99, 132)',
            borderColor: 'rgb(255, 99, 132)',
            data: [0, 10, 5, 2, 20, 30, 45],
        }]
    },

    // Configuration options go here
    options: {}
});

co(function*() {

	Promise.resolve(

			$.ajax({
				url: '/getdataforchart',
				method: 'GET',
				data: {
					'square': '1',
					'day': '1'
				}
			})

		).then(function(response) {

			console.log(response)

		})

		.catch(function(error) {

			console.log('Error while accessing getdataforchart service: ')
			console.log(error)
			onControlButtonClick()
			infoText.text('Something unexpected happened.')
		})

}.bind(this))
