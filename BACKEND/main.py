import pandas as pd
from processing import process_recommendations
from config import RESTAURANT_DATA_PATH, MENU_DATA_PATH
from utils import get_available_tags
from validation import validate_budget, validate_coordinate, validate_distance, validate_tags

_RES50 = pd.read_csv(RESTAURANT_DATA_PATH)
_MENU50 = pd.read_csv(MENU_DATA_PATH)

def main():

    # User GPS coordinates (fake)
    USER_LAT = 10.7629 #input
    USER_LON = 106.6826 #input
    is_valid, error = validate_coordinate(USER_LAT, USER_LON)
    if not is_valid:
        print(f"{error}")
        return
    # Input distance
    MAX_DISTANCE_KM = input("Max distance (km): ")
    is_valid, result = validate_distance(MAX_DISTANCE_KM)
    if not is_valid:
        print(f"{result}")
        return
    
    # Input budget
    while True:
        budget_input = input("Enter your budget (₫): ")
        is_valid, result = validate_budget(budget_input)
        
        if is_valid:
            MAX_BUDGET = result
            break
        else:
            print(f"{result}")
    
    # Input tags
    available_tags = get_available_tags(_RES50)
    while True:
        user_tags_input = input("Enter your preferences (comma separated, or press Enter to skip): ").lower()
        is_valid, result = validate_tags(user_tags_input, available_tags)
        
        if is_valid:
            user_tags = user_tags_input
            break
        else:
            print(f"{result}")
    
    print("\nSearching for restaurants...\n")
    recommendation = process_recommendations(_RES50, USER_LAT, USER_LON, MAX_DISTANCE_KM, MAX_BUDGET, user_tags)
    
    print(f"Location: ({USER_LAT}, {USER_LON})")
    print(f"Budget: {MAX_BUDGET:,}₫")
    print(f"Max distance: {MAX_DISTANCE_KM} km")
    print(f"Preferences: {user_tags if user_tags else 'Any'}")
    print("\n" + "="*70)
    print("                 TOP 3 RESTAURANT RECOMMENDATIONS")
    print("="*70 + "\n")


    if recommendation.empty:
        print("No restaurant found matching your criteria!")
        print("\nTry:")
        print("   - Increasing your budget")
        print("   - Expanding search distance")
        print("   - Changing tag preferences")
    else:
        print(recommendation.to_string(index=False))

        print("\n" + "="*70)
        Chosen_Res = input("\nWhich restaurant you want to choose (ID): ").upper()
        
        if Chosen_Res in recommendation['restaurant_id'].values:
            restaurant_name = recommendation[recommendation['restaurant_id'] == Chosen_Res]['name'].iloc[0]
            print(f"You chose {restaurant_name}")
            print("This is the restaurant's menu:")

            print("\n" + "="*70)
            if (Chosen_Res in _MENU50['restaurant_id'].values):
                chosen_menu = _MENU50[_MENU50['restaurant_id'] == Chosen_Res]
                print(chosen_menu.to_string(index=False))
        else:
            print(f"Invalid restaurant ID. Please choose from: {', '.join(recommendation['restaurant_id'].values)}")
    
if __name__ == "__main__":
    main()