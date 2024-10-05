from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv
import psycopg2
import random
# Load environment variables
load_dotenv()

emoji = {
    1: "1️⃣",
    2: "2️⃣",
    3: "3️⃣",
    4: "4️⃣",
    5: "5️⃣",
    6: "6️⃣",
    7: "7️⃣",
    8: "8️⃣",
    9: "9️⃣",
    10: "🔟"
}

def pick_random_workout_emoji():
    emojis = ['💪🏻', '🦾', '🏋️‍♂️', '🤸‍♀️', '🚴‍♂️', '🤼‍♀️', '🏃‍♂️', '⛹️‍♂️', '🤾‍♀️', '🏊‍♂️']
    return random.choice(emojis)

def query_tasks_today(status):
    conn = psycopg2.connect(
        host="postgres",
        database="airflow_db",
        user="airflow",
        password="airflow"
    )
    today = datetime.today().date()
    print(today)
    query = f"SELECT * FROM tasks WHERE status = {status} AND DATE(assign_date) = '{today}'"
    
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()

    
    if status == 1:
        final_result = ''
        for i, result in enumerate(results):
            exercise = result[2]
            reps = result[3]
            final_result += f'{emoji[i+1]} *{exercise}*: {reps} Reps {pick_random_workout_emoji()}' + ("\n" if i != len(results)-1 else "\n\n")
    else :
        final_result = ''
        for i, result in enumerate(results):
            exercise = result[2]
            reps = result[3]
            final_result += f'{emoji[i+1]} *Task {i+1}*: {exercise} {reps} Reps' + ("\n" if i != len(results)-1 else "\n\n")
    
    conn.close()
    return final_result


# Telegram bot token and chat_id
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Function to send message to Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
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
    
    text_splitter = '===============\n\n'
    message = (
        f"{text_splitter}"
        "☀️ *Good morning!🌅 Ready to tackle the day? Let’s make progress together! 💪🏻*\n\n"
        "✨ *Here's your daily update:*\n\n"
        "📝 *You have the following tasks to complete today:*\n"
        f"{query_tasks_today(0)}"
        "Let's have a productive day! 💪"
    )

    send_morning_message = PythonOperator(
        task_id='send_morning_message',
        python_callable=send_telegram_message,
        op_args=[message],
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

    text_splitter = '===============\n\n'
    message = (
        f"{text_splitter}"
        "🌙 *Great job today!*\n\n"
        "✅ *Today, you have completed:*\n\n"
        f"{query_tasks_today(1)}"
        "Keep up the great work!"
    )
        
    send_evening_message = PythonOperator(
        task_id='send_evening_message',
        python_callable=send_telegram_message,
        op_args=[message],
    )
