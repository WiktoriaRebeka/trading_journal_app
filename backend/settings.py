import os
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

# Ustawienia debugowania
DEBUG = True  # Dla środowiska deweloperskiego

# Dozwolone hosty (dla lokalnego serwera deweloperskiego)
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Konfiguracja bazy danych MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',    # Backend MySQL dla Django
        'NAME': os.getenv('DB_NAME'),            # Nazwa bazy danych
        'USER': os.getenv('DB_USER'),            # Użytkownik bazy danych
        'PASSWORD': os.getenv('DB_PASSWORD'),    # Hasło użytkownika
        'HOST': os.getenv('DB_HOST', 'localhost'),  # Serwer bazy danych (localhost)
        'PORT': os.getenv('DB_PORT', '3306'),    # Port MySQL (domyślnie 3306)
    }
}

# Klucz tajny - pamiętaj, aby zmienić go na produkcji
SECRET_KEY = 'your-secret-key-for-dev'

# Międzynarodowe ustawienia
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Ścieżki do plików statycznych (np. CSS, JavaScript)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'static')]

# Ścieżki do szablonów (HTML templates)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Aplikacje Django
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Konfiguracja URL
ROOT_URLCONF = 'backend.urls'

# Aplikacja WSGI
WSGI_APPLICATION = 'backend.wsgi.application'
