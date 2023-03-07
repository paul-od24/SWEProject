import json

from flask import Flask, render_template
import sqlalchemy as sqla
from sqlalchemy import create_engine, select, text
import dblogin
import apilogin
import datetime

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

app = Flask(__name__, template_folder="./templates")


@app.route("/")
def mapview():
    return render_template('index.html', dic=json.dumps(pinDic), mapkey=apilogin.MAPKEY)


if __name__ == "__main__":
    app.run(debug=True)
