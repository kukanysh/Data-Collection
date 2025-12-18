from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/opt/airflow/src')

from job2_cleaner import clean_and_store

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 12, 16),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'job2_hourly_cleaning',
    default_args=default_args,
    description='DAG 2: Hourly batch job - read Kafka, clean data, write to SQLite',
    schedule_interval='@hourly',
    catchup=False,
    tags=['cleaning', 'kafka', 'sqlite']
)

clean_task = PythonOperator(
    task_id='clean_and_store_data',
    python_callable=clean_and_store,
    dag=dag
)