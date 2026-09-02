import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Safarnama.settings')

application = get_wsgi_application()

app = application

# Auto-create superuser on startup if env variables are present
def auto_create_superuser():
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    if username and password:
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username=username, email=email, password=password)
                print(f"✅ Superuser '{username}' created successfully!")
            else:
                print(f"ℹ️ Superuser '{username}' already exists.")
        except Exception as e:
            # Handles cases where tables are not yet created or DB is connecting
            print(f"⚠️ Skip superuser creation: {e}")

auto_create_superuser()
    