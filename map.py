import json

from flask import Flask, render_template
import sqlalchemy as sqla
from sqlalchemy import create_engine, select, text
import dblogin
import apilogin

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

stmt = select(station.c.number, station.c.name, station.c.position_lat, station.c.position_lng)

pinDic = {}
avDic = {}

with engine.begin() as connection:
    for row in connection.execute(stmt):
        # static info to place pins on map
        pos = {"lat": float(row.position_lat), "lng": float(row.position_lng)}
        pinDic[row.number] = {"name": row.name, "position": pos}

        # pin information
        stmt2 = 'SELECT available_bikes, available_bike_stands, last_update FROM availability WHERE `number` = ' + str(
            row.number) + ' ORDER BY last_update DESC LIMIT 1;'
        res = connection.execute(text(stmt2)).mappings().all()[0]
        avDic[row.number] = dict(res)
        avDic[row.number]["last_update"] = str(avDic[row.number].get("last_update"))

print(json.dumps(avDic))

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


if __name__ == "__main__":
    app.run(debug=True)