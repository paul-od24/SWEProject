// define with a global scope so setPinDic and initMap can both access it
let pinDic;
let avDic;
// object to store the markers
const stations = {};
const dublin = { lat: 53.3498, lng: -6.2603 };
let userloc;

// function to get the data from the html template
// converts the input to a string, then to a JSON object
function setPinDic(data) {
  pinDic = JSON.stringify(data)
  pinDic = JSON.parse(pinDic)
  for (let i in pinDic) {
    // add bike availability information to the pin dictionary
    pinDic[i]["available_bikes"] = avDic[i]["available_bikes"];
    pinDic[i]["available_bike_stands"] = avDic[i]["available_bike_stands"];
  }
}
// function to get availability data from the html template
// converts the input to a string, then to a JSON object
//function setAvDic(data) {
  //avDic = JSON.stringify(data)
  //avDic = JSON.parse(avDic)
//}


// Initialize and add the map
function initMap() {
  // The location Dublin
  // The map, centered at Dublin
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 14,
    center: dublin,
  });

  // Create an InfoWindow object
  const infowindow = new google.maps.InfoWindow();

  // looping through the pins and adding them to the map
  for (let i in pinDic) {
    const stationMarker = new google.maps.Marker({
      position: pinDic[i]["position"],
      map: map,
    });

    // Add an event listener to show the InfoWindow when you hover over the marker
google.maps.event.addListener(stationMarker, "mouseover", function () {
  infowindow.setContent(
    `<div><strong>${pinDic[i]["name"]} <br> Station Number:  ${i}</strong><br>Available Bikes: ${pinDic[i]["available_bikes"]}<br>Available Bike Stands: ${pinDic[i]["available_bike_stands"]}</div>`
  );
  infowindow.open(map, stationMarker);
});

    // Hide the InfoWindow when you move away from the marker
    google.maps.event.addListener(stationMarker, "mouseout", function () {
      infowindow.close();
    });

    console.log("Added marker for station " + pinDic[i]["number"]); // added for debugging
    stations[pinDic[i]["number"]] = stationMarker;
  }
  autocomplete()
}
// populate current weather table
function popWeatherCurrent(weatherDict) {
  // setup table head
  let weather = '<th colspan="';
  weather += "2";
  weather += '">Current Weather</th>';
  // add row
  weather += '<tr><td>';
  // add symbol to row
  weather += weatherDict["symbol"];
  weather += '</td><td>';
  // add rain to row
  weather += weatherDict["rain"];
  // end row
  weather += '</td></tr>';
  // insert table into html
  document.getElementById("weather_cur").innerHTML = weather;
  }

// populate next 48 hours weather table
function popWeather48(weatherDict) {
  // setup table head
  let weather = '<th colspan="';
  weather += "3";
  weather += '">Weather Next 48hrs</th>';
  // create array of table rows
  let rows = [];
  // begin each table row
  for (let i = 0; i < 3; ++i) {
    rows[i] = '<tr>';
  }
  // i tracks current hour
  let i = 0;
  // loop through each key in our weather dictionary
  for (var key in weatherDict) {
    // split the ket by ' '
    splitKey = key.split(' ');
    // add new cell to each row
    for (let j = 0; j < rows.length; ++j) {
      rows[j] += '<td>';
    }
    // add time to row 1
    rows[0] += splitKey[1];
    // add symbol to row 2
    rows[1] += weatherDict[key]['symbol'];
    // add rain data to row 3
    rows[2] += weatherDict[key]['rain'];
    // end cell in each row
    for (let j = 0; j < rows.length; ++j) {
      rows[j] += '</td>';
    }
    // exit loop if we have 48 hours
    if (i >= 48) {
      break;
    }
    i++;
  }
  // end each row and add to table
  for (let j = 0; j < rows.length; ++j) {
    rows[j] += '</tr>';
    weather += rows[j];
  }
  // insret table into html
  document.getElementById("weather_48").innerHTML = weather;
}

// populate next week weather table
function popWeatherWeek(weatherDict) {
  // setup table head
  let weather = '<th colspan="';
  weather += "4";
  weather += '">Weather Next Week</th>';
  // create array of table rows
  let rows = [];
  // begin each table row
  for (let i = 0; i < 3; ++i) {
    rows[i] = '<tr>';
  }
  // loop through each key in our weather dictionary
  for (var key in weatherDict) {
    // split the key by ' '
    splitKey = key.split(' ');
    // we take a snapshot of weather data at midday
    if (splitKey[1] == '12:00:00') {
      for (let j = 0; j < rows.length; ++j) {
        // add new cell to each row
        rows[j] += '<td>';
      }
      // add day to row 1
      rows[0] += splitKey[0].split('-')[2];
      // add symbol to row 2
      rows[1] += weatherDict[key]['symbol'];
      // add rain data to row 3
      rows[2] += weatherDict[key]['rain'];
      // end cell in each row
      for (let j = 0; j < rows.length; ++j) {
        rows[j] += '</td>';
      }
    }
  }
  // end each row and add to table
  for (let j = 0; j < rows.length; ++j) {
    rows[j] += '</tr>';
    weather += rows[j];
  }
  document.getElementById("weather_week").innerHTML = weather;
}

function autocomplete() {
    google.maps.event.addDomListener(window, 'load', initialize);
}

// adapted from https://developers.google.com/maps/documentation/javascript/place-autocomplete
function initialize() {
    let input = document.getElementById('autocomplete_search');
    const defaultBounds = {
    north: dublin.lat + 0.2,
    south: dublin.lat - 0.2,
    east: dublin.lng + 0.2,
    west: dublin.lng - 0.2,
    };
    const options = {
    bounds: defaultBounds,
    componentRestrictions: { country: "ie" },
    fields: ["address_components", "geometry", "icon", "name"],
    strictBounds: false,
  };

    const autocomplete = new google.maps.places.Autocomplete(input, options);
    autocomplete.addListener('place_changed', function () {
        let place = autocomplete.getPlace();
        userloc = JSON.stringify({"lat":place.geometry['location'].lat(), "lng": place.geometry['location'].lng()});
        document.getElementById("debug").innerHTML = userloc;
    });
}

function sendLoc() {
  fetch(`${window.origin}`, {
    method: "POST",
    credentials: "include",
    body: userloc,
    cache: "no-cache",
    headers: new Headers({
      "content-type": "application/json"
    })
  })
  .then((response) => response.json())
  .then((data) => showClosest(data));

}

function showClosest(data) {
  n = data["number"].toString()
  document.getElementById("debug").innerHTML = "Closest station: " + pinDic[n]["name"] + "<br>" + "Distance: " + data["distance"] + " metres";
}

window.initMap = initMap;