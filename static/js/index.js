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
  const stations = {};


  // looping through the pins and adding them to the map
  for(let i in pinDic) {
    stations[pinDic[i]] = new google.maps.Marker({position: pinDic[i]["position"], map: map,})
    // stations.push(new google.maps.Marker({position: pinDic[i], map: map,}));
  }
}

window.initMap = initMap;