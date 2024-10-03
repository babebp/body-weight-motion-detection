from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram bot token and chat_id
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Function to send message to Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise ValueError(f"Failed to send message: {response.text}")

# Default arguments for both DAGs
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG for sending morning message at 9:00 AM
with DAG(
    'telegram_morning_message',
    default_args=default_args,
    description='Send morning message to Telegram at 9:00 AM',
    schedule_interval='0 9 * * *',  # Every day at 9:00 AM
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as morning_dag:

    send_morning_message = PythonOperator(
        task_id='send_morning_message',
        python_callable=send_telegram_message,
        op_args=["Good morning! This is your 9:00 AM message."],
    )

# DAG for sending evening message at 8:00 PM
with DAG(
    'telegram_evening_message',
    default_args=default_args,
    description='Send evening message to Telegram at 8:00 PM',
    schedule_interval='0 20 * * *',  # Every day at 8:00 PM
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as evening_dag:

    send_evening_message = PythonOperator(
        task_id='send_evening_message',
        python_callable=send_telegram_message,
        op_args=["Good evening! This is your 8:00 PM message."],
    )
