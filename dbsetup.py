import sqlalchemy as sqla
from sqlalchemy import create_engine
from sqlalchemy import text
import traceback
import glob
import os
from pprint import pprint
import simplejson as json
import requests
import time
from IPython.display import display
import dblogin

engine = create_engine(
    "mysql+mysqldb://{}:{}@{}:{}".format(dblogin.USER, dblogin.PASSWORD, dblogin.URI, dblogin.PORT),
    echo=True)

sql = """
CREATE DATABASE IF NOT EXISTS dbikes;
"""

with engine.begin() as connection:
    connection.execute(text(sql))
    connection.execute(text('USE dbikes'))

sql = """
CREATE TABLE IF NOT EXISTS station (
address VARCHAR(256),
banking INTEGER,
bike_stands INTEGER,
bonus INTEGER,
contract_name VARCHAR(256),
name VARCHAR(256),
number INTEGER,
position_lat REAL,
position_lng REAL,
status VARCHAR(256)
);
"""
try:
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS station;"))
        res = connection.execute(text(sql))
        print(res.fetchall())
except Exception as e:
    print(e)


sql = """
CREATE TABLE IF NOT EXISTS availability(
number INTEGER,
available_bikes INTEGER,
available_bike_stands INTEGER,
last_update INTEGER
);
"""
try:
    with engine.begin() as connection:
        res = connection.execute(text(sql))
        print(res.fetchall())
except Exception as e:
    print(e) #traceback.format_exc())
