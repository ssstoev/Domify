import sqlite3
import datetime as dt

def init_db(db_path='scraper/data/ads_storage.db'):
    conn = sqlite3.connect(db_path, timeout=10)
    conn.isolation_level = None  # Autocommit mode to avoid locks
    try:
        conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL for concurrent access
    except sqlite3.OperationalError:
        pass  # WAL already set or can't be set, continue anyway
    conn.isolation_level = ""  # Reset to default
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

def fetch_pending_ads(conn, batch_size=100):
    cursor = conn.cursor()
    cursor.execute("BEGIN IMMEDIATE")
    query = '''
    SELECT * FROM ads_raw WHERE status IN ("pending", "processing") LIMIT ?
    '''
    cursor.execute(query, (batch_size,))

    pending = cursor.fetchall()
    pending_list = [{"hash_id": row[0], "link": row[1]} for row in pending]

    # Or if you want column names from cursor.description
    columns = [desc[0] for desc in cursor.description]
    pending_list = [dict(zip(columns, row)) for row in pending]
    
    cursor.executemany("""
        UPDATE ads_raw
        SET status = 'processing'
        WHERE hash_id = ?
    """, [(ad["hash_id"],) for ad in pending_list])

    conn.commit()
    return pending_list

def update_records(conn, updates):
    cursor = conn.cursor()

    for update in updates:
        cursor.execute("""
            UPDATE ads_raw 
            SET description = ?, price_m2_eur = ?, price_m2_bgn = ?,
                       size_m2 = ?, floor = ?, akt16 = ?, energy_class = ?,
                       potreblenie = ?, broker_commision = ?, additional_notes = ?,
                       status = 'done', last_updated = ?
            WHERE hash_id = ?
        """, 
            (update["description"], update["price_m2_eur"], update["price_m2_bgn"],
              update["size_m2"], update["floor"], update["akt16"], update["energy_class"],
               update["potreblenie"], update["broker_commision"], update["additional_notes"],
               dt.datetime.now(), update["hash_id"])
        )
    conn.commit()
    return None

## We missed extracting data for 1 column so we will backfill it without scraping everything again from scratch

def create_missing_col(new_db_col_name: str, db_path='scraper/data/ads_storage.db'): 
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query_create_col = f'''
        ALTER TABLE ads_raw ADD COLUMN {new_db_col_name} TEXT
    '''
    cursor.execute(query_create_col)
    conn.commit()
    conn.close()

def fetch_missing_extras_rows(conn, batch_size=20):
    '''This funciton fetches the rows where the extras column is NULL'''

    cursor = conn.cursor()
    cursor.execute("BEGIN IMMEDIATE")
    query = '''
    SELECT hash_id, link FROM ads_raw WHERE extras is NULL LIMIT ?
    '''
    cursor.execute(query, (batch_size,))

    extras = cursor.fetchall()
    extras_list = [{"hash_id": row[0], "link": row[1]} for row in extras]

    return extras_list

def add_missing_col_information(conn, 
                                db_col_to_update: str, 
                                updates: dict, 
                                values_to_update_with:str):
    
    '''Add the additional scraped info to the col'''
    cursor = conn.cursor()

    query_update_col = f'''
        UPDATE ads_raw
        SET {db_col_to_update} = ?
        WHERE hash_id = ?    
    '''

    for update in updates:
        cursor.execute(query_update_col, 
                       (update[f"{values_to_update_with}"], update["hash_id"]))
    
    conn.commit()
    conn.close()
