from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    taste = models.TextField(blank=True)
    allergy = models.TextField(blank=True)
    pathology = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
