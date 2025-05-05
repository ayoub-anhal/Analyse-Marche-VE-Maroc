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
def get_autonomie_data():
    query = text("SELECT * FROM VOITURE_DATA.PUBLIC.ELECTRI5")
    with engine.connect() as connection:
        autonomie = pd.read_sql(query, connection)
    autonomie.rename(columns={'Prix': 'Prix (MAD)', 'Autonomie': 'Autonomie (km)'}, inplace=True)
    autonomie['Prix (MAD)'] = autonomie['Prix (MAD)'].astype(str)
    autonomie['Prix (MAD)'] = autonomie['Prix (MAD)'].str.replace(' MAD', '').str.replace(' ', '').str.replace('\xa0', '').str.replace('MAD', '').astype(float)
    autonomie['Autonomie (km)'] = autonomie['Autonomie (km)'].astype(str)
    autonomie['Autonomie (km)'] = autonomie['Autonomie (km)'].str.replace(' km', '').str.replace(' Km', '').str.replace('km', '').astype(int)
    labels = autonomie['Prix (MAD)'].tolist()
    values = autonomie['Autonomie (km)'].tolist()
    hover_labels = autonomie['VE'].tolist() if 'VE' in autonomie.columns else None
    return labels, values, hover_labels
