# import packages
import numpy as np
import pandas as pd
import sqlalchemy as sqla
from sqlalchemy import create_engine
import dblogin
import apilogin
import matplotlib.dates as mdates
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import cross_validate
import pickle

# suppress annoying pandas error messages
pd.options.mode.chained_assignment = None

# create engine for executing sql
engine = create_engine(
    "mysql+mysqldb://{}:{}@{}:{}/{}".format(dblogin.USER, dblogin.PASSWORD, dblogin.URI, dblogin.PORT, dblogin.DB),
    echo=True)

with engine.begin() as connection:
    avail_df = pd.read_sql_table('availability', connection)

with engine.begin() as connection:
    wh_df = pd.read_sql_table('weather_historical', connection)

station_numbers = avail_df.number.unique()

# create time series cross validation object
ts_cv = TimeSeriesSplit(
    n_splits=5,
    gap=48,
    max_train_size=10000,
    test_size=1000,
)

# create function for evaluating our models
def evaluate(model, X, y, cv):
    cv_results = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring=["neg_mean_absolute_error", "neg_root_mean_squared_error"],
    )
    mae = -cv_results["test_neg_mean_absolute_error"]
    rmse = -cv_results["test_neg_root_mean_squared_error"]
    print(
        f"Mean Absolute Error:     {mae.mean():.3f} +/- {mae.std():.3f}\n"
        f"Root Mean Squared Error: {rmse.mean():.3f} +/- {rmse.std():.3f}"
    )

num_models = 0
num_fails = 0
for station_number in station_numbers:
    try:
        # get data for current station
        station_df = avail_df.loc[avail_df['number'] == station_number]
        # convert last_update column datatype to datetime
        station_df['last_update'] = pd.to_datetime(station_df['last_update'])
        # create time column to join station data with weather data
        station_df['time'] = station_df['last_update'].dt.ceil('H')
        # merge weather and station data
        merged_df = pd.merge(
            station_df,
            wh_df,
            how='right',
            on='time'
        )
        # remove data from before 27 Feb due to discontinuous nature of this data
        merged_df = merged_df[merged_df['last_update'] >= '2023-02-27']
        # drop columns we are not interested in
        drop_cols = ['wind_dir', 'global_rad', 'humidity', 'pressure', 'cloudiness', 'low_clouds',
                    'med_clouds', 'high_clouds', 'dew_temp', 'rain_min', 'rain_max', 'symbol', 
                    'available_bike_stands', 'rain_prob', 'time']
        merged_df =  merged_df.drop(drop_cols, axis=1)
        # create column of weekdays represented as numbers
        merged_df['weekday'] = merged_df['last_update'].dt.weekday
        # create workday feature where Mon-Fri is a workday
        merged_df['workday'] = merged_df['weekday'] < 5
        # seperate datime into month, day, hour, minute
        merged_df['month'] = merged_df['last_update'].dt.month
        merged_df['day'] = merged_df['last_update'].dt.day
        merged_df['hour'] = merged_df['last_update'].dt.hour
        merged_df['minute'] = merged_df['last_update'].dt.minute
        # encode workday columns as 0 or 1
        workday = merged_df.workday
        workday = workday.apply(lambda x : 1 if x else 0)
        workday.value_counts()
        # create features df
        features = merged_df
        # drop columns from features that are not used by model
        features = features.drop(['number', 'available_bikes', 'status', 'last_update'], axis=1)
        # convert feature column headers to string datatype
        features.columns = features.columns.astype(str)
        # set y (our target feature) to available bikes
        y = merged_df.available_bikes
        # specify which columns are categorical and encode using ordinal encoder
        cat_cols = ['workday']
        categories = [
            [False, True]
        ]
        ordinal_encoder = OrdinalEncoder(categories=categories)
        # make our pipeline (model) 
        gbrt_pipeline = make_pipeline(
            ColumnTransformer(
                transformers=[
                    ("categorical", ordinal_encoder, cat_cols),
                ],
                remainder="passthrough",
                verbose_feature_names_out=False,
            ),
            HistGradientBoostingRegressor(
                categorical_features=cat_cols,
            ),
        ).set_output(transform="pandas")
        # evaluate model and print results
        evaluate(gbrt_pipeline, features, y, cv=ts_cv)
        # fit model
        gbrt_pipeline.fit(features, y)
        # store model in pickle_jar
        with open(f"pickle_jar/{station_number}_model.pkl", 'wb') as handle:
            pickle.dump(gbrt_pipeline, handle, pickle.HIGHEST_PROTOCOL)
        print(f"Model created for station number {station_number}")
        num_models += 1
    except:
        print(f"Error generating model for station number {station_number}")
        num_fails += 1

print(f"Finished. Generated {num_models} models and {num_fails} failures.")