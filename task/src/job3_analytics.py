import pandas as pd
from datetime import datetime, timedelta
from db_utils import get_connection, init_database

def compute_daily_analytics():
    print("Starting daily analytics job...")
    init_database()
    
    conn = get_connection()
    
    yesterday = (datetime.now() - timedelta(days=1)).date()
    
    query = 'SELECT * FROM events WHERE DATE(published_at) = ?'  
    df = pd.read_sql_query(query, conn, params=(yesterday,))
    
    if df.empty:
        print(f"No data for {yesterday}")
        conn.close()
        return
    
    print(f"Analyzing {len(df)} records for date: {yesterday}")
    
    analytics = {}
    
    analytics['summary_date'] = yesterday
    analytics['total_articles'] = len(df)
    analytics['unique_sources'] = df['source_name'].nunique()    
    analytics['avg_title_length'] = df['title'].str.len().mean()
    analytics['avg_description_length'] = df['description'].str.len().mean()
    analytics['articles_with_author'] = df[df['author'] != 'Unknown'].shape[0]
    analytics['articles_with_content'] = df[df['content'].str.len() > 0].shape[0]
    
    top_source = df['source_name'].value_counts().head(1)
    if not top_source.empty:
        analytics['top_source'] = top_source.index[0]
        analytics['top_source_count'] = int(top_source.values[0])
    else:
        analytics['top_source'] = None
        analytics['top_source_count'] = 0

    print(f"Total: {analytics['total_articles']}, Sources: {analytics['unique_sources']}")
    
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO daily_summary 
        (summary_date, total_articles, unique_sources, avg_title_length, 
         avg_description_length, top_source, top_source_count, 
         articles_with_author, articles_with_content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        analytics['summary_date'],
        analytics['total_articles'],
        analytics['unique_sources'],
        analytics['avg_title_length'],
        analytics['avg_description_length'],
        analytics['top_source'],
        analytics['top_source_count'],
        analytics['articles_with_author'],
        analytics['articles_with_content']
    ))
    
    conn.commit()
    conn.close()
    print("Daily analytics stored")

if __name__ == '__main__':
    compute_daily_analytics()