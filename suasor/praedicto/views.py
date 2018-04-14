from django.shortcuts import render, redirect
from django.http import HttpResponse

from .auxilium import get_train_set, save_train_grades


def index(request):
    return HttpResponse("Praedicto OK")

def train(request, user_id=None, grades=None):
    if user_id is None:
        # Require user to be logged in.
        try:
            user_id = request.session['user']
        except KeyError:
            return redirect('authenticas:index')

        trainset = get_train_set(user_id)
        content = {
            'trainset': trainset,
            'trainset_size': len(trainset),
            'user_id': user_id
        }
        return render(request, 'praedicto/train.html', content)
    else:
        save_train_grades(user_id, grades)
        return HttpResponse("Grading completed and save to database!")
