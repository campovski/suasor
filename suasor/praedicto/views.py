from django.shortcuts import render, redirect
from django.http import HttpResponse

from .auxilium import get_train_set, save_train_grades, can_continue_grading


def index(request):
    # Require user to be logged in.
    try:
        user_id = request.session['user']
    except KeyError:
        return redirect('authenticas:index')

    # Check if user can continue grading.
    can_continue = can_continue_grading(user_id)
    content = {
        'can_continue_grading': can_continue,
        'user_id': user_id
    }
    return render(request, 'praedicto/index.html', content)

def train(request, user_id_rated=None, grades=None, retrain=False):
    if user_id_rated is None:
        # Require user to be logged in.
        try:
            user_id = request.session['user']
        except KeyError:
            return redirect('authenticas:index')

        trainset = get_train_set(user_id, retrain)
        content = {
            'trainset': trainset,
            'trainset_size': len(trainset),
            'user_id': user_id
        }
        return render(request, 'praedicto/train.html', content)
    else:
        save_train_grades(user_id_rated, grades)
        return HttpResponse("Grading completed and saved to database!")
