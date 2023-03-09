from sqlalchemy import create_engine
from sqlalchemy import text
import dblogin

# creating the engine with connection parameters stored in separate dblogin file
engine = create_engine(
    "mysql+mysqldb://{}:{}@{}:{}".format(dblogin.USER, dblogin.PASSWORD, dblogin.URI, dblogin.PORT),
    echo=True)

# preparing sql statement to create db
sql = """
CREATE DATABASE IF NOT EXISTS dbikes;
"""

# creating the db and "activating it"
with engine.begin() as connection:
    connection.execute(text(sql))
    connection.execute(text('USE dbikes'))

# preparing sql statement to create station table
sql = """
CREATE TABLE IF NOT EXISTS station (
address VARCHAR(256),
banking INTEGER,
bike_stands INTEGER,
bonus INTEGER,
contract_name VARCHAR(256),
name VARCHAR(256),
number INTEGER NOT NULL,
position_lat REAL,
position_lng REAL,
CONSTRAINT PK_station PRIMARY KEY (number)
);
"""

# create station table
try:
    with engine.begin() as connection:
        res = connection.execute(text(sql))
        print(res.fetchall())
except Exception as e:
    print(e)

# preparing sql statement to create availability table
sql = """
CREATE TABLE IF NOT EXISTS availability(
number INTEGER NOT NULL,
available_bikes INTEGER,
available_bike_stands INTEGER,
status VARCHAR(256),
last_update DATETIME NOT NULL,
CONSTRAINT PK_availability PRIMARY KEY (number,last_update)
);
"""

# creating availability table
try:
    with engine.begin() as connection:
        res = connection.execute(text(sql))
        print(res.fetchall())
except Exception as e:
    print(e)  # traceback.format_exc())

# preparing sql statement to create weather_historical table
sql = """
CREATE TABLE IF NOT EXISTS weather_historical(
time DATETIME NOT NULL,
temp FLOAT,
wind_dir FLOAT,
wind_speed FLOAT,
wind_gust FLOAT,
global_rad DOUBLE,
humidity FLOAT,
pressure DOUBLE,
cloudiness FLOAT,
low_clouds FLOAT,
med_clouds FLOAT,
high_clouds FLOAT,
dew_temp FLOAT,
rain FLOAT,
rain_min FLOAT,
rain_max FLOAT,
rain_prob FLOAT,
CONSTRAINT weather_historical PRIMARY KEY (time)
);
"""

# creating weather_historical table
try:
    with engine.begin() as connection:
        res = connection.execute(text(sql))
        print(res.fetchall())
except Exception as e:
    print(e)  # traceback.format_exc())

# preparing sql statement to create weather_forecast table
sql = """
CREATE TABLE IF NOT EXISTS weather_forecast(
type VARCHAR(256),
start DATETIME NOT NULL,
end DATETIME NOT NULL,
temp FLOAT,
wind_dir FLOAT,
wind_speed FLOAT,
wind_gust FLOAT,
global_rad DOUBLE,
humidity FLOAT,
pressure DOUBLE,
cloudiness FLOAT,
low_clouds FLOAT,
med_clouds FLOAT,
high_clouds FLOAT,
dew_temp FLOAT,
rain FLOAT,
rain_hourly FLOAT,
rain_min FLOAT,
rain_max FLOAT,
rain_prob FLOAT,
CONSTRAINT weather_forecast PRIMARY KEY (start,end)
);
"""

# creating weather_forecast table
try:
    with engine.begin() as connection:
        res = connection.execute(text(sql))
        print(res.fetchall())
except Exception as e:
    print(e)  # traceback.format_exc())

# preparing sql statement to add symbol column to weather tables
sql = """
ALTER TABLE weather_historical
ADD symbol VARCHAR(256);
ALTER TABLE weather_forecast
ADD symbol VARCHAR(256);
"""

# adding symbol column to weather tables
try:
    with engine.begin() as connection:
        res = connection.execute(text(sql))
        print(res.fetchall())
except Exception as e:
    print(e)  # traceback.format_exc())