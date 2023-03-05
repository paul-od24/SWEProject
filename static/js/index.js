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

function popWeatherCurrent(weatherDict) {
  let weather = '<th colspan="';
  weather += "2";
  weather += '">Current Weather</th>';
  weather += '<tr><td>';
  weather += weatherDict["symbol"];
  weather += '</td><td>';
  weather += weatherDict["rain"];
  weather += '</td></tr>';
  document.getElementById("weather_cur").innerHTML = weather;
  }

function popWeather48(weatherDict) {
  let weather = '<th colspan="';
  weather += "3";
  weather += '">Weather Next 48hrs</th>';
  let rows = [];
  for (let i = 0; i < 3; ++i) {
    rows[i] = '<tr>';
  }
  let i = 0;
  for (var key in weatherDict) {
    splitKey = key.split(' ');
    for (let j = 0; j < rows.length; ++j) {
      rows[j] += '<td>';
    }
    rows[0] += splitKey[1];
    rows[1] += weatherDict[key]['symbol'];
    rows[2] += weatherDict[key]['rain'];
    for (let j = 0; j < rows.length; ++j) {
      rows[j] += '</td>';
    }
    if (i >= 48) {
      break;
    }
    i++;
  }
  for (let j = 0; j < rows.length; ++j) {
    rows[j] += '</tr>';
  }
  for (let j = 0; j < rows.length; ++j) {
    weather += rows[j];
  }
  document.getElementById("weather_48").innerHTML = weather;
}

function popWeatherWeek(weatherDict) {
  let weather = '<th colspan="';
  weather += "4";
  weather += '">Weather Next Week</th>';
  let rows = [];
  for (let i = 0; i < 3; ++i) {
    rows[i] = '<tr>';
  }
  for (var key in weatherDict) {
    splitKey = key.split(' ');
    if (splitKey[1] == '12:00:00') {
      for (let j = 0; j < rows.length; ++j) {
        rows[j] += '<td>';
      }
      rows[0] += splitKey[0].split('-')[2];
      rows[1] += weatherDict[key]['symbol'];
      rows[2] += weatherDict[key]['rain'];
      for (let j = 0; j < rows.length; ++j) {
        rows[j] += '</td>';
      }
    }
  }
  for (let j = 0; j < rows.length; ++j) {
    rows[j] += '</tr>';
  }
  for (let j = 0; j < rows.length; ++j) {
    weather += rows[j];
  }
  document.getElementById("weather_week").innerHTML = weather;
}

window.initMap = initMap;