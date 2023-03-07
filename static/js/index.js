// define with a global scope so setPinDic and initMap can both access it
let pinDic
let stations
// function to get the data from the html template
// converts the input to a string, then to a JSON object
function setPinDic(data) {
  pinDic = JSON.stringify(data)
  pinDic = JSON.parse(pinDic)
}

//Initialize and add the map
function initMap() {
  // The location Dublin
  const dublin = { lat: 53.3498, lng: -6.2603 };
  // The map, centered at Dublin
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 14,
    center: dublin,
  });

  // array to store the markers
  stations = [];

  for(let i in pinDic) {
    stations.push(new google.maps.Marker({position: pinDic[i], map: map}));

  // variable that stores the location of the bike stations icon
  var image = {
    url: "/static/icons/bike_icon.png",
    scaledSize: new google.maps.Size(20, 20)
  }};

  // looping through the pins and adding them to the map
  for(let i in pinDic) {
    const marker = new google.maps.Marker({
      position: pinDic[i], 
      map: map,
      icon: image});

    // create a new info window for the marker
    const infoWindow = new google.maps.InfoWindow({
      content: ''
    });

    // add mouseover and mouseout event listeners to the marker
    marker.addListener('mouseover', function() {
      // get the station information from the pinDic
      const station = pinDic[i];


      // create the content for the info window
      const content = '<div>' +
        '<h4>' + station.name + '</h4>' +
        '<h5>Estimated available Bikes: ' + station.available_bikes + '</h5>' +
        '<h5>Estimated available Spaces: ' + station.available_spaces + '</h5>' +
        '<h6>Station number: ' + station.available_spaces + '</h6>' +
        '</div>';

      // set the content of the info window and open it
      infoWindow.setContent(content);
      infoWindow.open(map, marker);
    });

    marker.addListener('mouseout', function() {
      // close the info window
      infoWindow.close();
    });

    // add the marker to the array
    stations.push(marker);
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

// create a button to hide the markers
const hideButton = document.getElementById("button-id");
hideButton.textContent = "Hide Markers";
hideButton.style.marginBottom = "10px";
hideButton.addEventListener("click", () => {
  // toggle the visibility of the markers
  stations.forEach(marker => {
    if(marker.getVisible()){
      marker.setVisible(false);
    } else {
      marker.setVisible(true);
    }
  });
});

window.initMap = initMap;