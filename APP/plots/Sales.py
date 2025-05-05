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

def get_sales_data():
 
    query = text("SELECT * FROM VOITURE_DATA.PUBLIC.ELECTRI2")
    with engine.connect() as connection:
        sales = pd.read_sql(query, connection)
    labels = sales['year'].tolist()
    values = sales['sales'].tolist()
    return labels, values