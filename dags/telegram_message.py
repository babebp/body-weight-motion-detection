from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv

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

# Define the DAG and schedule
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'telegram_message',
    default_args=default_args,
    description='Send message to Telegram at 9 AM and 8 PM daily',
    schedule_interval='0 9,20 * * *',  # Every day at 9:00 AM and 8:00 PM
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    send_morning_message = PythonOperator(
        task_id='send_morning_message',
        python_callable=send_telegram_message,
        op_args=["Good morning! This is your 9:00 AM message."],
    )

    send_evening_message = PythonOperator(
        task_id='send_evening_message',
        python_callable=send_telegram_message,
        op_args=["Good evening! This is your 8:00 PM message."],
    )

    send_morning_message >> send_evening_message
