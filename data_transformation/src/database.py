import sqlite3

def init_ads_cleaned_db(db_path='scraper/data/ads_storage.db'):
    conn = sqlite3.connect(db_path, timeout=10)
    conn.isolation_level = None  # Autocommit mode to avoid locks 
    try:
        conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL for concurrent access
    except sqlite3.OperationalError:
        pass  # WAL already set or can't be set, continue anyway
    conn.isolation_level = ""  # Reset to default
    cursor = conn.cursor()
    
    # Drop and recreate to ensure schema is always up to date
    # cursor.execute("DROP TABLE IF EXISTS ads_cleaned")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ads_cleaned (
            hash_id VARCHAR(64) PRIMARY KEY,
            title VARCHAR(500),
            link VARCHAR(1000),
            neighbourhood VARCHAR(255),
            type_of_estate VARCHAR(100),
            price_m2_eur DECIMAL(10,2),
            price_m2_bgn DECIMAL(10,2),
            size_m2 DECIMAL(10,2),
            description TEXT,
            floor SMALLINT,
            akt16 BOOL,
            energy_class VARCHAR(255),
            potreblenie VARCHAR(255),
            broker_commision BOOL,
            additional_notes VARCHAR(1000),
            extras VARCHAR(500)
        )
    """)
    conn.commit()
    conn.close()

def load_data_into_ads_cleaned(cleaned_dict, conn):
    # cleaned_dict = df.to_dict()
    # cleaned_data should be in format {"hash_id", "title", etc.}
    cursor = conn.cursor()
    for item in cleaned_dict:
        print(f"updating item: {item["hash_id"]}")
        query = """
            INSERT OR IGNORE INTO ads_cleaned (
                hash_id,
                title,
                link,               
                neighbourhood,
                type_of_estate,
                price_m2_eur,
                price_m2_bgn,
                size_m2,
                description,
                floor,
                akt16,
                energy_class,
                potreblenie,
                broker_commision,
                additional_notes,
                extras
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # 2. Execute
        cursor.execute(query, (
            item["hash_id"],
            item["title"],
            item["link"],               
            item["neighbourhood"],
            item["type_of_estate"],
            item["price_m2_eur"],
            item["price_m2_bgn"],
            item["size_m2"],
            item["description"],
            item["floor"],
            item["akt16"],
            item["energy_class"],
            item["potreblenie"],
            item["broker_commision"],
            item["additional_notes"],
            item["extras"]
        ))
    conn.commit()
    return None

def query_entire_database_table(table_name: str, conn: sqlite3.Connection) -> list[dict]:
    cursor = conn.cursor()
    query = f'''
            SELECT *
            FROM {table_name}
            '''
    
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    return [dict(zip(columns, row)) for row in rows]

def add_price_column(conn):
    '''Create and populate a total price column in ads_clean.
     The column is derived from the size_m2 * price_m2_eur'''
    cursor = conn.cursor()
    
    # query_create_column = '''
    # ALTER TABLE ads_cleaned
    # ADD COLUMN total_price_eur DECIMAL(10, 2);
    # '''
    # cursor.execute(query_create_column)
    
    query_populate_column = '''
    UPDATE ads_cleaned
    SET total_price_eur = COALESCE(price_m2_eur, 0) * COALESCE(size_m2, 0)
    '''

    cursor.execute(query_populate_column)
    conn.commit()