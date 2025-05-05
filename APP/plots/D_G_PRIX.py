from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine(URL(
    account = '*********',
    user = '********',
    password = '********',
    database = '********',
    schema = '********',
    warehouse = '********',
))

def load_data():
    query = "SELECT * FROM ELECTRI0"
    df = pd.read_sql(query, engine)
    df = df.drop(columns=["Unnamed: 3", "Unnamed: 4", "Unnamed: 5"], errors='ignore')
    df['Year'] = df['Month/Year'].str.split('-').str[0]
    return df

def get_available_years(df):
    return sorted(df['Year'].unique())

def get_prices_by_year(df, year=None):
    if year:
        df = df[df['Year'] == str(year)]
    labels = df['Month/Year'].tolist()
    diesel = df['Diesel Price (MAD/Liter)'].tolist()
    gasoline = df['Gasoline Price (MAD/Liter)'].tolist()
    return labels, diesel, gasoline
