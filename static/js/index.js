// define with a global scope so setPinDic and initMap can both access it
let pinDic; // object to store the pin data
const stations = {}; // object to store the markers
const dublin = {lat: 53.3498, lng: -6.2603}; // the location Dublin
let userloc; // the user location
let markersVisible = true; // variable to toggle marker visibility
let directionsService;
let directionsRenderer;
let autocomplete;
let originMarker;

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
    currentWeatherData.innerHTML += "<br><span style='font-size:25px; font-weight:bold;'>Temperature:</span> " + weather.temp + "°C 🔆<br>" +
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

// function using POST request to send selected location to backend. Backend responds with 10 closest stations.
async function sendLoc() {
    let data = {
        "pinDic": pinDic,
        "userloc": userloc
    }
    fetch(`${window.origin}`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(data),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
        .then((response) => response.json())
        .then(async (data) => {
            const routeFinder = new RouteFinder(userloc, data, pinDic);
            await routeFinder.updateRouteInfo();
            displayStations(routeFinder);
        });
}

// class storing stations that will be displayed to the user
class Station {
    constructor(stationNumber, stationName, bikes, stands, dist, dur, position) {
        this.stationNumber = stationNumber;
        this.stationName = stationName;
        this.bikes = bikes;
        this.stands = stands;
        this.dist = dist;
        this.duration = dur;
        this.position = position;
    }
}

// class storing functionality needed to get all necessary info relating to stations
class RouteFinder {
    constructor(userloc, data, pinDic) {
        this.userloc = userloc;
        this.stations = Object.entries(data).map(([key, value]) => {
            let position = pinDic[key].position;
            let stationName = pinDic[key].name;
            return new Station(parseInt(key), stationName, value.bikes, value.stands, value.dist, 0, position);
        });
    }

    // function to get route distances & durations
    async getRouteInfo() {
        return new Promise((resolve, reject) => {
            let mode = document.getElementById("mode").value;
            // storing the destination coordinates in an array
            let destinations = this.stations.map(station => {
                return new google.maps.LatLng(station.position.lat, station.position.lng);
            });
            // storing the coordinates of the user's location in an array (1 element only)
            let origins = [new google.maps.LatLng(this.userloc.lat, this.userloc.lng)]

            let req = {
                origins: origins,
                destinations: destinations,
                travelMode: mode
            };

            // sending request to distance matrix API
            let distanceMatrixService = new google.maps.DistanceMatrixService();
            distanceMatrixService.getDistanceMatrix(req, function (res, status) {
                if (status === "OK") {
                    // getting distance and duration values in response
                    let routeInfo = res.rows[0].elements.map(row => ({
                        distance: row.distance.value,
                        duration: row.duration.value
                    }));
                    resolve(routeInfo);
                } else {
                    reject("Error getting route:", status);
                }
            });
        });
    }

    // function to update the info related to the route for each station
    async updateRouteInfo() {
        const routeInfoArray = await this.getRouteInfo();

        this.stations.forEach((station, index) => {
            station.dist = routeInfoArray[index].distance;
            station.duration = routeInfoArray[index].duration;
        });
    }

    // function to show the selected route on the map
    async showRoute(destIndex) {
        let stationNumber = this.stations[destIndex].stationNumber;
        let dest = new google.maps.LatLng(this.stations[destIndex].position.lat, this.stations[destIndex].position.lng);
        let mode = document.getElementById('mode').value;
        let req = {
            origin: this.userloc,
            destination: dest,
            travelMode: mode,
        };

        // sending the request to the directionService API
        directionsService.route(req, (res, status) => {
            if (status === 'OK') {
                // hiding default markers
                directionsRenderer.setOptions({
                    suppressMarkers: true
                });
                // displaying the route on the map
                directionsRenderer.setDirections(res);
                // calling function to display custom origin marker
                this.updateOriginMarker(res);
            } else {
                console.error('Error getting route:', status);
            }
        });
    }

    // function to display custom origin marker
    async updateOriginMarker(res) {
        // remove previous origin marker, if present
        if (originMarker) {
            originMarker.setMap(null);
        }

        // display new marker
        let originLatLng = res.routes[0].legs[0].start_location;
        originMarker = new google.maps.Marker({
            position: originLatLng,
            map: directionsRenderer.getMap(),
            icon: {
                url: 'static/icons/user.svg', // Replace with your custom icon path
                scaledSize: new google.maps.Size(40, 40) // Set the width and height
            }
        });
    }
}

function setDateTime() {
    const now = new Date();
    const dateTimeInput = document.getElementById("datetime");
    dateTimeInput.value = now.toISOString().slice(0, 16);
}

// create table to display station-info on webpage
function displayStations(routeFinder) {
    const stationsContainer = document.getElementById('stations-container');

    // clearing any previous content
    stationsContainer.innerHTML = '';

    // creating table
    const table = document.createElement('table');
    table.className = 'stations-table';

    // creating headers
    const tableHeader = document.createElement('thead');
    tableHeader.innerHTML = `
    <tr>
        <th sort-index="0">Number <span class="sort-symbol"></span></th>
        <th sort-index="1">Name <span class="sort-symbol"></span></th>
        <th sort-index="2">Distance (metres) <span class="sort-symbol"></span></th>
        <th sort-index="3">Duration (minutes) <span class="sort-symbol"></span></th>
        <th sort-index="4">Bikes <span class="sort-symbol"></span></th>
        <th sort-index="5">Stands <span class="sort-symbol"></span></th>
        <th></th>
        <th></th>
    </tr>
`;
    // add headers to table
    table.appendChild(tableHeader);

    // make table sortable
    tableHeader.querySelectorAll('th[sort-index]').forEach(header => {
        header.addEventListener('click', () => {
            const columnIndex = parseInt(header.getAttribute('sort-index'));
            const currentOrder = header.getAttribute('sort-order') || 'asc';
            const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';

            // display correct symbol for sorted column
            tableHeader.querySelectorAll('th[sort-index]').forEach(header => {
                const symbolSpan = header.querySelector('.sort-symbol');
                if (header === event.target) {
                    symbolSpan.textContent = newOrder === 'asc' ? '▲' : '▼';
                } else {
                    symbolSpan.textContent = '';
                }
            });

            // call function to sort table based on selected header
            sortTable(table, columnIndex, newOrder);

            // update sort-order attribute
            header.setAttribute('sort-order', newOrder);
        });
    });

    // create table body
    const tableBody = document.createElement('tbody');

    routeFinder.stations.forEach((station, index) => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td>${station.stationNumber}</td>
            <td>${station.stationName}</td>
            <td>${station.dist}</td>
            <td>${Math.ceil(station.duration / 60)}</td>
            <td>${station.bikes}</td>
            <td>${station.stands}</td>
            <td><button class="show-route-btn">Show Route</button></td>
            <td><button class="show-graphs-btn">Show Graphs</button></td>
        `;

        row.querySelector('.show-route-btn').addEventListener('click', () => {
            routeFinder.showRoute(index);
        });

        row.querySelector('.show-graphs-btn').addEventListener('click', () => {
            createChart(station);
            updateLayout();
          });


        tableBody.appendChild(row);
    });
    // add body to table
    table.appendChild(tableBody);
    stationsContainer.appendChild(table);

    // sort table by distance initially
    sortTable(table, 2, 'asc');
    // display correct sorting symbol
    const distanceHeader = tableHeader.querySelector('th[sort-index="2"]');
    const distanceSymbolSpan = distanceHeader.querySelector('.sort-symbol');
    distanceSymbolSpan.textContent = '▲';
}

// function to sort table by column values
function sortTable(table, columnIndex, order) {
    const tableBody = table.querySelector('tbody');
    const rows = Array.from(tableBody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const cellA = a.cells[columnIndex].textContent;
        const cellB = b.cells[columnIndex].textContent;

        let compare = 0;
        // handling for numerical values
        if (!isNaN(parseFloat(cellA)) && !isNaN(parseFloat(cellB))) {
            compare = parseFloat(cellA) - parseFloat(cellB);
            //     handling for text values
        } else {
            compare = cellA.localeCompare(cellB);
        }

        return order === 'desc' ? -compare : compare;
    });

    tableBody.innerHTML = '';
    rows.forEach(row => tableBody.appendChild(row));
}


const dateTime = document.getElementById("datetime");

// Get the value of the selected date and time
dateTime.addEventListener("change", function () {
    const selectedDateTime = dateTime.value;
    console.log(selectedDateTime);
});

function updateLayout() {
    document.getElementById("map").style.height="60vh";
    document.getElementById("graphs").style.height="35vh";
}

function createChart(station) {
    const ctx = document.getElementById('myChart').getContext('2d');
    
    // destroy existing chart instance if it exists
    if (window.myChart instanceof Chart) {
        window.myChart.destroy();
    }
    
    const chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Bikes', 'Stands'],
        datasets: [{
          label: 'Availability',
          backgroundColor: ['#36A2EB', '#FF6384'],
          data: [station.bikes, station.stands]
        }]
      },
      options: {
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: true
            }
          }]
        }
      }
    });
  }

window.initMap = initMap;