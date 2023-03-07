let pinDic;
// object to store the markers
const stations = {};

// function to get the data from the html template
// converts the input to a string, then to a JSON object
function setPinDic(data) {
  pinDic = JSON.parse(JSON.stringify(data));
  // Add station information to pinDic object
  for (let i in pinDic) {
    const station = pinDic[i];
    station.name = station.address.split(',')[0];
    station.available_bikes = station.available_bikes || 0;
    station.available_bike_stands = station.available_bike_stands || 0;
    station.number = station.number || i;
  }
  
  // toggle markers on button click
  const toggleBtn = document.getElementById("toggleBtn");
  toggleBtn.addEventListener("click", toggleMarkers);
}

function initMap() {
  // The location Dublin
  const dublin = { lat: 53.3498, lng: -6.2603 };
  // The map, centered at Dublin
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 14,
    center: dublin,
  });

  // looping through the pins and adding them to the map
  for(let i in pinDic) {
    const station = pinDic[i];
    const marker = new google.maps.Marker({
      position: station.position,
      map: map,
      title: station.name,
      visible: true, // add a property to track visibility state
    });

    // create the content of the info window
    const content = `
      <div>
        <p><b>${station.name}</b></p>
        <p>Available bikes: ${station.available_bikes}</p>
        <p>Available bike stands: ${station.available_bike_stands}</p>
        <p>Station number: ${station.number}</p>
      </div>
    `;

    // create the info window with the content
    const infowindow = new google.maps.InfoWindow({
      content: content,
    });

    // add the event listeners to the marker
    marker.addListener('mouseover', () => {
      infowindow.open(map, marker);
    });

    marker.addListener('mouseout', () => {
      infowindow.close();
    });

    // add marker to stations object with station number as key
    stations[station.number] = marker;
  }
  
  // toggle markers on button click
  const toggleBtn = document.getElementById("toggleBtn");
  toggleBtn.addEventListener("click", toggleMarkers);
}

function toggleMarkers() {
  // loop through all markers and toggle their visibility
  for(let i in stations) {
    const station = stations[i];
    const marker = station.marker;
    const visible = !station.visible;
    marker.setVisible(visible);
    // update the visibility state in the stations object
    stations[i].visible = visible;
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