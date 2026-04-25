import sqlite3
import os
from data_transformation.ads_appartments_transformation.database import init_ads_appartments_table, load_data_into_ads_appartments
from data_transformation.ads_appartments_transformation.transform import transform_ads_cleaned_data
from data_transformation.ads_cleaned_transformation.database import init_ads_cleaned_db, load_data_into_ads_cleaned, rename_table
from data_transformation.ads_cleaned_transformation.clean import clean_ads_raw_data
from data_transformation.ads_cleaned_transformation.transform import transform_data

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scraper', 'data', 'ads_storage.db')

def main():
    conn = sqlite3.connect(_DB_PATH)
    
    # create backup of previous ads_cleaned (just in case)
    # rename_table("ads_cleaned", "ads_cleaned_backup", conn)
    # print("Successfully renamed old ads_cleaned table to ads_cleaned_backup \n")

    # perform ads_cleaned transformation & upload in db table
    init_ads_cleaned_db(db_path=_DB_PATH)
    ads_cleaned_df = clean_ads_raw_data(conn)
    ads_cleaned_df_transformed = transform_data(ads_cleaned_df)
    load_data_into_ads_cleaned(ads_cleaned_df_transformed, conn)

    # perform ads_appartments transformation & upload in db table
    init_ads_appartments_table(db_path=_DB_PATH)
    ads_appartments_df = transform_ads_cleaned_data(ads_cleaned_df_transformed)
    load_data_into_ads_appartments(ads_appartments_df, conn)

    # add_price_column(conn)
    conn.close()

if __name__ == "__main__":
    main()