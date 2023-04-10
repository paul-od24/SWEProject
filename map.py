import json
from flask import Flask, render_template, request
import sqlalchemy as sqla
from sqlalchemy import create_engine, select, text
from geopy import distance
from itertools import islice
import dblogin
import apilogin
from availability_predict import availability_predict, multi_availability_predict

# creating the engine
engine = create_engine(
    "mysql+mysqldb://{}:{}@{}:{}/{}".format(dblogin.USER, dblogin.PASSWORD, dblogin.URI, dblogin.PORT, dblogin.DB),
    echo=True)

metadataS = sqla.MetaData()
# creating table object for station table
station = sqla.Table("station", metadataS,
                     autoload_with=engine,
                     schema='dbikes'
                     )

metadataA = sqla.MetaData()
# creating table object for availability table
availability = sqla.Table("availability", metadataA,
                          autoload_with=engine,
                          schema='dbikes'
                          )

# creating metadata objects for each of the tables
metadataWH = sqla.MetaData()
metadataWF = sqla.MetaData()

# creating table object for weather_historical table
weather_historical = sqla.Table("weather_historical", metadataWH,
                                autoload_with=engine,
                                schema='dbikes'
                                )

# creating table object for weather_forecast table
weather_forecast = sqla.Table("weather_forecast", metadataWF,
                              autoload_with=engine,
                              schema='dbikes'
                              )

app = Flask(__name__, template_folder="./templates")


def update_data(pinDic, wCur, wetDic):
    """
    Function that gets the latest bike and weather data and stores it in the appropriate dictionaries.
    Returns: void
    """
    # sql statement to select bike data
    stmt = '''SELECT station.number, name, position_lat, position_lng, available_bikes, available_bike_stands, last_update
    FROM station, latest_availability
    WHERE station.`number` = latest_availability.number;
    '''

    with engine.begin() as connection:
        for row in connection.execute(text(stmt)):
            pos = {"lat": float(row.position_lat), "lng": float(row.position_lng)}
            pinDic[row.number] = {"number": row.number, "name": row.name, "position": pos,
                                  "available_bikes": row.available_bikes,
                                  "available_bike_stands": row.available_bike_stands,
                                  "last_update": str(row.last_update)}

    # preparing sql statement to get current weather
    stmt = "SELECT * FROM weather_historical ORDER BY `time` DESC LIMIT 1"
    # executing sql statement
    with engine.begin() as connection:
        res = connection.execute(text(stmt))
        res = res.mappings().all()
        res = res[0]
        wCur["symbol"] = res.symbol
        wCur["rain"] = res.rain
        wCur["temp"] = res.temp

    # preparing sql statement to get current weather
    stmt = select(weather_forecast.c.end, weather_forecast.c.symbol, weather_forecast.c.rain_hourly)

    # executing sql statement
    with engine.begin() as connection:
        for row in connection.execute(stmt):
            data = {"symbol": row.symbol, "rain": row.rain_hourly}
            wetDic[str(row.end)] = data


@app.route("/")
def mapview():
    """
    Function returning rendered template index.html including variables needed for weather & pins
    Returns:
        object: rendered flask template
    """
    pinDic = {}
    wCur = {}
    wetDic = {}

    update_data(pinDic, wCur, wetDic)
    return render_template('index.html', dic=json.dumps(pinDic), mapkey=apilogin.MAPKEY, wCur=json.dumps(wCur),
                           wetDic=json.dumps(wetDic))


@app.route("/", methods=["post"])
def findClosest():
    """
    Function taking a location from the webpage and checking for the closest station.
    Returns:
        dict: Dictionary containing number of and distance to closest station.
    """
    data = dict(request.get_json())
    userloc = (data["userloc"]["lat"], data["userloc"]["lng"])
    pinDic = data["pinDic"]
    d_dic = {}
    predictions = {}
    for i in pinDic:
        station = (pinDic[i]["position"].get("lat"), pinDic[i]["position"].get("lng"))
        d = distance.distance(userloc, station).m
        d_dic[i] = d
    d_dic_sorted = dict(sorted(d_dic.items(), key=lambda item: item[1]))
    print(d_dic_sorted)

    closest = dict(islice(d_dic_sorted.items(), 10))

    # create list of stations
    stations = []
    for i in closest.keys():
        stations.append(str(i))

    # pass list of stations and time to model
    res = multi_availability_predict(stations, '2023-04-14 19:15:00', engine)

    for i in closest.keys():
        # TODO call prediction function and map returned values to bikes/stands
        #bikes, stands = pinDic[i].get("available_bikes"), pinDic[i].get("available_bike_stands")
        bikes, stands = res[i][0], res[i][1]
        predictions[i] = {"dist": closest[i], "bikes": bikes, "stands": stands}

    return predictions


if __name__ == "__main__":
    app.run(debug=True)