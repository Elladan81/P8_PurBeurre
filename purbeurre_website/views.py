from django.shortcuts import render
from substitute_food.models import Product


def index(request):
    """the home page for purbeurre"""
    total_product = Product.objects.all().count()
    return render(request, 'purbeurre_website/index.html', {"total_product": total_product})


def legal_mentions(request):
    return render(request, 'purbeurre_website/legal.html')