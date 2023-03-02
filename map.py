import json

from flask import Flask, render_template
import sqlalchemy as sqla
from sqlalchemy import create_engine, select
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

stmt = select(station.c.name, station.c.position_lat, station.c.position_lng)

pinDic = {}

with engine.begin() as connection:
    for row in connection.execute(stmt):
        pos = {"lat": float(row.position_lat), "lng": float(row.position_lng)}
        pinDic[row.name] = pos

print(str(pinDic))

app = Flask(__name__, template_folder="./templates")


@app.route("/")
def mapview():
    return render_template('index.html', dic=json.dumps(pinDic), mapkey=apilogin.MAPKEY)


if __name__ == "__main__":
    app.run(debug=True)
