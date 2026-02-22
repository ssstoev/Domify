import pandas as pd
import numpy as np
import _sqlite3
import re

def clean_data(conn: _sqlite3.Connection):
    '''Clean the ads_raw table. 
     - Convert fileds to numeric
     - Convert fields to bool
     '''

    # 1. Load into a pandas DF
    # Fetch all processed data
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ads_raw WHERE status = 'done'")
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()

    # Convert to DataFrame
    # conn.close()
    df = pd.DataFrame(rows, columns=columns)

    # 2. Convert to numeric fields
    cols_to_strip = ["price_m2_eur", "price_m2_bgn"]
    df = df.copy()
    df[cols_to_strip] = df[cols_to_strip].apply(lambda row: row.str.replace(" ", ""))
    df[cols_to_strip] = df[cols_to_strip].astype(float)

    # convert the size_m2 col separately as there aren't whitespaces to strip there
    df["size_m2"] = pd.to_numeric(df["size_m2"])

    # 3. Convert cols to bool
    bool_cols = ["akt16", "broker_commision"]
    for col in bool_cols:
        df[f"{col}"] = df[f"{col}"].apply(convert_to_bool)
        # drop the old columns
        # df.drop(labels=col, axis=1, inplace=True)

    return df

# Helper function to convert yes/no columns to bool
def convert_to_bool(value: str):
    if pd.isna(value):
        return np.nan
    
    elif value.upper() == "ДА":
        return True

    else:
        return False