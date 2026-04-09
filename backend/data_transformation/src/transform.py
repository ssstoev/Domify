import pandas as pd
import numpy as np
import re

# WIP: extract number of rooms; add total_floors col/on last floor - yes/no
# clean the description col from phone numbers and other noise signs
def transform_data(df: pd.DataFrame):
    '''
    Does the following transformations:
    1. Extracts the floor number from the floor column
    2. Extract neiighbourhood name from title column
    3. Extract the estate type - garage, land, shop, etc.
    4. Extract number of rooms
    5. Calculate the total price of the estate
    Args:
        df (pd.DataFrame): dataframe
    Returns:
        cleaned_dict (dict): dictionary with transformed data    
    '''

    print("Begin transformation of data...\n")
    # 1. Extract the floor number from the floor column
    df["floor"] = df["floor"].apply(extract_floor_number)

    # 2. Extract the neighbourhood from the title col
    df['neighbourhood'] = df['title'].str.extract(r'в София, \s*(.*)', expand=False)

    # 3. Extract if its a garage or living building or area for building (parcel)
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

    # 4. Extract number of rooms
    df["nr_of_rooms"] = df["title"].apply(extract_number_of_rooms)

    # 5. Calculate the total price of the estate in EUR
    df["total_price_eur"] = df["price_m2_eur"] * df["size_m2"]

    cleaned_dict = df.to_dict('records')
    print("Finished transformation of data!\n")

    return cleaned_dict

# Helper funciton to extract floor number
def extract_floor_number(floor_string: str):
    '''Helper function to extract floor number'''
    if pd.isna(floor_string):
        return np.nan
    
    match = re.search(r'\d+', str(floor_string))
    return int(match.group()) if match else np.nan

# Helper function to extract nr of rooms 
# WIP: more professional to replace with mapping dict {"Ednostaen": 1, ...}
def extract_number_of_rooms(text):
    if "Едностаен" in text:
        return 1
    elif "Двустаен" in text:
        return 2
    elif "Тристаен" in text:
        return 3
    elif "Четиристаен" in text or "Многостаен" in text:
        return 4
    else:
        return np.nan