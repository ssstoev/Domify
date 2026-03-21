from src.database import add_price_column, init_ads_cleaned_db, load_data_into_ads_cleaned
from src.clean import clean_data
from src.transform import transform_data
import sqlite3

def main():
    conn = sqlite3.connect("scraper/data/ads_storage.db")
    # init_ads_cleaned_db()
    # df = clean_data(conn)
    # transformed_data = transform_data(df)
    # load_data_into_ads_cleaned(transformed_data, conn)
    add_price_column(conn)
    conn.close()

if __name__ == "__main__":
    main()