import random

from suasor.models import UserData, Rating


TRAIN_SET_SIZE = 100

"""
    Checks if user can continue grading or he has completed the grading or has not
    even started it.
    @param user_id: Facebook ID of user that will grade
    @return True if user has incomplete rating session, False if completed, otherwise None
"""
def can_continue_grading(user_id):
    # Get all ratings of user that belong to trainset.
    user_trainset_ratings = Rating.objects.filter(user1=user_id).filter(trainset=True)

    # If there are no such ratings, user has not rated anyone yet.
    if not user_trainset_ratings:
        return None

    # If there are some ratings with grade null, user can continue grading.
    if user_trainset_ratings.filter(grade__isnull=True):
        return True
    return False

"""
    Get the train set.
    @param user_id: Facebook ID of user that requested the search
    @return trainset
"""
def get_train_set(user_id, retrain):
    # If user wants to start training from beginning, delete his grades and get
    # new trainset.
    if retrain:
        delete_grades(user_id)

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

    else:
        # If user will continue training, then get the users he has not rated yet.
        train = Rating.objects.filter(user1=user_id).filter(trainset=True).filter(grade__isnull=True).order_by('user2')

    return train

"""
    Saves grades of people in trainset to database.
    @param user_id: Facebook ID of user that graded the trainset
    @param ts_grades: list of grades
"""
def save_train_grades(user_id, ts_grades):
    # Get people that user_id has not graded yet.
    ratings = Rating.objects.filter(user1=user_id).filter(trainset=True).filter(grade__isnull=True).order_by('user2')

    # Fill grade column. If user has not graded everyone in trainset, some of grades
    # (last ones) will stay null.
    for i in range(len(ts_grades)):
        ratings[i].grade = bool(int(ts_grades[i]))
        ratings[i].save()

"""
    When user wants to regrade the (new) trainset, we delete all of his previous grades;
    also those, that were inserted by praedicto.
    @param user_id: Facebook ID of user that wants to retrain
"""
def delete_grades(user_id):
    Rating.objects.filter(user1=user_id).delete()
