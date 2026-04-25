'''DB funcitons for the ads_appartments table'''

import sqlite3
import os 
import pandas as pd

def init_ads_appartments_table(db_path='scraper/data/ads_storage.db'):
    conn = sqlite3.connect(db_path, timeout=10)
    conn.isolation_level = None  # Autocommit mode to avoid locks 
    try:
        conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL for concurrent access
    except sqlite3.OperationalError:
        pass  # WAL already set or can't be set, continue anyway
    conn.isolation_level = ""  # Reset to default
    cursor = conn.cursor()
    
    # Drop and recreate to ensure schema is always up to date
    # cursor.execute("DROP TABLE IF EXISTS ads_appartments")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ads_appartments (
            hash_id VARCHAR(64) PRIMARY KEY,
            title VARCHAR(500),
            img_url VARCHAR(1000),
            link VARCHAR(1000),
            neighbourhood VARCHAR(255),
            type_of_estate VARCHAR(100),
            total_price_eur DECIMAL(10, 2),
            price_m2_eur DECIMAL(10,2),
            price_m2_bgn DECIMAL(10,2),
            size_m2 DECIMAL(10,2),
            nr_of_rooms SMALLINT,
            description TEXT,
            appartment_floor SMALLINT,
            total_floors SMALLINT,
            is_first_floor BOOL,
            is_last_floor BOOL,
            near_public_transport BOOL,
            furnished BOOL,
            includes_parking,
            new_building BOOL,
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
    print("Created ads_appartments table!")

def load_data_into_ads_appartments(appartments_df: pd.DataFrame, conn):
    appartments_dict = appartments_df.to_dict()
    appartments_dict = appartments_df.to_dict('records') if hasattr(appartments_df, 'to_dict') else appartments_df

    # appartments_data should be in format {"hash_id", "title", etc.}
    print("Loading data into ads_appartments...\n")
    cursor = conn.cursor()
    for item in appartments_dict:
        print(f"updating item: {item["hash_id"]}")
        query = f"""
            INSERT OR IGNORE INTO ads_appartments (
                hash_id,
                title,
                img_url,
                link,               
                neighbourhood,
                type_of_estate,
                total_price_eur,
                price_m2_eur,
                price_m2_bgn,
                size_m2,
                nr_of_rooms,
                description,
                appartment_floor,
                is_first_floor,
                is_last_floor,
                total_floors,
                near_public_transport,
                furnished,
                includes_parking,
                new_building,
                akt16,
                energy_class,
                potreblenie,
                broker_commision,
                additional_notes,
                extras
            ) VALUES ({", ".join(["?"] * 26)})
        """
        
        # 2. Execute
        cursor.execute(query, (
            item["hash_id"],
            item["title"],
            item["img_url"],
            item["link"],               
            item["neighbourhood"],
            item["type_of_estate"],
            item["total_price_eur"],
            item["price_m2_eur"],
            item["price_m2_bgn"],
            item["size_m2"],
            item["nr_of_rooms"],
            item["description"],
            item["appartment_floor"],
            item["total_floors"],
            item["is_first_floor"],
            item["is_last_floor"],
            item["near_public_transport"],
            item["furnished"],
            item["includes_parking"],
            item["new_building"],
            item["akt16"],
            item["energy_class"],
            item["potreblenie"],
            item["broker_commision"],
            item["additional_notes"],
            item["extras"]
        ))
    conn.commit()
    print("Finished loading data into ads_appartments!\n")

    return None