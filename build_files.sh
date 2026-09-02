echo "BUILD START"
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations 
python manage.py migrate
python manage.py collectstatic --noinput
echo "BUILD END"