import pandas as pd
import sqlalchemy as sqla
import dblogin
import calendar


def getChartData(station_number):
    # creating the engine
    engine = sqla.create_engine(
        "mysql+mysqldb://{}:{}@{}:{}/{}".format(dblogin.USER, dblogin.PASSWORD, dblogin.URI, dblogin.PORT, dblogin.DB),
        echo=True)

    # load data into a DataFrame
    df = pd.read_sql(f'SELECT * FROM availability WHERE number = {station_number} ORDER BY last_update DESC LIMIT 10080', engine)

    # convert Unix timestamp to datetime
    df['last_update'] = pd.to_datetime(df['last_update'], unit='s')

    df['day'] = df['last_update'].dt.day_name()

    df['hour'] = df['last_update'].dt.hour

    # group the data by station number day of the week, hour and calculate the mean of available bikes and available bike stands
    availability_grouped = df.groupby(['number', 'day', 'hour'])[
        ['available_bikes', 'available_bike_stands']].mean().reset_index()
    availability_grouped['available_bikes'] = availability_grouped['available_bikes'].round()
    availability_grouped['available_bike_stands'] = availability_grouped['available_bike_stands'].round()

    # sorting the dataframe
    availability_grouped['day'] = pd.Categorical(availability_grouped['day'], categories=list(calendar.day_name),
                                                 ordered=True)
    availability_grouped = availability_grouped.sort_values(by=['day', 'hour']).reset_index(drop=True)

    # return in json format
    return availability_grouped.to_json(orient='records')
