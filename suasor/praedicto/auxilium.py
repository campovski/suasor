import random

from suasor.models import UserData, Rating


TRAIN_SET_SIZE = 100

"""
    Get the train set.
    @param user_id: Facebook ID of user that requested the search
    @return train set
"""
def get_train_set(user_id):
    users = list(UserData.objects.all())
    n_max = len(users)
    train = set()

    # While we don't have desired number of people, generate new ones.
    while len(train) < TRAIN_SET_SIZE:
        user = users[random.randint(1, n_max)]

        # If user found is not the user that requested the search, we can add
        # him/her to trainset.
        if user.user_id != user_id:
            train.add(user)

    return train

"""
    Saves grades of people in trainset to database.
    @param user_id: Facebook ID of user that graded the trainset
    @param ts_grades: 2D array, where each row contains UserData and grade
"""
def save_train_grades(user_id, ts_grades):
    for ts_grade in ts_grades:
        rating = Rating()
        rating.user1 = user_id
        rating.user2 = ts_grade[0].user_id
        rating.grade = bool(int(ts_grade[2]))
        rating.trainset = True
        rating.save()

"""
    When user wants to regrade the (new) trainset, we delete all of his previous grades;
    also those, that were inserted by praedicto.
    @param user_id: Facebook ID of user that wants to retrain
"""
def delete_grades(user_id):
    Rating.objects.filter(user1=user_id).delete()
