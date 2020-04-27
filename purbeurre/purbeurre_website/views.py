from django.shortcuts import render


def index(request):
    """the home page for purbeurre"""
    return render(request, 'purbeurre_website/index.html')
