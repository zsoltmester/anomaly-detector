var map
function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 45.465055, lng: 9.186954},
        zoom: 13
    })
    // map.data.loadGeoJson('/assets/milano-grid.geojson')
}

//
// Properties
//

let daySelect = $("#daySelect")
let hourSelect = $("#hourSelect")
let minuteSelect = $("#minuteSelect")

let fromDayText = $("#fromDayText")
let fromHourText = $("#fromHourText")
let fromMinuteText = $("#fromMinuteText")

//
// Initialization
//

daySelect.change(onToDateChanged);
hourSelect.change(onToDateChanged);
minuteSelect.change(onToDateChanged);

updateTheFromDate()

//
// Functions
//

function onToDateChanged(event) {

    if (daySelect.val() == 1 && hourSelect.val() == 0 && minuteSelect.val() == 0) {
        minuteSelect.val(10)
    }

    updateTheFromDate();
}

function updateTheFromDate() {

    let minute = minuteSelect.val() - 10
    var hour = hourSelect.val()
    var day = daySelect.val()

    if (minute < 0) {

        minute = 50
        hour = hourSelect.val() - 1

        if (hour < 0) {

            hour = 23
            day = daySelect.val() - 1
        }
    }

    if (minute == 0) {
        minute = "00"
    }

    fromMinuteText.text(minute)
    fromHourText.text(hour)
    fromDayText.text(day)
}
