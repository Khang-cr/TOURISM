# Nomnomly - Food Tourism Platform

## Project Description
A Django-based web application for food tourism with user registration, profile management, and food preference tracking.

## Features
- User registration and authentication
- User profile with food preferences
- Food taste, allergies, and medical conditions tracking
- Data export to CSV

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd TOURISM
```

### 2. Create virtual environment
```bash
python -m venv venv
```

### 3. Activate virtual environment
**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Apply migrations
```bash
python manage.py migrate
```

### 6. Create superuser (optional)
```bash
python manage.py createsuperuser
```

### 7. Run development server
```bash
python manage.py runserver
```

### 8. Access the application
Open browser and go to: `http://127.0.0.1:8000/`

## Project Structure
```
TOURISM/
├── Nomnomly/           # Main project folder
│   ├── settings.py     # Project settings
│   ├── urls.py         # Main URL configuration
│   └── wsgi.py
├── accounts/           # Authentication app
│   ├── views.py        # View functions
│   ├── urls.py         # App URL configuration
│   ├── forms.py        # User forms
│   └── models.py
├── templates/          # HTML templates
│   ├── registration/   # Auth templates
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── collect_data.html
│   │   └── profile_detail.html
│   └── homepage.html
├── manage.py
├── requirements.txt
└── user_data.csv       # User data storage
```

## URLs
- `/` - Homepage
- `/accounts/login/` - Login page
- `/accounts/signup/` - Registration page
- `/accounts/collect-data/` - User information collection
- `/accounts/profile/` - User profile page
- `/admin/` - Admin panel

