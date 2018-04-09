# Run updates.
sudo apt-get update && sudo apt-get upgrade

# Install dependencies via apt-get.
sudo apt-get install -y nginx
sudo apt-get install -y python-dev python-pip
sudo apt-get install -y postgresql postgresql-contrib
sudo apt-get install -y libpq-dev

# Activate virtualenv and install Python modules.
pip install virtualenv
virtualenv venv
source venv/bin/activate
python -m pip install "django<2" psycopg2
deactivate

# Create database and user admin_rimor.
sudo -u postgres psql -f "$PWD/praeparo/memoria/init.sql"

# Migrate models and populate log types via django.
source venv/bin/activate
cd suasor/
python manage.py makemigrations
python manage.py migrate
python manage.py populate_log_types
deactivate
cd ..
