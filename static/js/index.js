// define with a global scope so setPinDic and initMap can both access it
let pinDic; // object to store the pin data
const stations = {}; // object to store the markers
const dublin = {lat: 53.3498, lng: -6.2603}; // the location Dublin
let userloc; // the user location
let markersVisible = true; // variable to toggle marker visibility
let directionsService;
let directionsRenderer;
let autocomplete;

// function to get the data from the html template
// converts the input to a string, then to a JSON object
function setPinDic(data) {
    pinDic = JSON.stringify(data);
    pinDic = JSON.parse(pinDic);
}

// Initialize and add the map
function initMap() {
    // The map, centered at Dublin
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 14,
        center: dublin,
    });

    // set date time
    setDateTime();
    // setting up routing
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map);

    // Create an InfoWindow object
    const infowindow = new google.maps.InfoWindow();


    // variable that stores the location of the bike stations icon
    var image = {
        url: "/static/icons/bike_icon.png",
        scaledSize: new google.maps.Size(20, 20)
    };

    // looping through the pins and adding them to the map
    for (let i in pinDic) {
        const stationMarker = new google.maps.Marker({
            position: pinDic[i]["position"],
            map: map,
            icon: image
        });

        // Add an event listener to show the InfoWindow when you hover over the marker
        google.maps.event.addListener(stationMarker, "mouseover", function () {
            infowindow.setContent(
                `<div class="info-window"><h3>${pinDic[i]["name"]}</h3><p>Station Number: ${i}</p><p>Available Bikes: ${pinDic[i]["available_bikes"]}</p><p>Available Bike Stands: ${pinDic[i]["available_bike_stands"]}</p></div>`
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
    // call the autocomplete function
    autocomplete_init();
}

// populate current weather table
function popWeatherCurrent(weather) {
    // Get a reference to the current weather div
    var currentWeatherDiv = document.getElementById("weather_cur");
    
    // Create a header element for the current weather
    var currentWeatherHeader = document.createElement("h2");
    currentWeatherHeader.innerText = "Current Weather";
    currentWeatherDiv.appendChild(currentWeatherHeader);
    
    // Create a paragraph element for the weather data
    var currentWeatherData = document.createElement("p");
    
    // Create an image element for the weather icon
    var weatherIcon = document.createElement("img");
    
    // Set the src attribute of the weather icon based on the weather symbol
switch (weather.symbol) {
    case "Cloud":
        weatherIcon.src = "static/icons/cloudy.png";
        break;
    case "Sun":
        weatherIcon.src = "static/icons/sunny.png";
        break;
    case "PartlyCloud":
        weatherIcon.src = "static/icons/partlycloudy.png";
        break;
    case "DrizzleSun":
        weatherIcon.src = "static/icons/drizzlesun.png";
        break;
    case "Rain":
        weatherIcon.src = "static/icons/rain.png";
        break;
    case "Drizzle":
        weatherIcon.src = "static/icons/drizzle.png";
        break;
    case "LightRain":
        weatherIcon.src = "static/icons/lightrain.png";
        break;
    // Add more cases for each weather symbol and corresponding icon
    default:
        weatherIcon.src = "static/icons/default.png"; // A default icon to use if the symbol is not recognized
        break;
}
    
    // Add the weather icon to the paragraph element
    currentWeatherData.appendChild(weatherIcon);
    
    // Add precipitation and temperature data to the paragraph element
  currentWeatherData.innerHTML+= "<br><span style='font-size:25px; font-weight:bold;'>Temperature:</span> " + weather.temp + "°C 🔆<br>" +
  "<span style='font-size:25px; font-weight:bold;'>Precipitation:</span> " + weather.rain + "mm ☔";

    
    // Add the weather data to the current weather div
    currentWeatherDiv.appendChild(currentWeatherData);
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

function autocomplete_init() {
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
        componentRestrictions: {country: "ie"},
        fields: ["address_components", "geometry", "icon", "name"],
        strictBounds: false,
    };

    autocomplete = new google.maps.places.Autocomplete(input, options);
    autocomplete.addListener('place_changed', function () {
        let place = autocomplete.getPlace();
        userloc = {"lat": place.geometry['location'].lat(), "lng": place.geometry['location'].lng()};
    });
}

function currentLoc() {
    return new Promise((resolve) => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    userloc = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                    }
                    resolve(userloc)
                    // get the input element
                    const input = document.getElementById("autocomplete_search");
                    // set the value of the input field to the current latitude and longitude
                    input.value = `${userloc.lat},${userloc.lng}`;
                })
        }
    });
}

// function gets the current location of the user and populates the search bar with the formatted address of that location.
function getCurrentLocation() {
    currentLoc().then((location) => {
      var geocoder = new google.maps.Geocoder();
      geocoder.geocode({
        location: new google.maps.LatLng(location.lat, location.lng)
      }, function (results, status) {
        if (status == "OK") {
          autocomplete.setFields(["address_component", "geometry"]);
          autocomplete.setBounds(results[0].geometry.viewport);
          document.getElementById("autocomplete_search").value =
            results[0].formatted_address;
        } else {
        // if the geocoder fails, log an error message to the console
          console.log("Geocode was not successful for the following reason: " + status);
        }
      });
    });
  }

// function using POST request to send selected location to backend. Backend responds with closest station.
async function sendLoc() {
    fetch(`${window.origin}`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(userloc),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
        .then((response) => response.json())
        .then((data) => showClosest(data));
}

// function to find route distances
function findRoute(origin, dest) {
    return new Promise((resolve, reject) => {
        let mode = document.getElementById("mode").value;
        let req = {
            origin: origin,
            destination: dest,
            travelMode: mode,
        };

        directionsService.route(req, function (res, status) {
            if (status === "OK") {
                let dist = res.routes[0].legs[0].distance.value;
                resolve(dist);
            } else {
                reject("Error getting route:", status);
            }
        });
    });
}

// function to show the closest station based on route distance
async function showClosest(data) {
    let min_dist = {number: "0", distance: -1};
    let final_dest;
    let dist;

    for (let i in data) {
        let n = i.toString();
        let dest = {
            lat: pinDic[n]["position"]["lat"],
            lng: pinDic[n]["position"]["lng"],
        };

        try {
            dist = await findRoute(userloc, dest);

            if (min_dist["distance"] === -1 || dist < min_dist["distance"]) {
                min_dist["number"] = n;
                min_dist["distance"] = dist;
                final_dest = dest;
            }
        } catch (error) {
            console.error(error);
        }
    }

    let n = min_dist["number"];
    document.getElementById("stationInfo").innerHTML =
        "Closest station: " + pinDic[n]["name"];
    let stationInfo = pinDic[n]["name"] + " <br>Station Number: " + pinDic[n]["number"] + ", <br>Available Bikes: " + pinDic[n]["available_bikes"] + ", <br>Available Bike Stands: " + pinDic[n]["available_bike_stands"];
    document.getElementById("stationInfo").innerHTML = "Closest station: " + stationInfo;
    showRoute(userloc, final_dest);
}

// function to actually display the route on the map
function showRoute(origin, dest) {
    let dist
    let dur
    let mode = document.getElementById('mode').value;
    let req = {
        origin: origin,
        destination: dest,
        travelMode: mode,
    };

    directionsService.route(req, function (res, status) {
        if (status === 'OK') {
            directionsRenderer.setDirections(res);
            dist = res.routes[0].legs[0].distance.text;
            dur = res.routes[0].legs[0].duration.text;

            document.getElementById("stationDuration").innerHTML = "Distance: " + dist + "<br>" + "Duration: " + dur;

        } else {
            console.error('Error getting route:', status);
        }
    });
}
function setDateTime() {
    const now = new Date();
    const dateTimeInput = document.getElementById("datetime");
    dateTimeInput.value = now.toISOString().slice(0, 16);
  }

const dateTime = document.getElementById("datetime");

// Get the value of the selected date and time
dateTime.addEventListener("change", function () {
    const selectedDateTime = dateTime.value;
    console.log(selectedDateTime);
});

window.initMap = initMap;