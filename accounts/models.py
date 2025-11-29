from django.db import models
from django.contrib.auth.models import User
from datetime import date
import random
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=100, blank=True)
    taste = models.TextField(blank=True)
    allergy = models.TextField(blank=True)
    pathology = models.TextField(blank=True)

    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    def otp_generator(self):
        self.otp_code = str(random.randint(100000, 999999))
        self.otp_created_at = timezone.now()
        self.save()
        return self.otp_code
    
    def verify_otp(self, otp):
        from django.conf import settings
        if not self.otp_code or not self.otp_created_at:
            return False
        
        time_diff = (timezone.now() - self.otp_created_at).total_seconds()
        if time_diff > settings.OTP_EXPIRY_TIME:
            return False
        
        return self.otp_code == otp
        
        