import json
import pandas as pd
from kafka import KafkaConsumer
from datetime import datetime
from db_utils import get_connection, init_database
import time

KAFKA_BROKER = "kafka:29092"
KAFKA_TOPIC = "raw_events"
KAFKA_GROUP_ID = "cleaner_group"

def create_kafka_consumer():
    max_retries = 10
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=[KAFKA_BROKER],
                group_id=KAFKA_GROUP_ID,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                consumer_timeout_ms=10000
            )
            print("Kafka consumer connected")
            return consumer
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise

def clean_and_store():
    print("Starting cleaning job...")
    init_database()
    
    consumer = create_kafka_consumer()
    messages = []
    
    for message in consumer:
        messages.append(message.value)
    
    consumer.close()
    
    if not messages:
        print("No new messages to process")
        return
    
    print(f"Consumed {len(messages)} messages from Kafka")
    
    df = pd.DataFrame(messages)
    
    print("Cleaning data...")
    
    df["source_name"] = df["source"].apply(lambda x: x.get("name") if isinstance(x, dict) else None)
    df = df.dropna(subset=["title", "url"])    
    df["author"] = df["author"].fillna("Unknown")
    df["description"] = df["description"].fillna("")
    df["content"] = df["content"].fillna("")    
    df["published_at"] = pd.to_datetime(df["publishedAt"], errors="coerce")
    df = df.dropna(subset=["published_at"])    
    df = df.drop_duplicates(subset=["url"], keep="first")    
    df["category"] = df["source_name"].apply(lambda x: "Technology" if x and "tech" in x.lower() 
                                             else "Business" if x and "business" in x.lower()
                                             else "General")
    df["title"] = df["title"].str.strip().str.replace(r"\s+", " ", regex=True)
    df["description"] = df["description"].str.strip().str.replace(r"\s+", " ", regex=True)
    df["content"] = df["content"].str.strip().str.replace(r"\s+", " ", regex=True)
    
    df_clean = df[["source_name", "author", "title", "description", "url", 
                   "published_at", "content", "category"]].copy()
    
    print(f"Cleaned data: {len(df_clean)} records")
    
    conn = get_connection()
    
    inserted = 0
    skipped = 0

    for _, row in df_clean.iterrows():
        try:
            cursor = conn.cursor()
            # Convert timestamp to string for SQLite
            published_at_str = row["published_at"].isoformat() if pd.notna(row["published_at"]) else None
            
            cursor.execute("""
                INSERT OR IGNORE INTO events 
                (source_name, author, title, description, url, published_at, content, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["source_name"],
                row["author"],
                row["title"],
                row["description"],
                row["url"],
                published_at_str,  # Use converted string
                row["content"],
                row["category"]
            ))
            if cursor.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"Error inserting record: {e}")
            import traceback
            traceback.print_exc()
    
    conn.commit()
    conn.close()
    
    print(f"INSERTED {inserted} new records into database")
    print(f"SKIPPED {skipped} duplicates")

if __name__ == "__main__":
    clean_and_store()
