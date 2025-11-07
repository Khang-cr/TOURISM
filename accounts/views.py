from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import SignUpForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import login
import csv
import os
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
        # Lưu vào CSV
        user = request.user
        save_to_csv(user, {
            'first_name': first_name,
            'last_name': last_name,
            'age': age,
            'country': country,
            'taste': taste,
            'allergy': allergy,
            'pathology': pathology,
        })
        
        # chuyen sang trang hien thi thong tin
        return redirect('profile_detail')
    
    return render(request, 'registration/collect_data.html')

@login_required
def profile_detail_view(request):
    user = request.user

    additional_info = read_user_from_csv(user.username)

    first_name = additional_info.get('first_name', user.first_name) if additional_info else user.first_name
    last_name = additional_info.get('last_name', user.last_name) if additional_info else user.last_name

    context = {
    'user': user,
    'username': user.username,
    'email': user.email,
    'first_name': user.first_name,
    'last_name': user.last_name,
    'date_joined': user.date_joined,
    'additional_info': additional_info,
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

def save_to_csv(user, additional_info):
    csv_file = os.path.join(settings.BASE_DIR, 'user_data.csv')
    
    file_exists = os.path.isfile(csv_file)
    
    # Đọc dữ liệu hiện tại
    existing_data = []
    user_exists = False
    
    if file_exists:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == user.username:
                    # Cập nhật dữ liệu user hiện tại
                    user_exists = True
                    row.update({
                        'email': user.email,
                        'first_name': additional_info.get('first_name', ''),
                        'last_name': additional_info.get('last_name', ''),
                        'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                        'age': additional_info.get('age', ''),
                        'country': additional_info.get('country', ''),
                        'taste': additional_info.get('taste', ''),
                        'allergy': additional_info.get('allergy', ''),
                        'pathology': additional_info.get('pathology', ''),
                    })
                existing_data.append(row)
    
    # Nếu user chưa tồn tại, thêm mới
    if not user_exists:
        existing_data.append({
            'username': user.username,
            'email': user.email,
            'first_name': additional_info.get('first_name', ''),
            'last_name': additional_info.get('last_name', ''),
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            'age': additional_info.get('age', ''),
            'country': additional_info.get('country', ''),
            'taste': additional_info.get('taste', ''),
            'allergy': additional_info.get('allergy', ''),
            'pathology': additional_info.get('pathology', ''),
        })
    
    # Ghi lại toàn bộ dữ liệu
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['username', 'email', 'first_name', 'last_name', 'date_joined',
                     'age', 'country', 'taste', 'allergy', 'pathology']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_data)

# Doc thong tin
def read_user_from_csv(username): 
    csv_file = os.path.join(settings.BASE_DIR, 'user_data.csv')
    
    if not os.path.isfile(csv_file):
        return {}
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['username'] == username:
                return row
    
    return {}

