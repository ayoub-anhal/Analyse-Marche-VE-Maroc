from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine, text
import pandas as pd
import folium
from opencage.geocoder import OpenCageGeocode
from time import sleep

engine = create_engine(URL(
    account = '*********',
    user = '********',
    password = '********',
    database = '********',
    schema = '********',
    warehouse = '********',
))

def generate_map():
    query = text("SELECT * FROM VOITURE_DATA.PUBLIC.ELECTRI6")
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)
    df.columns = df.columns.str.strip()

    df['lieu'] = df['localisation'].apply(
        lambda x: x.split(',')[-1].strip() if ',' in x else x.split(' ')[-1].strip()
    )

    key = '380315a7680f4ea8a602199f2f284880'
    geocoder = OpenCageGeocode(key)

    def geocode_location(location):
        try:
            results = geocoder.geocode(location + ", Maroc")
            if results and len(results):
                geometry = results[0]['geometry']
                return pd.Series([geometry['lat'], geometry['lng']])
            else:
                return pd.Series([None, None])
        except Exception as e:
            print(f"Erreur pour {location} : {e}")
            sleep(1)
            return geocode_location(location)

    df[['latitude', 'longitude']] = df['lieu'].apply(geocode_location)
    df = df.dropna(subset=['latitude', 'longitude'])

    maroc_map = folium.Map(location=[31.7917, -7.0926], zoom_start=6)

    for _, row in df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"<b>{row['nom']}</b><br>{row['description']}",
            tooltip=row['nom'],
            icon=folium.Icon(color='green', icon='bolt', prefix='fa')
        ).add_to(maroc_map)

    maroc_map.save("templates/bornes_recharge_maroc.html")

