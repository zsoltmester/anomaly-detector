var map // eslint-disable-line
function initMap () { // eslint-disable-line
  map = new google.maps.Map(document.getElementById('map'), { // eslint-disable-line
    center: {lat: 45.465055, lng: 9.186954},
    zoom: 13
  })
  map.data.loadGeoJson('/assets/milano-grid.geojson')
}
