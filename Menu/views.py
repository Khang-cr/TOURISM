from django.shortcuts import render, get_object_or_404
from .models import Dish, Restaurant

def dish_list(request):
    dishes = Dish.objects.all()
    return render(request, "Menu/dish_list.html", {"dishes": dishes})

def restaurant_by_dish(request):
    dish_id = request.GET.get("dish")
    
    if not dish_id:
        # Show all restaurants
        restaurants = Restaurant.objects.all()
        return render(request, "Menu/restaurant_list.html", {
            "restaurants": restaurants,
            "all_restaurants": True
        })
    
    # Get the dish
    dish = get_object_or_404(Dish, id=dish_id)
    
    # Find restaurants that have this dish in their menu_list
    # The menu_list might contain dish IDs, names, or some other reference
    # You'll need to adjust this based on how the data is stored
    
    # Option 1: If menu_list contains dish IDs
    restaurants = Restaurant.objects.filter(menu_list__contains=dish_id)
    
    # Option 2: If menu_list contains dish names
    # restaurants = Restaurant.objects.filter(menu_list__contains=dish.dish_name)
    
    # Option 3: If menu_list is a comma-separated list of IDs
    # restaurants = Restaurant.objects.filter(menu_list__regex=r'\b' + dish_id + r'\b')
    
    return render(request, "Menu/restaurant_list.html", {
        "dish": dish,
        "restaurants": restaurants,
        "all_restaurants": False
    })