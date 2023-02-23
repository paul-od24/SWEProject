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
        connection.execute(text("DROP TABLE IF EXISTS station;"))
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
