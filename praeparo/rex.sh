# Run updates.
sudo apt-get update && sudo apt-get upgrade

# Install dependencies via apt-get.
sudo apt-get install -y nginx
sudo apt-get install -y python-dev python-pip
sudo apt-get install -y postgresql postgresql-contrib
sudo apt-get install -y libpq-dev

# Create directories for indicina.
mkdir "$PWD/suasor/indicina"
mkdir "$PWD/suasor/indicina/tmp"
mkdir "$PWD/suasor/indicina/persona"
mkdir "$PWD/suasor/indicina/imaginibus"
mkdir "$PWD/suasor/indicina/diarium"
sudo chmod -R 777 "$PWD/suasor/indicina"

# Activate virtualenv and install Python modules.
pip install virtualenv
virtualenv venv
sudo chmod -R 777 venv
source venv/bin/activate
python -m pip install "django<2" psycopg2
pip install requests
deactivate

# Create database and user admin_rimor.
sudo -u postgres psql -f "$PWD/praeparo/memoria/init.sql"

# Create dummy local_settings.py file so you can instantly run the server.
printf "SECRET_KEY = 'vsdjhv093rvo32l2mlfk32l2VJsvormkm'\n\n\
DATABASES = {\n\
    'default': {\n\
      'ENGINE': 'django.db.backends.postgresql_psycopg2',\n\
      'NAME': 'rimor_db',\n\
      'USER': 'admin_rimor',\n\
      'PASSWORD': 'testpwd1',\n\
      'HOST': 'localhost',\n\
      'PORT': ''\n\
    }\n\
}" > suasor/suasor/local_settings.py

# Migrate models and populate log types via django.
source venv/bin/activate
cd suasor/
python manage.py makemigrations
python manage.py makemigrations suasor
python manage.py migrate
python manage.py populate_log_types
deactivate
cd ..
