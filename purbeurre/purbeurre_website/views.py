from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404


def index(request):
    """the home page for learning log"""
    return render(request, 'purbeurre_website/index.html')
