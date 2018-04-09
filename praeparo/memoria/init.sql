-- Create database with UTF8 encoding.
CREATE DATABASE rimor_db ENCODING 'UTF8';

-- Create admin for database and grant permissions. Remember to change
-- password later!
CREATE ROLE admin_rimor;
ALTER ROLE admin_rimor WITH PASSWORD 'testpwd1';
GRANT ALL PRIVILEGES ON DATABASE rimor_db TO admin_rimor;
ALTER ROLE admin_rimor WITH LOGIN;
