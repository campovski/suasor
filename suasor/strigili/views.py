# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import threading

from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import LoginForm
from .auxilium import strigili


def index(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)

		if form.is_valid():
			username = form.cleaned_data['user']
			password = form.cleaned_data['password']
			depth = form.cleaned_data['depth']
			roots = form.cleaned_data['roots']

			thread = threading.Thread(target=strigili, args=[username, password, depth, roots])
			thread.start()

			return search(request)

		return render(request, 'strigili/index.html', { 'form': form })

	return HttpResponse("Error, bad request!")

def search(request):
	return HttpResponse("Your request is being processed... We will notify you when it's done!")
