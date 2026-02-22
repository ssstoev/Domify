# data_transformation/main.py
from src.database import init_db, load_transformed_data
from src.clean import clean_data
from src.transform import transform_data
import sqlite3

def main():
    conn = sqlite3.connect("scraper/data/ads_storage.db")
    init_db()
    df = clean_data(conn)
    df = transform_data(df)
    load_transformed_data(df, conn)
    conn.close()

if __name__ == "__main__":
    main()