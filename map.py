import json

from flask import Flask, render_template, jsonify
import sqlalchemy as sqla
from sqlalchemy import create_engine, select, text
import pandas as pd
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
infoDic = {}

with engine.begin() as connection:
    for row in connection.execute(stmt):
        pos = {"lat": float(row.position_lat), "lng": float(row.position_lng)}
        pinDic[row.name] = pos
        infoStmt='''
        select station.name, available_bikes, available_bike_stands, last_update, availability.`number`  
from station, availability
WHERE availability.`number` = 73 AND station.number=availability.`number` 
ORDER BY `last_update` DESC 
limit 1;
        '''


print(str(pinDic))

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

wCur = {}
stmt = "SELECT * FROM weather_historical ORDER BY `time` DESC LIMIT 1"
with engine.begin() as connection:
        res = connection.execute(text(stmt))
        res = res.mappings().all()
        res = res[0]
        data = {"symbol": res.symbol, "rain": res.rain}
        wCur = data
        
stmt = select(weather_forecast.c.end, weather_forecast.c.symbol, weather_forecast.c.rain_hourly)

wetDic = {}

with engine.begin() as connection:
    for row in connection.execute(stmt):
        data = {"symbol": row.symbol, "rain": row.rain_hourly}
        wetDic[str(row.end)] = data

app = Flask(__name__, template_folder="./templates")


@app.route("/")
def mapview():
    # pins= json.dumps()
    # pins.status_code = 200
    return render_template('index.html', dic=json.dumps(pinDic), mapkey=apilogin.MAPKEY, wCur=json.dumps(wCur), wetDic=json.dumps(wetDic), name=json.dumps(name), bikesAvail=json.dumps(bikesAvail))


if __name__ == "__main__":
    app.run(debug=True)
