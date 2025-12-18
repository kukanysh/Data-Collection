import os
import json
import time
import requests
from kafka import KafkaProducer
from datetime import datetime

KAFKA_BROKER = 'kafka:29092'
KAFKA_TOPIC = 'raw_events'
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'a4490e3c26c14d15b30a06ea958a1c2a')
NEWS_API_URL = 'https://newsapi.org/v2/top-headlines'

def create_kafka_producer():
    max_retries = 15
    retry_delay = 10

    print(f"Attempting to connect to Kafka at {KAFKA_BROKER}...")
    
    for attempt in range(max_retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                max_block_ms=10000,
                request_timeout_ms=30000
            )
            print("Kafka producer connected successfully")
            return producer
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print("FAILED TO CONNECT")
                raise

def fetch_news_data():
    params = {
        'apiKey': NEWS_API_KEY,
        'country': 'us',
        'pageSize': 100
    }
    
    try:
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'ok':
            return data.get('articles', [])
        else:
            print(f"API Error: {data.get('message', 'Unknown error')}")
            return []
    # except requests.exceptions.RequestException as e:
    #     print(f"Network error fetching news: {e}")
    #     return []
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def produce_to_kafka(duration_minutes=2):
    producer = create_kafka_producer()
    start_time = time.time()
    iteration = 0
    total_sent = 0
    
    print(f"Starting continuous ingestion for {duration_minutes} minutes...")
    
    while time.time() - start_time < duration_minutes * 60:
        iteration += 1
        print(f"\n--- Iteration {iteration} at {datetime.now()} ---")
        
        articles = fetch_news_data()
        
        if articles:
            for article in articles:
                message = {
                    'source': article.get('source', {}),
                    'author': article.get('author'),
                    'title': article.get('title'),
                    'description': article.get('description'),
                    'url': article.get('url'),
                    'publishedAt': article.get('publishedAt'),
                    'content': article.get('content'),
                    'fetched_at': datetime.now().isoformat()
                }
                producer.send(KAFKA_TOPIC, value=message)
            
            producer.flush()
            print(f"Sent {len(articles)} articles to Kafka topic '{KAFKA_TOPIC}'")
        else:
            print("No articles fetched")
        
        time.sleep(120)
    
    producer.close()
    print("Producer finished successfully")

if __name__ == '__main__':
    produce_to_kafka()