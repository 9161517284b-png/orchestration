from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import requests

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

def fetch_iss_position():
    url = "http://api.open-notify.org/iss-now.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    timestamp = datetime.utcfromtimestamp(data['timestamp'])
    latitude = float(data['iss_position']['latitude'])
    longitude = float(data['iss_position']['longitude'])
    return {"timestamp": timestamp, "latitude": latitude, "longitude": longitude}

def insert_into_db(**context):
    data = context['ti'].xcom_pull(task_ids='fetch_iss_position')
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    insert_sql = """
    INSERT INTO iss_position (timestamp, latitude, longitude)
    VALUES (%s, %s, %s)
    ON CONFLICT (timestamp) DO NOTHING;
    """
    pg_hook.run(insert_sql, parameters=(data['timestamp'], data['latitude'], data['longitude']))

with DAG(
    'iss_position_dag',
    default_args=default_args,
    description='DAG to fetch ISS position and load into Postgres',
    schedule_interval='*/30 * * * *',
    start_date=datetime(2025, 10, 30),
    catchup=False,
    tags=['example'],
) as dag:

    fetch_task = PythonOperator(
        task_id='fetch_iss_position',
        python_callable=fetch_iss_position
    )
    
    load_task = PythonOperator(
        task_id='load_into_db',
        python_callable=insert_into_db,
        provide_context=True
    )

    fetch_task >> load_task
