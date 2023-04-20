import json
import requests
import traceback
import apilogin
import sqlalchemy as sqla
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import insert
from dateutil import tz
import datetime
import dblogin

# creating the engine
engine = create_engine(
    "mysql+mysqldb://{}:{}@{}:{}/{}".format(dblogin.USER, dblogin.PASSWORD, dblogin.URI, dblogin.PORT, dblogin.DB),
    echo=True)

# creating metadata objects for each of the tables
metadataS = sqla.MetaData()
metadataA = sqla.MetaData()
metadataLA = sqla.MetaData()

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

# creating table object for latest availability table
latest_availability = sqla.Table("latest_availability", metadataLA,
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
        vals = tuple(map(fix_data, data))
        # preparing statement station insert
        stmt = insert(station)
        # adding parameters to the statement to "ignore" duplicate keys (-> update with same value)
        odk_stmt = stmt.on_duplicate_key_update(
            number=stmt.inserted.number)
        # executing insert operations for station
        connection.execute(odk_stmt, vals)

        # preparing statement availability insert
        stmt = insert(availability)
        # adding parameters to the statement to "ignore" duplicate keys (-> update with same value)
        odk_stmt = stmt.on_duplicate_key_update(
            number=stmt.inserted.number)
        # executing insert operations for availability
        connection.execute(odk_stmt, vals)

        # statement to update the latest availability table
        stmt = insert(latest_availability)
        latest_stmt = stmt.on_duplicate_key_update(available_bikes=stmt.inserted.available_bikes,
                                                   available_bike_stands=stmt.inserted.available_bike_stands,
                                                   last_update=stmt.inserted.last_update)
        connection.execute(latest_stmt, vals)


def toirish(utc):
    # need to declare datetime object as utc
    from_zone = tz.tzutc()
    utc = utc.replace(tzinfo=from_zone)
    # define timezone to convert time to
    to_zone = tz.gettz('Europe/Dublin')
    return utc.astimezone(to_zone)


# function to "fix" data so it can be processed in the db without issues
def fix_data(data):
    data['position_lat'] = data['position']['lat']
    data['position_lng'] = data['position']['lng']
    # converting epoch time in milliseconds to date-time format
    data['last_update'] = toirish(datetime.datetime.fromtimestamp(data['last_update'] / 1000))
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
