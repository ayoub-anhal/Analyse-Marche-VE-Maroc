from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
import json
import requests
import threading
import time
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine, text

from plots.Sales import get_sales_data
from plots.D_G_PRIX import load_data, get_available_years, get_prices_by_year
from plots.Autonomie import get_autonomie_data
from plots.generate_map import generate_map
from plots.Tableau_Co2 import load_co2_data
from plots.dist_geo import get_geo_distribution_by_year, get_available_years as get_geo_years

app = Flask(__name__)


engine = create_engine(URL(
    account = '*********',
    user = '********',
    password = '********',
    database = '********',
    schema = '********',
    warehouse = '********',
))
df = load_data()
generate_map()

try:
    query = text("SELECT * FROM VOITURE_DATA.PUBLIC.ELECTRI3")
    with engine.connect() as connection:
        cars_data = pd.read_sql(query, connection)
    print("Données électriques chargées avec succès:", cars_data.head())
except Exception as e:
    print(f"Erreur lors du chargement des données électriques: {e}")
    pass

# Dictionnaire des GIFs pour chaque marque
car_gifs = {
    'DACIA': 'Dacia1.gif',
    'BYD': 'BYD1.gif',
    'VOLVO': 'volvo1.gif',
    'CITROEN': 'citroin1.gif',
    'DFSK': 'dfsk1.gif',
    'Mercedes-benz': 'mercidece1.gif',
    'AUDI': 'Audi1.gif',
    'Hyundai': 'hyundai1.gif',
    'MG': 'MG1.gif'
}

# Configuration pour l'API de news
NEWS_API_KEY = '07261da4478345c0aac30ffd81138008'
articles_data = []

# Fonction pour obtenir les derniers articles sur les véhicules électriques
def get_ev_articles():
    url = (
        f'https://newsapi.org/v2/everything?'
        f'q=Electric+Vehicle&'
        f'sortBy=publishedAt&'
        f'language=en&'
        f'pageSize=10&'
        f'apiKey={NEWS_API_KEY}'
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('articles', [])
    else:
        return []

# Tâche en arrière-plan pour mettre à jour les articles toutes les minutes
def update_articles():
    global articles_data
    shown_urls = set()

    while True:
        articles = get_ev_articles()
        if articles:
            for article in articles:
                if article['url'] not in shown_urls:
                    articles_data.append(article)
                    shown_urls.add(article['url'])

        time.sleep(60)  # Rafraîchir toutes les 60 secondes

# Démarrer le thread en arrière-plan
threading.Thread(target=update_articles, daemon=True).start()

@app.route('/')
def dashboard():
    # Préparer les données pour la visualisation des voitures électriques
    vis_years = sorted(cars_data['year'].unique().tolist())
    vis_brands = sorted(cars_data['marque'].unique().tolist())
    car_data_json = cars_data.to_json(orient='records')
    
    # Charger les années disponibles pour la distribution géographique
    geo_years = get_geo_years()
    
    return render_template('dashboard.html', 
                          vis_years=vis_years, 
                          vis_brands=vis_brands, 
                          car_data=car_data_json,
                          car_gifs=json.dumps(car_gifs),
                          geo_years=geo_years)

@app.route('/news')
def news():
    return render_template('news.html', articles=articles_data)

@app.route('/chart-data')
def chart_data():
    year = request.args.get('year')
    labels, diesel, gasoline = get_prices_by_year(df, year)
    return jsonify({
        'labels': labels,
        'diesel': diesel,
        'gasoline': gasoline
    })

@app.route('/years')
def years():
    years = get_available_years(df)
    return jsonify({'years': years})

@app.route('/sales-data')
def sales_data():
    labels, values = get_sales_data()
    return jsonify({
        'labels': labels,
        'values': values
    })

@app.route('/autonomie-data')
def autonomie_data():
    labels, values, hover_labels = get_autonomie_data()
    return jsonify({
        'labels': labels,
        'values': values,
        'hover_labels': hover_labels
    })

@app.route('/carte-bornes')
def carte_bornes():
    return render_template('bornes_recharge_maroc.html')

@app.route('/co2-data')
def co2_data():
    columns, data = load_co2_data()
    return jsonify({
        'columns': columns,
        'data': data
    })

@app.route('/api/car_data')
def get_car_data():
    data = cars_data.to_dict(orient='records')
    return jsonify(data)

# Nouvelle route pour les données de distribution géographique
@app.route('/geo-distribution-data')
def geo_distribution_data():
    year = request.args.get('year')
    cities, distribution = get_geo_distribution_by_year(year)
    return jsonify({
        'cities': cities,
        'distribution': distribution,
        'selected_year': year
    })

if __name__ == '__main__':
    app.run(debug=True)