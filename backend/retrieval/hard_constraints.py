import os
from dotenv import load_dotenv
import re
import sqlite3
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional

load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")

class HardConstraints(BaseModel):
    neighbourhood: Optional[str] = None
    is_first_floor: Optional[bool] = None
    is_last_floor: Optional[bool] = None
    near_public_transport: Optional[bool] = None
    includes_parking: Optional[bool] = None
    furnished: Optional[bool] = None
    new_building: Optional[bool] = None
    nr_of_rooms: Optional[int] = None
    total_price_eur: Optional[float] = None
    price_m2_eur: Optional[float] = None
    appartment_floor: Optional[int] = None
    size_m2: Optional[float] = None


PROPERTY_TYPE_ROOMS = {
    'гарсониера': 1,
    'едностаен': 1,
    'едностайни': 1,
    'двустаен': 2,
    'двустайни': 2,
    'тристаен': 3,
    'тристайни': 3,
    'многостаен': 4,
    'многостайни':4
}

def extract_hard_constraints_v0(query: str):
    '''Extract the following hard constraints from a user query:
       1. Price
       2. Price p/m2
       3. Area of the estate
       4. The type of appartment (room numbers)
    '''
    query = query.lower()

    # Price: match 5-7 digit totals followed by optional currency, but NOT followed by /m2
    price_regex = r'(\d{5,7})\s*(€|eur|лв|bgn)?(?!\s*/?\s*(?:m2|м2))'
    price_m2_regex = r'(\d{3,5})\s*(€|eur|лв|bgn)?\s*/\s*(m2|м2)'
    floor_regex = r'(\d+)(?:-?(?:ви|ри|ти|и))?\s*(?:(?:от|/)\s*(\d+))?\s*(етаж|floor)'
    size_regex = r'(\d+(?:[\.,]\d+)?)\s*(кв\.?м?|m2|sqm)'
    property_type_regex = r'(едностаен|двустаен|тристаен|многостаен|гарсониера|едностайни|двустайни|тристайни|многостайни)'

    price_match = re.search(price_regex, query)
    price_m2_match = re.search(price_m2_regex, query)
    floor_match = re.search(floor_regex, query)
    size_match = re.search(size_regex, query)
    property_type_match = re.search(property_type_regex, query)

    constraints_dict = {
        'nr_of_rooms': PROPERTY_TYPE_ROOMS.get(property_type_match.group(1)) if property_type_match else None,
        'total_price_eur': int(price_match.group(1).replace(' ', '').replace(',', '')) if price_match else None,
        'price_m2_eur': int(price_m2_match.group(1)) if price_m2_match else None,
        'floor': int(floor_match.group(1)) if floor_match else None,
        'size_m2': float(size_match.group(1).replace(',', '.')) if size_match else None,
    }

    return constraints_dict

def extract_hard_constraints_v1(query: str) -> HardConstraints:
    client = OpenAI(api_key=OPEN_AI_API_KEY)

    response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """
    You extract real estate constraints from user queries.

    Rules:

        1. Extract ONLY explicitly stated or strongly implied constraints.
        2. If a constraint is not mentioned, return null.
        3. Handle negations:
        - "не на последен етаж" → is_on_last_floor = false
        - "без паркомясто" → includes_parking = false
        4. "близо до метро", "градски транспорт" → near_public_transport = true
        5. Convert all prices to EUR if possible. If unclear, still extract numeric value.
        6. Extract number of rooms from words like:
        - "едностаен" → 1
        - "двустаен" → 2
        - "тристаен" → 3
        - "многостаен" → 4
        7. Extract size in square meters (m2, кв.м).
        8. Extract floor if explicitly mentioned (e.g. "5-ти етаж").
        9. For neighbourhood, extract location names(they are from Sofia, Bulgaria) (e.g. "Младост", "Лозенец").
        10. Do NOT guess. If uncertain → null.
    """
                },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                response_format=HardConstraints
            )


    return response.choices[0].message.parsed

def build_sql_query(constraints: HardConstraints):
    _DB_PATH = os.path.join(os.path.dirname(__file__), "..", "scraper", "data", "ads_storage.db")
    conn = sqlite3.connect(_DB_PATH)
    cursor = conn.cursor()

    base_query = "SELECT * FROM ads_appartments"
    
    conditions = []
    params = []

    data = constraints.model_dump()

    for field, value in data.items():
        if value is None:
            continue

        # --- BOOLEAN FIELDS ---
        if field in [
            "is_first_floor",
            "is_last_floor",
            "near_public_transport",
            "includes_parking",
            "furnished",
            "new_building"
        ]:
            conditions.append(f"{field} = ?")
            params.append(int(value))  # SQLite uses 0/1

        # --- NUMERIC EXACT ---
        elif field in ["nr_of_rooms", "appartment_floor"]:
            conditions.append(f"{field} = ?")
            params.append(value)

        # --- NUMERIC RANGE ---
        elif field == "total_price_eur":
            conditions.append("total_price_eur <= ?")
            params.append(value)

        elif field == "price_m2_eur":
            conditions.append("price_m2_eur <= ?")
            params.append(value)

        elif field == "size_m2":
            conditions.append("size_m2 >= ?")
            params.append(value)

        # --- TEXT ---
        elif field == "neighbourhood":
            conditions.append("neighbourhood LIKE ?")
            params.append(f"%{value}%")

    # Combine conditions
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    results = cursor.execute(base_query, params)
    print(results)
    return [row[0] for row in results]
    # return base_query, params

# hard_constraints = extract_hard_constraints_v1("Търся тристаен в Дружба 2")
# print(hard_constraints)
# print(build_sql_query(hard_constraints))

# WIP: build upper & lower bounds for fields like price/size etc. and add a +10% range for prices/sizes
# WIP: E.g. a query for a 40 m2 place should include up to 45 m2
# WIP: create classes for types for constraints_dict & the hahs_ids list
# WIP: Add neighbourhood to hard constraints
# def filter_db_on_hard_constraints(constraints_dict: dict) -> list:
#     '''Receives a constraints dictionary and returns all hash_ids which fall in the criteria'''

#     _DB_PATH = os.path.join(os.path.dirname(__file__), "..", "scraper", "data", "ads_storage.db")
#     conn = sqlite3.connect(_DB_PATH)
#     base_query  = "SELECT hash_id FROM ads_cleaned"
#     cursor = conn.cursor()
#     # build a dynamic query
#     where_clauses = []
#     params = {}

#     # Exact match fields
#     exact_fields = ["nr_of_rooms", "floor"]

#     for field in exact_fields:
#         if constraints_dict.get(field) is not None:
#             where_clauses.append(f"{field} = :{field}")
#             params[field] = constraints_dict[field]

#     # Upper bound fields — user wants at most this value
#     lte_fields = ["total_price_eur", "size_m2", "price_m2_eur"]
#     for field in lte_fields:
#         if constraints_dict.get(field) is not None:
#             where_clauses.append(f"{field} <= :{field}")
#             params[field] = constraints_dict[field]

#     if not where_clauses:
#         return []
    
#     print(where_clauses)
#     full_query = f"{base_query} WHERE {' AND '.join(where_clauses)}"
#     print(full_query)

#     results = cursor.execute(full_query, params)
#     print(results)
#     return [row[0] for row in results]