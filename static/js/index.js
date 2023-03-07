// define with a global scope so setPinDic and initMap can both access it
let pinDic

// function to get the data from the html template
// converts the input to a string, then to a JSON object
function setPinDic(data) {
  pinDic = JSON.stringify(data)
  pinDic = JSON.parse(pinDic)
}

// Initialize and add the map
function initMap() {
  // The location Dublin
  const dublin = { lat: 53.3498, lng: -6.2603 };
  // The map, centered at Dublin
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 14,
    center: dublin,
  });

  // array to store the markers
  const stations = [];

  // looping through the pins and adding them to the map
  for(let i in pinDic) {
    stations.push(new google.maps.Marker({position: pinDic[i], map: map,}));
  }
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

window.initMap = initMap;