-- Create database with UTF8 encoding.
CREATE DATABASE rimor_db ENCODING 'UTF8';

-- Create admin for database and grant permissions. Remember to change
-- password later!
CREATE ROLE admin_rimor;
ALTER ROLE admin_rimor WITH PASSWORD 'testpwd1';
GRANT ALL PRIVILEGES ON DATABASE rimor_db TO admin_rimor;
ALTER ROLE admin_rimor WITH LOGIN;

-- Connect to the created database.
\c rimor_db;
SET ROLE admin_rimor;

-- Create table that stores data about people.
CREATE TABLE user_data (
  user_id TEXT PRIMARY KEY,
  name TEXT,
  birthday TEXT,
  lives_in TEXT,
  comes_from TEXT,
  study TEXT,
  picture_url TEXT,
  married BOOLEAN,
  in_relationship BOOLEAN
);

-- Create table that tells that user1 has rated user2 with grade grade \in {0,1}
CREATE TABLE rating (
  user1 TEXT,
  user2 TEXT,
  grade BOOLEAN,
  trainset BOOLEAN
);

-- Create table that stores friendships.
CREATE TABLE friendship (
  user1 TEXT,
  user2 TEXT
);

-- Definitions of different log types.
CREATE TABLE log_type (
  id SERIAL PRIMARY KEY,
  name VARCHAR(10)
);

-- Create table for logs.
CREATE TABLE log (
  at_time VARCHAR(27),
  type INTEGER REFERENCES log_type,
  in_package TEXT,
  in_function TEXT,
  description TEXT
);

-- Populate table "log" with different log types.
INSERT INTO log_type (name) VALUES ('ERROR');
INSERT INTO log_type (name) VALUES ('INFO');
INSERT INTO log_type (name) VALUES ('DEBUG');
INSERT INTO log_type (name) VALUES ('WARNING');
