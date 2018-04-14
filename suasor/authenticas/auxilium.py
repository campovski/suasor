from .models import User


"""
    Checks if user exists.
    @param user_id: Facebook ID of user that tries to login.
    @param password: custom password for Suasor (not Facebook one)
    @return True if user exists, else False
"""
def validate_login(user_id, password):
    try:
        user = User.objects.get(user_id=user_id, password=password)
    except User.DoesNotExist:
        user = None
    return True if user else False

"""
    Sign up user by adding him to User table.
    @param user_id: Facebook ID of user that signed up to Suasor
    @param password: desired password
    @return False if user_id already registered, otherwise True
"""
def signup_user(user_id, password):
    try:
        User.objects.get(user_id=user_id)
        return False # user already exists
    except User.DoesNotExist:
        user = User()
        user.user_id = user_id
        user.password = password
        user.save()
        return True
