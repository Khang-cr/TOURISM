from math import radians, sin, cos, sqrt, atan2
from config import PRICE_MAP
import re

# Ham tinh khoang cach duong chim bay tu user den restaurant
def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371 # ban kinh Trai Dat Km
    lat1, lon1, lat2, lon2 = map(radians, [lat1,lon1,lat2,lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance 

# Chuan hoa tags
def standardize_tags(tag_series):
    return tag_series.str.lower().str.replace(', ', '|').str.replace(',', '|').str.strip()

# chuyen doi '₫' thanh gia tri so hoc
def standardize_price(price_range_series):
    return price_range_series.map(PRICE_MAP)

def get_available_tags(df):
    all_tags = set()
    for tags_str in df['tags'].dropna():
        tags_list = [t.strip().lower() for t in re.split(r'[,|]', tags_str)]
        all_tags.update(tags_list)
    
    return sorted(all_tags)

def suggest_similar_tags(input_tag, available_tags):
    from difflib import get_close_matches
    suggestions = get_close_matches(input_tag, available_tags, n = 3, cutoff=0.6)
    return suggestions if suggestions else list(available_tags)[:3]
