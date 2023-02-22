import json
import requests
import traceback
import datetime
import time
import apilogin
import sqlalchemy as sqla
from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy import text
import datetime
import dblogin

# creating the engine
engine = create_engine(
    "mysql+mysqldb://{}:{}@{}:{}/{}".format(dblogin.USER, dblogin.PASSWORD, dblogin.URI, dblogin.PORT, dblogin.DB),
    echo=True)

metadataS = sqla.MetaData()
metadataA = sqla.MetaData()

station = sqla.Table("station", metadataS,
                     autoload_with=engine,
                     schema='dbikes'
                     )

availability = sqla.Table("availability", metadataA,
                          autoload_with=engine,
                          schema='dbikes'
                          )

APIKEY = apilogin.APIKEY
NAME = 'Dublin'
STATIONS = 'https://api.jcdecaux.com/vls/v1/stations'


def write_to_file(text, now):
    with open('data/bikes_{}'.format(now).replace(' ', '_'), 'w') as f:
        f.write(text)


def write_to_db(text):
    data = json.loads(text)
    with engine.begin() as connection:
        stmt = tuple(map(fix_data, data))
        connection.execute(insert(station), stmt)
        connection.execute(insert(availability), stmt)


def fix_data(data):
    data['position_lat'] = data['position']['lat']
    data['position_lng'] = data['position']['lng']
    data['last_update'] = datetime.datetime.fromtimestamp(data['last_update'] / 1000)
    return data


def main():
    try:
        now = datetime.datetime.now()
        r = requests.get(STATIONS, params={'apiKey': APIKEY, 'contract': NAME})
        print(r, now)
        write_to_file(r.text, now)
        write_to_db(r.text)
    except:
        print(traceback.format_exc())

        # TODO
        # if engine is None:
        #     pass

    return


main()
