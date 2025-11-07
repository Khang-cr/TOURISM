from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

# Do Django không hỗ trợ sẵn form đăng ký nên phải tự cook

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required = True,
        label = "Email",
        widget=forms.EmailInput(attrs={'placeholder': 'example@gmail.com'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Username',
        }
        help_texts = {
            'username': 'Must have, 150 digits, only alphabet, numbers and @/./+/-/_',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = "Password"
        self.fields['password1'].help_text = (
        '<ul>'
        '<li>At least 8 digits</li>'
        '</ul>'
        )
        self.fields['password2'].label = 'Confirm Password'
        self.fields['password2'].help_text = 'Write your password again to confirm'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user