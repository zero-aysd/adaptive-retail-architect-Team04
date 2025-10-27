CITY_TO_GEO = {
    "surat":      {"geo": "IN", "sub_geo": "IN-GJ", "state": "Gujarat"},
    "ahmedabad":  {"geo": "IN", "sub_geo": "IN-GJ", "state": "Gujarat"},
    "mumbai":     {"geo": "IN", "sub_geo": "IN-MH", "state": "Maharashtra"},
    "delhi":      {"geo": "IN", "sub_geo": "IN-DL", "state": "Delhi"},
    "bangalore":  {"geo": "IN", "sub_geo": "IN-KA", "state": "Karnataka"},
}

def resolve_geo(city: str):
    city = city.strip().lower()
    if city not in CITY_TO_GEO:
        raise ValueError(f"Unsupported city: {city}")
    return CITY_TO_GEO[city]