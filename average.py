import pandas as pd
import sqlalchemy as sqla
import dblogin

# creating the engine
engine = sqla.create_engine(
    "mysql+mysqldb://{}:{}@{}:{}/{}".format(dblogin.USER, dblogin.PASSWORD, dblogin.URI, dblogin.PORT, dblogin.DB),
    echo=True)

# load data into a DataFrame
df = pd.read_sql('SELECT * FROM availability', engine)

# convert Unix timestamp to datetime
df['last_update'] = pd.to_datetime(df['last_update'], unit='s')

df['day'] = df['last_update'].dt.day_name()

# group the data by station number and day of the week and calculate the mean of available bikes and available bike stands
availability_grouped = df.groupby(['number', df['last_update'].dt.day_name()])[['available_bikes', 'available_bike_stands']].mean()

# print the result
# filter for station 
result = availability_grouped.loc[(number, day)]