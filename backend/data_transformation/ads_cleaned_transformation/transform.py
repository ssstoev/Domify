import pandas as pd
import numpy as np
import re

# WIP: clean the description col from phone numbers and other noise signs
def transform_data(df: pd.DataFrame):
    '''
    Does the following transformations:
    1. Extract neighbourhood name from title column
    2. Extract the estate type - garage, land, shop, house.
    3. Calculate the total price of the estate
    Args:
        df (pd.DataFrame): dataframe
    Returns:
        cleaned_dict (dict): dictionary with transformed data    
    '''

    print("Begin transformation of data...\n")

    # 1. Extract the neighbourhood from the title col
    df['neighbourhood'] = df['title'].str.extract(r'в София, \s*(.*)', expand=False)

    # 2. Extract if its a garage or living building or area for building (parcel)
    # "Гараж, паркомясто"; "Парцел"
    # we use a vectorized approach since it's fastest
    df["type_of_estate"] = np.select(
        [
            df["title"].str.contains("Гараж", na=False),
            df["title"].str.contains("Парцел", na=False),
            df["title"].str.contains("Магазин", na=False),
            df["title"].str.contains("Къща", na=False)
        ],
        ["гараж", "парцел", "магазин", "къща"],
        default="жилище"
    )

    # 3. Calculate the total price of the estate in EUR
    df["total_price_eur"] = df["price_m2_eur"] * df["size_m2"]

    print("Finished transformation of data!\n")

    return df