# Suasor -- Likeable-person recommender

Suasor is meant for everyone that wants to find new people or just experiment around
with machine learning. Originally meant as a project for Data Science class, but Suasor
is going to be available 24/7 when developing is finished and all tiny bits of security are taken care of.

## Idea

Idea behind Suasor, mainly it's core -- *praedicto* --, is for user to decide on some
training set of people whether he/she likes that person or not (by appearance, interests,
origin, whatever, the *praedicto* will find out what you prefer). After the manual grading
is done, Suasor now trains itself based on your input and input from others whether you like
the rest of people in database or not and now it is up to you to decide if you really like
the person or not but the idea is to get as close to getting it correct as possible.

## How it works?

Suasor consists of two parts:
 * **strigili** aka scrapper. This is a Python module that given a search root
 scraps Facebook, going from the given root to root's top 20 friends, to their friends, etc.
 It scraps various data about users and builds a database, that is just growing
 by each run with different root.
 * **praedicto** aka predictor. Written in R (and Python), takes care about all machine
 learning stuff, from selecting training set for particular user to deciding which
 people to recommend. Convolutional neural networks is the main thing.

Taking care for communication between user and server is Django, the best web framework.

## Setup notes
If you want to somehow experiment with the code, first read [LICENSE](https://github.com/campovski/suasor/blob/master/LICENSE).

<hr>

**Requirements** Linux (might need to change application manager in `rex.sh`).

<hr>

First, clone the repository.

```
git clone https://github.com/campovski/suasor
```

Now navigate to directory with Suasor and run the dependency manager. You will be asked for
your administrator password, because some things need to be installed and some permissions given.

```
cd suasor
sudo bash praeparo/rex.sh
```

After the script is done, you have a fully functional Suasor distribution, with your own
database. Now, you need to activate virtual environment by

```
source venv/bin/activate
```

and now navigate into suasor directory

```
cd suasor
```

This is the core of the program, fire up server by executing

```
python manage.py runserver
```

*Note: change* `suasor/local_settings.py` *file with proper settings.*
