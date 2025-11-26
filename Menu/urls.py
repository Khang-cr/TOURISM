from django.urls import path
from . import views

urlpatterns = [
    path("dishes/", views.dish_list, name="dish_list"),
    path("restaurants/", views.restaurant_by_dish, name="restaurant_by_dish"),
]