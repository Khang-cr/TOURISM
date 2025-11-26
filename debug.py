# In Django shell
from Menu.models import Dish, Restaurant, DishRestaurant

# Get some dishes and restaurants
dishes = Dish.objects.all()[:2]  # First 2 dishes
restaurants = Restaurant.objects.all()[:2]  # First 2 restaurants

print("Creating relationships...")
for dish in dishes:
    for restaurant in restaurants:
        # Create relationship if it doesn't exist
        if not DishRestaurant.objects.filter(dish=dish, restaurant=restaurant).exists():
            DishRestaurant.objects.create(dish=dish, restaurant=restaurant)
            print(f"✓ {dish.dish_name} -> {restaurant.res_name}")

print(f"Total relationships: {DishRestaurant.objects.count()}")