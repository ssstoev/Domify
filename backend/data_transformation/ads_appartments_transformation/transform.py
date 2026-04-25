'''Transformation functions for the ads_appartments db table'''
import numpy as np
import pandas as pd
import re 

def transform_ads_cleaned_data(ads_cleaned_df: pd.DataFrame):
    '''
    Perform the following transformations:
    1. Extracts the floor number from the floor column
    2. Extracts the total number of floors in the building
    3. Checks if it's on the first/last floor
    4. Checks if it's near a public transport (T/F)
    5. Checks if it's furnished (T/F)
    6. Checks if it includes parking/garage (T/F)
    7. Checks if it's a new building (T/F)
    8. Extract number of rooms

    Args:
        ads_cleaned_df (pd.DataFrame): dataframe from the ads_cleaned db table
    Returns:
        cleaned_dict (dict): dictionary with transformed data    
    '''

    print("Begin preparation of data for ads_appartments...\n")

    # leave only appartments from ads_cleaned
    df_appartments = ads_cleaned_df[ads_cleaned_df["type_of_estate"] == "жилище"]

    # 1. & 2. Extract floor number and total floors in one pass
    df_appartments[["appartment_floor", "total_floors"]] = df_appartments["floor"].apply(
        lambda x: pd.Series(extract_floor_number(x))
    )

    # 3. Check if it's on  first/last floor (T/F)
    df_appartments["is_last_floor"] = df_appartments.apply(lambda r: is_last_floor(r["appartment_floor"], r["total_floors"]), axis=1)
    df_appartments["is_first_floor"] = df_appartments["appartment_floor"].apply(is_first_floor)

    # 4. Checks if it's near a public transport (T/F)
    df_appartments['near_public_transport'] = df_appartments.apply(check_proximity_to_public_transport, axis=1)

    # 5. Checks if it's furnished (T/F)
    df_appartments["furnished"] = df_appartments["extras"].apply(check_if_furnished)

    # 6. Checks if it includes parking/garage (T/F)
    df_appartments["includes_parking"] = df_appartments["extras"].apply(includes_parking)

    # 7. Checks if it's a new building (T/F)
    df_appartments["new_building"] = df_appartments["extras"].apply(check_if_new_building)

    # 8. Extract number of rooms
    df_appartments["nr_of_rooms"] = df_appartments["title"].apply(extract_number_of_rooms)

    # cleaned_dict = df_appartments.to_dict('records')
    print("Finished transformation of data for ads_appartments! \n")

    return df_appartments

# Helper funciton to extract floor number
def extract_floor_number(floor_string: str):
    '''Helper function to extract floor number'''
    if pd.isna(floor_string):
        return np.nan
    
    s = str(floor_string)
    match = re.search(r'\d+', s)
    floor_number = int(match.group()) if match else np.nan

    last_match = re.search(r'(\d+)\D*$', s)
    total_floors = int(last_match.group(1)) if last_match else np.nan

    return floor_number, total_floors

# Helper function to extract nr of rooms 
NUMBER_OF_ROOMS = {
    "ЕДНОСТАЕН": 1,
    "ДВУСТАЕН": 2,
    "ТРИСТАЕН": 3,
    "ЧЕТИРИСТАЕН": 4,
    "МНОГОСТАЕН": 4
}

def extract_number_of_rooms(text):
    upper = text.upper()
    for keyword, rooms in NUMBER_OF_ROOMS.items():
        if keyword in upper:
            return rooms
    return np.nan

TRANSPORT_KEYWORDS = [
    "ГРАДСКИ ТРАНСПОРТ",
    "СПИРКА",
    "СПИРКИ",
    "АВТОБУС",
    "АВТОБУСНА СПИРКА",
    "ТРАМВАЙ",
    "ТРАМВАЙНА СПИРКА",
    "ТРОЛЕЙ",
    "ТРОЛЕЙБУС",
    "ЛИНИИ",
    "ЛИНИЯ",
    "ОБЩЕСТВЕН ТРАНСПОРТ",
    "МЕТРО",
    "МЕТРОСТАНЦИЯ",
    "МЕТРОСТ.",
    "МЕТРО СТАНЦИЯ"
]

def check_proximity_to_public_transport(row: pd.Series) -> bool:
    '''We check both the extras & the description cols'''
    string_to_check = (str(row["extras"]) + str(row["description"])).upper()
    return any(kw in string_to_check for kw in TRANSPORT_KEYWORDS)
    
def check_if_furnished(extras: str) -> bool:
    return "ОБЗАВЕДЕН" in str(extras).upper()

def includes_parking(extras: str) -> bool:
    parking_keywords = ["ПАРКОМЯСТО", "ГАРАЖ"]
    return any(kw in str(extras).upper() for kw in parking_keywords)

def is_last_floor(appartment_floor, total_floors) -> bool:
    if pd.isna(appartment_floor) or pd.isna(total_floors):
        return False
    return appartment_floor == total_floors

def is_first_floor(appartment_floor) -> bool:
    if pd.isna(appartment_floor):
        return False
    return appartment_floor == 1

def check_if_new_building(extras: str) -> bool:
    return "НОВО СТРОИТЕЛСТВО" in str(extras).upper()