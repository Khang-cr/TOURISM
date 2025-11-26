from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import SignUpForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import login
from .models import UserProfile

# Define view functions | request -> reponse | view = request handler

# Dùng class-based view có sẵn để làm sign up vì nó sẽ tự xử lý việc tạo user và validate form

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('collect_data')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        return response

def collect_info_view(request):
    if request.method == 'POST':
        # Lay du lieu
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        age = request.POST.get('age', '')
        country = request.POST.get('country', '')
        taste = request.POST.get('taste', '')
        allergy = request.POST.get('allergy', '')
        pathology = request.POST.get('pathology', '')
        
        # Lưu vào database
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        # Tạo hoặc cập nhật UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.age = age
        profile.country = country
        profile.taste = taste
        profile.allergy = allergy
        profile.pathology = pathology
        profile.save()
        
        # chuyen sang trang hien thi thong tin
        return redirect('profile_detail')
    
    return render(request, 'registration/collect_data.html')

@login_required
def profile_detail_view(request):
    user = request.user
    
    # Lấy thông tin từ database
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = None

    context = {
        'user': user,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'date_joined': user.date_joined,
        'profile': profile,
    }

    return render(request, 'registration/profile_detail.html', context)

@login_required
# User hien tai
def ProfileView(request):
    user = request.user

    username = user.username
    email = user.email
    first_name = user.first_name
    last_name = user.last_name
    is_staff = user.is_staff
    date_joined = user.date_joined

    context = {
        'user': user,
        'username': username,
        'email': email
    }

    return render(request, 'profile.html', context)

# tat ca user
from django.contrib.auth.models import User

def user_list_view(request):
    all_users = User.objects.all()
    
    active_users = User.objects.filter(is_active=True)

    specific_user = User.objects.get(username='tên_user')
    
    return render(request, 'user_list.html', {'users': all_users})

