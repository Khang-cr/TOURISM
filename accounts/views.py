from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import SignUpForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import login
from .models import UserProfile
from .constants import TASTE_CHOICES, ALLERGY_CHOICES, PATHOLOGY_CHOICES
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

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
        date_of_birth = request.POST.get('date_of_birth', '')
        language = request.POST.get('language', '')

        taste = ', '.join(request.POST.getlist('taste'))
        allergy = ', '.join(request.POST.getlist('allergy'))
        pathology = ', '.join(request.POST.getlist('pathology'))
        
        # Lưu vào database
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        # Tạo hoặc cập nhật UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.date_of_birth = request.POST.get('date_of_birth', '')
        profile.language = language
        profile.taste = taste
        profile.allergy = allergy
        profile.pathology = pathology
        profile.save()
        
        # chuyen sang trang hien thi thong tin
        return redirect('profile_detail')
    
    context = {
        'taste_choices': TASTE_CHOICES,
        'allergy_choices': ALLERGY_CHOICES,
        'pathology_choices': PATHOLOGY_CHOICES,
    }

    return render(request, 'registration/collect_data.html', context)

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

@login_required
def profile_edit_view(request):
    user = request.user

    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()

        profile.date_of_birth = request.POST.get('date_of_birth', '')
        profile.language = request.POST.get('language', '')
        profile.taste = ', '.join(request.POST.getlist('taste'))
        profile.allergy = ', '.join(request.POST.getlist('allergy'))
        profile.pathology = ', '.join(request.POST.getlist('pathology'))
        profile.save()
        
        return redirect('profile_detail')
    
    context = {
        'user': user,
        'profile': profile,
        'taste_choices': TASTE_CHOICES,
        'allergy_choices': ALLERGY_CHOICES,
        'pathology_choices': PATHOLOGY_CHOICES,
        'selected_tastes': profile.taste.split(', ') if profile.taste else [],
        'selected_allergies': profile.allergy.split(', ') if profile.allergy else [],
        'selected_pathologies': profile.pathology.split(', ') if profile.pathology else [],
    }

    return render(request, 'registration/profile_edit.html', context)

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')

        try:
            user = User.objects.get(email=email)
            profile, created = UserProfile.objects.get_or_create(user=user)

            otp = profile.otp_generator()

            subject = 'Password Reset OTP - Nomnomly'
            message = f'''
            Hello {user.username},
            
            Your OTP code for password reset is : {otp}
            
            This code will expire in 5 minutes.

            Best regards,
            Nomnomly Team
            '''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently = False,
            )

            request.session['reset_email'] = email
            messages.success(request, 'An OTP has been sent to your email!')
            return redirect('verify_otp')
        except User.DoesNotExist:
            messages.error(request, 'Email not found!')
    return render(request, 'registration/forgot_password.html')

def verify_otp_view(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Please start from forgot password page.')
        return redirect('forgot_password')
    if request.method == 'POST':
        otp = request.POST.get('otp', '')

        try:
            user = User.objects.get(email=email)
            profile = user.profile

            if profile.verify_otp(otp):
                request.session['verified_user_id'] = user.id
                return redirect('reset_password')
            else:
                messages.error(request, 'Invalid or expired OTP code!')
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            messages.error(request, 'An error occurred!')

    return render(request, 'registration/verify_otp.html', {'email': email})

def reset_password_view(request):
    user_id = request.session.get('verified_user_id')

    if not user_id:
        messages.error(request, 'Please verify OTP first!')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
        elif len(password1) < 8:
            messages.error(request, 'Pass word must be at least 8 characters!')
        else:
            try:
                user = User.objects.get(id = user_id)
                user.set_password(password1)
                user.save()

                profile = user.profile
                profile.otp_code = None
                profile.otp_created_at = None
                profile.save()

                del request.session['verified_user_id']
                del request.session['reset_email']

                messages.success(request, 'Password reset successfully!')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'Error occurred!')

    return render(request, 'registration/reset_password.html')
