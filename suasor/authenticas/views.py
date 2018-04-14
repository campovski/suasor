from django.shortcuts import render
from django.http import HttpResponse

from suasor.settings import BASE_HTTP_ADDRESS
from .forms import SuasorLoginForm, SuasorSignupForm


def index(request):
    try:
        if request.session['user'] is not None:
            return redirect(BASE_HTTP_ADDRESS)
    except KeyError:
        pass # continue with logging in

    if request.method == 'POST':
        form = SuasorLoginForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            password = form.cleaned_data['password']
            if validate_login(user_id, password):
                request.session['user'] = user_id
                return redirect(BASE_HTTP_ADDRESS)
            else:
                return render(request, 'authenticas/index.html', { 'form': form, 'valid': False })
    else:
        form = SuasorLoginForm()
    return render(request, 'authenticas/index.html', { 'form': form, 'valid': True })

def signup(request):
    try:
        if request.session['user'] is not None:
            return redirect(BASE_HTTP_ADDRESS)
    except KeyError:
        pass # continue with signing up

    if request.method == 'POST':
        form = SuasorSignupForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            if password1 == password2:
                signup_successful = signup_user(user_id, password1)
                if not signup_successful:
                    return render(request, 'authenticas/signup.html', { 'form': form, 'valid': None })
                request.session['user'] = user_id
                return redirect(BASE_HTTP_ADDRESS)
            else:
                return render(request, 'authenticas/signup.html', { 'form': form, 'valid': False })
    else:
        form = SuasorSignupForm()
    return render(request, 'authenticas/signup.html', { 'form': form, 'valid': True })
