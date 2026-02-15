import sqlite3
import datetime as dt

def init_db(db_path='data/ads_storage.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ads_raw (
            hash_id TEXT PRIMARY KEY,
            title TEXT,
            link TEXT,
            price_m2_eur TEXT,
            price_m2_bgn TEXT,
            size_m2 TEXT,
            description TEXT,
            floor TEXT,
            akt16 TEXT,
            energy_class TEXT,
            potreblenie TEXT,
            broker_commision TEXT,
            additional_notes TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME,
            last_updated DATETIME
        )
    """)
    conn.commit()
    conn.close()

def insert_ad(cursor, ad_data):
    '''Initial insert of ad into the database'''
    for hash_id, info in ad_data.items():
        # 1. Prepare the Query
        time = dt.datetime.now()
        query = """
            INSERT OR IGNORE INTO ads_raw (
                hash_id, title, link, status, created_at, last_updated
            ) VALUES (?, ?, ?, 'pending', ?, ?)
        """
        
        # 2. Execute
        cursor.execute(query, (
            hash_id,
            info.get('ad_title'),
            info.get('link_to_ad'),
            time, 
            time
        ))

        # print(f"Successfully inserted item {hash_id}")

def fetch_pending_ads(): 
    query = '''
    SELECT * FROM ads_raw WHERE status = "pending"
'''