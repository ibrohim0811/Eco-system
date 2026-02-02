# winget install casey.just
set shell := ["powershell", "-Command"]
mig:
    python manage.py makemigrations
    python manage.py migrate

migrate:
    python manage.py makemigrations apps
    python manage.py migrate

run:
    python manage.py runserver


setup:
    pip install -r requirements.txt
    just mig

admin:
    python manage.py createsuperuser

cd:
    cd "C:\Users\ucer\OneDrive\Desktop\other projects\Eco system\bot"