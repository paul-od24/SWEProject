import requests
import traceback
import sqlalchemy as sqla
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import delete
import datetime
import dblogin
import xml.etree.ElementTree as ET

# creating the engine
engine = create_engine(
    "mysql+mysqldb://{}:{}@{}:{}/{}".format(dblogin.USER, dblogin.PASSWORD, dblogin.URI, dblogin.PORT, dblogin.DB),
    echo=True)

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

#API parameters
LAT = 53.350140
LON = -6.266155
MET = "http://metwdb-openaccess.ichec.ie/metno-wdb2ts/locationforecast?lat={};long={}"

# getting the data from the api
r = requests.get(MET.format(LAT, LON))

# parse xml data
root = ET.fromstring(r.text)

# create list of terminal times for each model
terminals = []
# iterate over models tag in xml
for model in root.iter('model'):
    # append model end time to list of terminals
    terminals.append(model.attrib['to'])

# function for reading harmonie model data into data dictionary
def harmonie(time, data):
    # move down xml tree to loc tag
    loc = time.find('location')
    # read data into dictionary
    data['temp'] = loc.find('temperature').attrib['value']
    data['wind_dir'] = loc.find('windDirection').attrib['deg']
    data['wind_speed'] = loc.find('windSpeed').attrib['mps']
    data['wind_gust'] = loc.find('windGust').attrib['mps']
    data['global_rad'] = loc.find('globalRadiation').attrib['value']
    data['humidity'] = loc.find('humidity').attrib['value']
    data['pressure'] = loc.find('pressure').attrib['value']
    data['cloudiness'] = loc.find('cloudiness').attrib['percent']
    data['low_clouds'] = loc.find('lowClouds').attrib['percent']
    data['med_clouds'] = loc.find('mediumClouds').attrib['percent']
    data['high_clouds'] = loc.find('highClouds').attrib['percent']
    data['dew_temp'] = loc.find('dewpointTemperature').attrib['value']

# function for reading ECMWF_1Hour model data into data dictionary
def ECMWF_1(time, data):
    data['type'] = "ECMWF_1Hour"
    # move down xml tree to loc tag
    loc = time.find('location')
    # read data into dictionary
    data['temp'] = loc.find('temperature').attrib['value']
    data['wind_dir'] = loc.find('windDirection').attrib['deg']
    data['wind_speed'] = loc.find('windSpeed').attrib['mps']
    data['global_rad'] = loc.find('globalRadiation').attrib['value']
    data['humidity'] = loc.find('humidity').attrib['value']
    data['pressure'] = loc.find('pressure').attrib['value']
    data['cloudiness'] = loc.find('cloudiness').attrib['percent']
    data['low_clouds'] = loc.find('lowClouds').attrib['percent']
    data['dew_temp'] = loc.find('dewpointTemperature').attrib['value']

# function for reading ECMWF_3Hour model data into data dictionary
def ECMWF_3(time, data):
    data['type'] = "ECMWF_3Hour"
    # move down xml tree to loc tag
    loc = time.find('location')
    # read data into dictionary
    data['temp'] = loc.find('temperature').attrib['value']
    data['wind_dir'] = loc.find('windDirection').attrib['deg']
    data['wind_speed'] = loc.find('windSpeed').attrib['mps']
    data['global_rad'] = loc.find('globalRadiation').attrib['value']
    data['humidity'] = loc.find('humidity').attrib['value']
    data['pressure'] = loc.find('pressure').attrib['value']
    data['cloudiness'] = loc.find('cloudiness').attrib['percent']
    data['low_clouds'] = loc.find('lowClouds').attrib['percent']
    data['dew_temp'] = loc.find('dewpointTemperature').attrib['value']

# function for reading ECMWF_6Hour model data into data dictionary
def ECMWF_6(time, data):
    data['type'] = "ECMWF_6Hour"
    # move down xml tree to loc tag
    loc = time.find('location')
    # read data into dictionary
    data['temp'] = loc.find('temperature').attrib['value']
    data['wind_dir'] = loc.find('windDirection').attrib['deg']
    data['wind_speed'] = loc.find('windSpeed').attrib['mps']
    data['global_rad'] = loc.find('globalRadiation').attrib['value']
    data['humidity'] = loc.find('humidity').attrib['value']
    data['pressure'] = loc.find('pressure').attrib['value']
    data['cloudiness'] = loc.find('cloudiness').attrib['percent']
    data['low_clouds'] = loc.find('lowClouds').attrib['percent']
    data['dew_temp'] = loc.find('dewpointTemperature').attrib['value']

# function for reading rain data
def Rain(time, data, h = 1):
    # we use the rain data to determine the time interval
    data['start'] = time.attrib['from']
    data['end'] = time.attrib['to']
    # move down xml tree to loc tag
    loc = time.find('location')
    # rain data is typecast to float to allow division
    data['rain'] = float(loc.find('precipitation').attrib['value'])
    # we divide by the number of hours to get hourly data
    data['rain_hourly'] = data['rain'] / h
    # harmonie_1hour and ECMWF_1hour have the below data but other models do not
    if h == 1:
        data['rain_min'] = loc.find('precipitation').attrib['minvalue']
        data['rain_max'] = loc.find('precipitation').attrib['maxvalue']
        data['rain_prob'] = loc.find('precipitation').attrib['probability']

def write_to_db(table, data):
    try:
        # starting transaction
        with engine.begin() as connection:
            # preparing insert statement
            stmt = insert(table)
            # executing insert operations
            connection.execute(stmt, data)
    except:
        print(traceback.format_exc())

def forecast_delete():
    try:
        # starting transaction
        with engine.begin() as connection:
            # preparing delete statement
            stmt = delete(weather_forecast)
            # executing delete operations
            connection.execute(stmt)
    except:
        print(traceback.format_exc())

# create list of models
models = [harmonie, ECMWF_1, ECMWF_3, ECMWF_6]
# first tells us if we are looking at the first entry
first = True
# rain tells us if we are looking at rain data (every second entry is rain data)
rain = False
# i keeps track of which model we are using
current_model = 0
# create empty dictionary
data = {}
# iterate through each time entry in our xml
for time in root.iter('time'):
    # we both read data from xml and execute sql on rain data
    if rain:
        # first entry is our historical data
        if (first):
            # get time (only one for historical data)
            data['time'] = time.attrib['to']
            # move down xml tree to loc tag
            loc = time.find('location')
            # we do not use Rain function as historical data is slightly different
            data['rain'] = float(loc.find('precipitation').attrib['value'])
            data['rain_min'] = loc.find('precipitation').attrib['minvalue']
            data['rain_max'] = loc.find('precipitation').attrib['maxvalue']
            data['rain_prob'] = loc.find('precipitation').attrib['probability']
            # no longer first
            first = False
            # write to weather_historical table
            write_to_db(weather_historical, data)
            # delete all rows from the weather_forecast table
            forecast_delete()
        # harmonie_1hour data
        elif (current_model == 0):
            # get data not part of harmonie_1hour function
            data['type'] = "Harmonie_1hour"
            # get rain data
            Rain(time, data)
            # write to weather_forecast table
            write_to_db(weather_forecast, data)
        # ECMWF_1hour data
        elif (current_model == 1):
            # get rain data
            Rain(time, data)
            # write to weather_forecast table
            write_to_db(weather_forecast, data)
        # ECMWF_3hour data
        elif (current_model == 2):
            # get rain data, which is for 3 hours
            Rain(time, data, 3)
            # write to weather_forecast table
            write_to_db(weather_forecast, data)
        # ECMWF_6hour data
        elif (current_model == 3):
            # get rain data, which is for 6 hours
            Rain(time, data, 6)
            # write to weather_forecast table
            write_to_db(weather_forecast, data)
        # empty data dictionary
        data = {} 
    # we only read data using our functions on non-rain data
    else:
        models[current_model](time, data)
    # if we have reached the end of current model move to next one
    if (time.attrib['to'] == terminals[current_model] and rain == True):
        current_model += 1
    # update rain flag
    rain = not rain
