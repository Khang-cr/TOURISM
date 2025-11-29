from django.urls import path
from .views import SignUpView, collect_info_view, profile_detail_view, profile_edit_view, forgot_password_view, verify_otp_view, reset_password_view

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('collect-data/', collect_info_view, name='collect_data'),
    path('profile/', profile_detail_view, name='profile_detail'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),
    path('reset-password/', reset_password_view, name='reset_password'),
]