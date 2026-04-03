import re

PROPERTY_TYPE_ROOMS = {
    'гарсониера': 1,
    'едностаен': 1,
    'двустаен': 2,
    'тристаен': 3,
    'многостаен': 4,
}

# WIP : Create Logic for extracting the hard constraints ( price, floor, size, neighbourhood, etc.)
def extract_hard_constraints(query: str) -> dict:
    query = query.lower()

    # Price: match 5-7 digit totals followed by optional currency, but NOT followed by /m2
    price_regex = r'(\d{5,7})\s*(€|eur|лв|bgn)?(?!\s*/?\s*(?:m2|м2))'
    price_m2_regex = r'(\d{3,5})\s*(€|eur|лв|bgn)?\s*/\s*(m2|м2)'
    floor_regex = r'(\d+)(?:-?(?:ви|ри|ти|и))?\s*(?:(?:от|/)\s*(\d+))?\s*(етаж|floor)'
    area_regex = r'(\d+(?:[\.,]\d+)?)\s*(кв\.?м?|m2|sqm)'
    property_type_regex = r'(едностаен|двустаен|тристаен|многостаен|гарсониера)'

    price_match = re.search(price_regex, query)
    price_m2_match = re.search(price_m2_regex, query)
    floor_match = re.search(floor_regex, query)
    area_match = re.search(area_regex, query)
    property_type_match = re.search(property_type_regex, query)

    constraints_dict = {
        'nr_of_rooms': PROPERTY_TYPE_ROOMS.get(property_type_match.group(1)) if property_type_match else None,
        'price': int(price_match.group(1).replace(' ', '').replace(',', '')) if price_match else None,
        'price_m2': int(price_m2_match.group(1)) if price_m2_match else None,
        'floor': int(floor_match.group(1)) if floor_match else None,
        'area': float(area_match.group(1).replace(',', '.')) if area_match else None,
    }

    return constraints_dict

query = "Търся едностаен за 160000 EUR (40 кв) на 4-ти етаж"
print(extract_hard_constraints(query))