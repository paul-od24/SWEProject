import pickle
import pandas as pd
import dblogin
import sqlalchemy as sqla
from sqlalchemy import create_engine, text

# creating the engine
engine = create_engine(
    "mysql+mysqldb://{}:{}@{}:{}/{}".format(dblogin.USER, dblogin.PASSWORD, dblogin.URI, dblogin.PORT, dblogin.DB),
    echo=True)

with engine.begin() as conn:
    # sql query to get number of bike stands at station
    stmt = "SELECT number, bike_stands "
    stmt += "FROM station"
    res = conn.execute(text(stmt))
    res = res.mappings().all()

# create dictionary to store number of bike stands for each station
bike_stands = {}

# create entry for each station in bike_stands dictionary
for dict in res:
    bike_stands[dict['number']] = dict['bike_stands']

# write bike_stands dictionary to pickle file
with open("/home/ubuntu/SWEProject/pickle_jar/bike_stands.pkl", 'wb') as handle:
    pickle.dump(bike_stands, handle, pickle.HIGHEST_PROTOCOL)