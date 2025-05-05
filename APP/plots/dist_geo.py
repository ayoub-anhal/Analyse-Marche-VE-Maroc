from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine, text
import pandas as pd


engine = create_engine(URL(
    account = 'gkexgfn-mc38946',
    user = 'AYOUB',
    password = 'Ayoub543211@#@',
    database = 'VOITURE_DATA',
    schema = 'PUBLIC',
    warehouse = 'COMPUTE_WH',
))

def load_geo_data():

    try:
        query = text("SELECT * FROM VOITURE_DATA.PUBLIC.ELECTRI4")
        with engine.connect() as connection:
            dist_geo = pd.read_sql(query, connection)
        print(f"Données géographiques chargées avec succès: {len(dist_geo)} entrées")
        return dist_geo
    except Exception as e:
        print(f"Erreur lors du chargement des données géographiques: {e}")
        return pd.DataFrame(columns=['year', 'city', 'distribution of sales'])

def get_available_years():

    dist_geo = load_geo_data()
    if dist_geo.empty:
        return []
    return sorted(dist_geo['year'].unique().tolist())

def get_geo_distribution_by_year(year=None):

    dist_geo = load_geo_data()
    if dist_geo.empty:
        return [], []
    
    if year:
        if isinstance(year, str) and year.isdigit():
            year = int(year)
        filtered_data = dist_geo[dist_geo['year'] == year]
    else:
        latest_year = dist_geo['year'].max()
        filtered_data = dist_geo[dist_geo['year'] == latest_year]
    
    filtered_data = filtered_data.sort_values(by='distribution of sales', ascending=False)
    cities = filtered_data['city'].tolist()
    distribution = filtered_data['distribution of sales'].tolist()
    return cities, distribution
