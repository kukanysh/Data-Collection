import sqlite3
import os

DB_PATH = '/opt/airflow/data/app.db' 

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT,
            author TEXT,
            title TEXT,
            description TEXT,
            url TEXT UNIQUE,
            published_at TIMESTAMP,
            content TEXT,
            category TEXT,
            ingestion_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_date DATE UNIQUE,
            total_articles INTEGER,
            unique_sources INTEGER,
            avg_title_length REAL,
            avg_description_length REAL,
            top_source TEXT,
            top_source_count INTEGER,
            articles_with_author INTEGER,
            articles_with_content INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")