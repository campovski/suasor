import random

from suasor.models import UserData, Rating


TRAIN_SET_SIZE = 100

"""
    Get the train set.
    @param user_id: Facebook ID of user that requested the search
    @return trainset
"""
def get_train_set(user_id):
    users = list(UserData.objects.all())
    n_max = len(users)
    train = []

    # While we don't have desired number of people, generate new ones.
    while len(train) < TRAIN_SET_SIZE:
        user = users[random.randint(1, n_max)]

        # If user found is not the user that requested the search, we can add
        # him/her to trainset.
        if user.user_id != user_id and user not in train:
            train.append(user)

    # Save to database which users were selected for grading. This
    # simplifies the process of grading, because now that we will sort them,
    # there will exist a bijection between binary-valued string of length TRAIN_SET_SIZE
    # and people that user has graded.
    # Do not save rating.grade, so that we know whether the user has really graded
    # them or stopped in the middle of the process.
    train.sort(key=lambda x: x.user_id)
    for user in train:
        rating = Rating()
        rating.user1 = user_id
        rating.user2 = user.user_id
        rating.trainset = True
        rating.save()

    return train

"""
    Saves grades of people in trainset to database.
    @param user_id: Facebook ID of user that graded the trainset
    @param ts_grades: list of grades
"""
def save_train_grades(user_id, ts_grades):
    # Get people that user_id has graded.
    ratings = Rating.objects.filter(user1=user_id).order_by('user_id')
    assert len(ratings) == len(ts_grades), "Number of ratings does not match the number \
        in database."

    # Fill grade column.
    for i in range(len(ratings)):
        ratings[i].grade = bool(int(ts_grade[i]))
        ratings[i].save()

"""
    When user wants to regrade the (new) trainset, we delete all of his previous grades;
    also those, that were inserted by praedicto.
    @param user_id: Facebook ID of user that wants to retrain
"""
def delete_grades(user_id):
    Rating.objects.filter(user1=user_id).delete()
