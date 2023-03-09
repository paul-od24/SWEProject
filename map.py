import json

from flask import Flask, render_template, request
import sqlalchemy as sqla
from sqlalchemy import create_engine, select, text
from geopy import distance
import dblogin
import apilogin

# creating the engine
engine = create_engine(
    "mysql+mysqldb://{}:{}@{}:{}/{}".format(dblogin.USER, dblogin.PASSWORD, dblogin.URI, dblogin.PORT, dblogin.DB),
    echo=True)

metadataS = sqla.MetaData()
# creating table object for station table
station = sqla.Table("station", metadataS,
                     autoload=engine,
                     schema='dbikes'
                     )

metadataS = sqla.MetaData()
# creating table object for availability table
availability = sqla.Table("availability", metadataS,
                     autoload=engine,
                     schema='dbikes'
                     )

stmt = select(
    station.c.number, 
    station.c.name, 
    station.c.position_lat, 
    station.c.position_lng, 
    availability.c.available_bikes, 
    availability.c.available_bike_stands
).select_from(station.join(availability, station.c.number == availability.c.number)).order_by(station.c.number)

# pin information
stmt2 = select([
    station.c.number, 
    station.c.name, 
    station.c.position_lat, 
    station.c.position_lng,
    availability.c.available_bikes,
    availability.c.available_bike_stands
]).select_from(
    station.join(
        availability, 
        station.c.number == availability.c.number
    )
).order_by(station.c.number)


pinDic = {}
avDic = {}

with engine.begin() as connection:
    for row in connection.execute(stmt):
        # pin information
        avDic[row.number] = {"available_bikes": row.available_bikes, "available_bike_stands": row.available_bike_stands}

    # loop through the results and add to pinDic dictionary
    for row in connection.execute(stmt2):
        # static info to place pins on map
        pos = {"lat": float(row.position_lat), "lng": float(row.position_lng)}
        pinDic[row.number] = {"name": row.name, "number": row.number, "position": pos, "available_bikes": row.available_bikes, "available_bike_stands": row.available_bike_stands}
#print(pinDic)
#print(json.dumps(avDic))

# creating metadata objects for each of the tables
metadataWH = sqla.MetaData()
metadataWF = sqla.MetaData()

# creating table object for weather_historical table
weather_historical = sqla.Table("weather_historical", metadataWH,
                                autoload=engine,
                                schema='dbikes'
                                )

# creating table object for weather_forecast table
weather_forecast = sqla.Table("weather_forecast", metadataWF,
                              schema='dbikes',
                              autoload=True,
                              autoload_with=engine
                              )

# creating wCur dictionary
wCur = {}
# prpearing sql statement to get current weather
stmt = "SELECT * FROM weather_historical ORDER BY `time` DESC LIMIT 1"
# executing sql statment
with engine.begin() as connection:
    res = connection.execute(text(stmt))
    res = res.mappings().all()
    res = res[0]
    data = {"symbol": res.symbol, "rain": res.rain}
    wCur = data

# preparing sql statement to get current weather
stmt = select(weather_forecast.c.end, weather_forecast.c.symbol, weather_forecast.c.rain_hourly)

# creating weather forecast dictionary
wetDic = {}

# executing sql statement
with engine.begin() as connection:
    for row in connection.execute(stmt):
        data = {"symbol": row.symbol, "rain": row.rain_hourly}
        wetDic[str(row.end)] = data

app = Flask(__name__, template_folder="./templates")


@app.route("/")
def mapview():
    return render_template('index.html', dic=json.dumps(pinDic), mapkey=apilogin.MAPKEY, wCur=json.dumps(wCur),
                           wetDic=json.dumps(wetDic))

# function taking a location from the webpage and checking for the closest station
@app.route("/", methods=["post"])
def findClosest():
    userloc = dict(request.get_json())
    userloc = (userloc["lat"], userloc["lng"])
    mindist = -1
    closest = {"failed": "failed"}
    for i in pinDic:
        teststation = (pinDic[i]["position"].get("lat"), pinDic[i]["position"].get("lng"))
        d = distance.distance(userloc, teststation).m
        if mindist == -1 or d < mindist:
            mindist = round(d, 0)
            closest = {"number": i, "distance": mindist}
    return closest


if __name__ == "__main__":
    app.run(debug=True)