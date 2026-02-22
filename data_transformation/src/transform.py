import pandas as pd
import numpy as np
import _sqlite3
import re

def transform_data(df: pd.DataFrame):

    # 1. Extract the floor number from the floor column
    df["floor"] = df["floor"].apply(extract_floor_number)

    # 2. Extract the neighbourhood from the title col
    df['neighbourhood'] = df['title'].str.extract(r'в София, \s*(.*)', expand=False)

    # 6. Extract if its a garage or living building or area for building (parcel)
    # "Гараж, паркомясто"; "Парцел"
    # we use a vectorized approach since it's fastest
    df["type_of_estate"] = np.select(
        [
            df["title"].str.contains("Гараж", na=False),
            df["title"].str.contains("Парцел", na=False),
            df["title"].str.contains("Магазин", na=False),
        ],
        ["гараж", "парцел", "магазин"],
        default="жилище"
    )

    cleaned_dict = df.to_dict('records')
    return cleaned_dict

# Helper funciton to extract floor number
def extract_floor_number(floor_string: str):
    if pd.isna(floor_string):
        return np.nan
    
    match = re.search(r'\d+', str(floor_string))
    return int(match.group()) if match else np.nan

