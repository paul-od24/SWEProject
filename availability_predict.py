import pickle
import pandas as pd
import sqlalchemy as sqla
from sqlalchemy import create_engine, text

def availability_predict(station, time, engine):
    """
    Function to use pre-generated models to predict bike and bike stand availability.
    Inputs: a station number, a time in the format '%Y-%m-%d %H:%M:%S', an sqlalchemy engine.
    Returns: a list in the format [estimated available bikes, estimated available bike stands]
            or the list [0, 0] if there was any error encountered.
    """
    # typecast station to int to remove any digits after decimal so we can open correct file
    station = int(station)
    try:
        with open(f"pickle_jar/{station}_model.pkl", 'rb') as handle:
            model = pickle.load(handle)

        # create features dataframe and convert time to datetime
        features = pd.DataFrame(data={"time": [time]})
        features['time'] = pd.to_datetime(features['time'], format='%Y-%m-%d %H:%M:%S')
        # decompose time into discrete features for model
        features['weekday'] = features['time'].dt.weekday
        features['workday'] = features['weekday'] < 5
        features['month'] = features['time'].dt.month
        features['day'] = features['time'].dt.day
        features['hour'] = features['time'].dt.hour
        features['minute'] = features['time'].dt.minute

        # round time up for getting weather data
        features['time'] = features['time'].dt.ceil('H')

        with engine.begin() as conn:
            # sql query to get weather forecast data
            stmt = "SELECT end, temp, wind_speed, wind_gust, rain_hourly "
            stmt += f"FROM weather_forecast WHERE end='{features['time'].astype(str).values[0]}'"
            wf_df = pd.read_sql(text(stmt), conn)

        with engine.begin() as conn:
            # sql query to get number of bike stands at station
            stmt = "SELECT bike_stands "
            stmt += f"FROM station WHERE number={station}"
            bike_stands = conn.execute(text(stmt))
            bike_stands = bike_stands.mappings().all()
            bike_stands = bike_stands[0]['bike_stands']
        
        # rename column in wf_df to allow merging with features
        wf_df = wf_df.rename(columns={"end": "time"})

        # merge wf_df with features
        features = pd.merge(
            wf_df,
            features,
            how='right',
            on='time'
        )

        # format features dataframe to be passed to model
        features = features.rename(columns={"rain_hourly": "rain"})
        features = features.drop(columns=['time'])
        features.columns = features.columns.astype(str)

        # get estimated available bikes from model
        avail_bikes = round(model.predict(features)[0])
        avail_bike_stands = bike_stands - avail_bikes

        return[avail_bikes, avail_bike_stands]
    
    except:
        return [0, 0]
    

    
