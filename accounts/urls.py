from django.urls import path
from .views import SignUpView, collect_info_view, profile_detail_view

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('collect-data/', collect_info_view, name='collect_data'),
    path('profile/', profile_detail_view, name='profile_detail'),
]