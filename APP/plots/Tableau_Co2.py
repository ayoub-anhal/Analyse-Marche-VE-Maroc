from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine(URL(
    account = '*********',
    user = '********',
    password = '********',
    database = '********',
    schema = '********',
    warehouse = '********',
))

def load_co2_data():
    try:

        query = text("SELECT * FROM VOITURE_DATA.PUBLIC.ELECTRI1")
        with engine.connect() as connection:
            co2_emission = pd.read_sql(query, connection)
        
        co2_data = co2_emission.to_dict(orient='records')
        
        columns = co2_emission.columns.tolist()
        
        return columns, co2_data
    except Exception as e:
        print(f"Erreur lors du chargement des données CO2: {e}")
        return [], []
