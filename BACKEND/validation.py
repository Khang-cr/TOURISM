from config import VN_LAT_MAX,VN_LAT_MIN,VN_LON_MAX,VN_LON_MIN
import re
from difflib import get_close_matches
def validate_budget(budget_input):
    try:
        budget = int(budget_input)
        
        if budget <= 0:
            return False, "Budget must be positive!"
        
        if budget < 20000:
            return False, "Budget too low!"

        return True, budget
    except (ValueError, TypeError):
        return False, "Budget must be a number!"
    
def validate_distance(distance_input):
    try:
        distance = float(distance_input)
        if distance <= 0:
            return False, "Distance must be positive!"
        return True, distance
    except ValueError:
        return False, "Distance must be a number!"

def validate_coordinate(lat, lon):
    if not (-90<=lat<=90):
        return False, f"Invalid latitude: {lat}. Must be between -90 and 90!"
    if not (-180<=lon<=180):
        return False, f"Invalid lonitude: {lon}. Must be betwenn -180 and 180!"
    
    # Kiem tra toa do co nam o VN khong
    if not (VN_LAT_MIN <= lat <= VN_LAT_MAX and VN_LON_MIN <= lon <= VN_LON_MAX):
        return False, f"Coordinate ({lat},{lon} are outside Vietname!)"

    return True, None


def validate_tags(tags_input, availablle_tags):
    if not tags_input or tags_input.strip() == "":
        return True, []

    user_tags = [tag.strip().lower() for tag in tags_input.split(',')]
    user_tags = [tag for tag in user_tags if tag]

    if not user_tags:
        return False, "No valid tags provided!"
    
    restaurant_tags = set(availablle_tags)

    invalid_tags = []
    valid_tags = []

    for tags in user_tags:
        if tags in restaurant_tags:
            valid_tags.append(tags)
        else:
            invalid_tags.append(tags)

    if invalid_tags:
        suggestion = get_close_matches(invalid_tags[0], restaurant_tags)
        return False, f"Tag {invalid_tags[0]} not found! Did you mean: {', '.join(suggestion[:3])}?"
    
    return True, valid_tags