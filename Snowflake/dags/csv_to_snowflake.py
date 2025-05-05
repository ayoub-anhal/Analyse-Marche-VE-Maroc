from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from datetime import datetime
import pandas as pd
import os
from snowflake.connector.pandas_tools import write_pandas

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 4, 1),
    'retries': 1,
}

FILES = [
    "/opt/airflow/dags/data/electri0.csv",
    "/opt/airflow/dags/data/electri1.csv",
    "/opt/airflow/dags/data/electri2.xlsx",
    "/opt/airflow/dags/data/electri3.xlsx",
    "/opt/airflow/dags/data/electri4.xlsx",
    "/opt/airflow/dags/data/electri5.xlsx",
    "/opt/airflow/dags/data/electri6.xlsx",
]

def upload_files_to_snowflake():
    hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
    conn = hook.get_conn()

    for file_path in FILES:
        table_name = os.path.splitext(os.path.basename(file_path))[0].upper()
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Format de fichier non supporté: {file_path}")

        write_pandas(conn, df, table_name, schema='PUBLIC', auto_create_table=True, overwrite=True)
        print(f"Fichier {file_path} chargé dans la table {table_name}")

with DAG(
    dag_id='multi_files_to_snowflake',
    default_args=default_args,
    schedule=None,
    catchup=False,
) as dag:

    upload_task = PythonOperator(
        task_id='upload_files_to_snowflake',
        python_callable=upload_files_to_snowflake,
    )

    upload_task
