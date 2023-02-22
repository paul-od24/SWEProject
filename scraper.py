import json
import requests
import traceback
import apilogin
import sqlalchemy as sqla
from sqlalchemy import create_engine
from sqlalchemy import insert
import datetime
import dblogin

# creating the engine
engine = create_engine(
    "mysql+mysqldb://{}:{}@{}:{}/{}".format(dblogin.USER, dblogin.PASSWORD, dblogin.URI, dblogin.PORT, dblogin.DB),
    echo=True)

# creating metadata objects for each of the tables
metadataS = sqla.MetaData()
metadataA = sqla.MetaData()

# creating table object for station table
station = sqla.Table("station", metadataS,
                     autoload_with=engine,
                     schema='dbikes'
                     )

# creating table object for availability table
availability = sqla.Table("availability", metadataA,
                          autoload_with=engine,
                          schema='dbikes'
                          )

# API parameters (apilogin is a separate py file)
APIKEY = apilogin.APIKEY
NAME = 'Dublin'
STATIONS = 'https://api.jcdecaux.com/vls/v1/stations'


def write_to_db(text):
    # loading the data
    data = json.loads(text)
    # starting transaction
    with engine.begin() as connection:
        # preparing statement for insertion
        stmt = tuple(map(fix_data, data))
        # executing insert operations for each of the tables (station & availability)
        connection.execute(insert(station), stmt)
        connection.execute(insert(availability), stmt)


# function to "fix" data so it can be processed in the db without issues
def fix_data(data):
    data['position_lat'] = data['position']['lat']
    data['position_lng'] = data['position']['lng']
    # converting epoch time in milliseconds to date-time format
    data['last_update'] = datetime.datetime.fromtimestamp(data['last_update'] / 1000)
    return data


def main():
    try:
        now = datetime.datetime.now()
        # getting the data from the api
        r = requests.get(STATIONS, params={'apiKey': APIKEY, 'contract': NAME})
        # calling function to write data to db
        write_to_db(r.text)
    except:
        print(traceback.format_exc())

        # TODO
        # if engine is None:
        #     pass

    return


main()
