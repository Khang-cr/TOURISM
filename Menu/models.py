from django.db import models

class Dish(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    dish_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "dbo.Menu"
        app_label = "Menu"

    def __str__(self):
        return self.dish_name

class Restaurant(models.Model):
    res_id = models.CharField(primary_key=True, max_length=10)
    res_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    menu_list = models.TextField(null=True, blank=True)  # This contains the dish relationships

    class Meta:
        managed = False
        db_table = "dbo.Restaurant"
        app_label = "Menu"

    def __str__(self):
        return self.res_name

# You can remove the DishRestaurant model entirely since it's not needed