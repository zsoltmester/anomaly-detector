var map // eslint-disable-line
function initMap () { // eslint-disable-line
  map = new google.maps.Map(document.getElementById('map'), { // eslint-disable-line
    center: {lat: 45.465055, lng: 9.186954},
    zoom: 13
  })
  //map.data.loadGeoJson('/assets/milano-grid.geojson')
}

let dayInMilliseconds = 86400000
let startDateInMilliseconds = 1385856000000
var dateFormatter = function (value) {
  let day = $('#select').find(":selected").val()
  let valueInMilliseconds = value * 10 * 60 * 1000
  let date = new Date(startDateInMilliseconds + valueInMilliseconds + (day - 1) * dayInMilliseconds)
  return date.toUTCString()
}

$('#slider').slider({
  formatter: dateFormatter,
  id: "slider",
  max: 143,
  min: 0,
  range: true,
	tooltip_position:'bottom',
  tooltip_split: true,
  value: [62, 82],
});

$("#slider").on("slideStop", function(event) {
	console.log(event.value)
  // TODO call far the values
});
