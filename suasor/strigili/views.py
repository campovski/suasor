# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import threading

from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import LoginForm
from .auxilium import StrigiliThread


def index(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)

		if form.is_valid():
			username = form.cleaned_data['user']
			password = form.cleaned_data['password']
			depth = form.cleaned_data['depth']
			roots = form.cleaned_data['roots']
			rescrap = form.cleaned_data['rescrap']

			thread = StrigiliThread(request, username, password, depth, roots, rescrap)
			thread.start()

			return HttpResponse("""<b>Please do not close this tab or your browser.</b>\n
				Your request is being processed...\nYou will be redirected when process finishes.""")

	else:
		form = LoginForm()

	return render(request, 'strigili/index.html', { 'form': form })
