from data_transformation.src.database import init_ads_cleaned_db, load_data_into_ads_cleaned, rename_table
from data_transformation.src.clean import clean_data
from data_transformation.src.transform import transform_data
import sqlite3
import os

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scraper', 'data', 'ads_storage.db')

def main():
    conn = sqlite3.connect(_DB_PATH)
    rename_table("ads_cleaned", "ads_cleaned_backup", conn)
    print("Successfully renamed old ads_cleaned table to ads_cleaned_backup")
    init_ads_cleaned_db(db_path=_DB_PATH)
    df = clean_data(conn)
    transformed_data = transform_data(df)
    load_data_into_ads_cleaned(transformed_data, conn)
    # add_price_column(conn)
    conn.close()

if __name__ == "__main__":
    main()