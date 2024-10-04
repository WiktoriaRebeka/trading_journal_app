import os
from dotenv import load_dotenv

load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',    # Backend MySQL dla Django
        'NAME': os.getenv('DB_NAME'),            # Nazwa bazy danych
        'USER': os.getenv('DB_USER'),            # Użytkownik bazy danych
        'PASSWORD': os.getenv('DB_PASSWORD'),    # Hasło użytkownika
        'HOST': os.getenv('DB_HOST', 'localhost'),  # Serwer bazy danych (localhost dla lokalnej)
        'PORT': os.getenv('DB_PORT', '3306'),    # Port, na którym działa MySQL (domyślnie 3306)
    }
}
