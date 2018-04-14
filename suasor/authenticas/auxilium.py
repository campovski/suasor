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
