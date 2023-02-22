from sqlalchemy import create_engine
from sqlalchemy import text
import dblogin

# creating the engine
engine = create_engine(
    "mysql+mysqldb://{}:{}@{}:{}/{}".format(dblogin.USER, dblogin.PASSWORD, dblogin.URI, dblogin.PORT, dblogin.DB),
    echo=True)

# starting transaction
with engine.begin() as connection:
    # selecting all columns in station table
    s_cols = connection.execute(text('SELECT * FROM station'))
    # selecting all columns in availability table
    a_cols = connection.execute(text('SELECT * FROM availability'))

# print column names for both tables
print(s_cols.keys())
print(a_cols.keys())
