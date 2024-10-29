

**- Env**
python3 -m venv __my_env
source __my_env/bin/activate
pip install -r requirements.txt
pip install --upgrade pip



**- Comands Python / Django**
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py atualizar_cotacao
python migrate_all.py
pip freeze > requirements.txt
find . -name "*.pyc" -delete
python manage.py createsuperuser
deactivate
docker-compose up --build
tail -f /home/ubuntu/logs/django.log
