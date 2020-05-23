import profile
from random import randint

import requests
from django.contrib import messages
from django.contrib.admin.utils import unquote
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .database_fill import fill, delete_db
from .models import Product, FavoriteProduct


# Create your views here.

def list_product_by_category(products, categories, exclude_product):
    """Function used to list products by categories and for remove duplicates

    Arguments:
        products {list of Product} -- The list of products you want to order
        categories {list of Category} -- The list of categories of your product
        exclude_product {Product} -- The original product to exclude

    Returns:
        products_by_category {dict} -- The products ordered by categories and
        nutriscores
    """
    product_already_listed = []
    products_by_category = {}
    for category in categories:
        products = (products | category.products.exclude(
            productName=exclude_product))
        for product in product_already_listed:
            products = products.exclude(productName=product)
        for product in products:
            product_already_listed.append(product.productName)
        products_by_category[category.categoryName] = products.exclude(
            id=exclude_product.id).order_by('nutriscore').distinct()[:9]
    return products_by_category


def search(request):
    """Display the page for product search
    Models:
        Product, Category
    Returns:
        template : "site/search.html"
    """
    query = request.POST.get('product_name', '')
    if query != "":
        try:
            products = Product.objects.annotate(search=SearchVector('productName', 'brands')).filter(
                search=query).order_by('-nutriscore')[:18]
            print(products)
            return render(request, 'substitute_food/search.html', locals())
        except Product.DoesNotExist:
            return render(request, 'substitute_food/search.html', locals())
    else:
        messages.error(request, "Pour faire une recherche, merci d'entrer un aliment.")
        return render(request, 'purbeurre_website/index.html', locals())


def find_substitute(request, query, product_id):
    """Display the page of a product

        Arguments:
            query {string} -- Original query for product
            product_id {string} -- Product to substitute

        Returns:
            template : "site/substitute.html"
        """
    product = Product.objects.get(id=product_id)
    product_name = product.productName
    url = product.productURL
    img = product.imgURL
    substitutes = Product.objects.filter(productName__search=query).order_by('nutriscore').exclude(productName=product)[
                  :30]
    categories = product.category_set.all()
    products_by_category = list_product_by_category(
        substitutes, categories, product)
    return render(request, 'substitute_food/find_substitute.html', locals())


def product_info(request, product_name):
    """Display the page of a product

    Arguments:
        product_name {string} -- The name of the product

    Models:
        Product

    Returns:
        template : "site/product.html"
    """
    product_name = unquote(product_name)
    product = Product.objects.get(productName=product_name)
    url = product.productURL
    code = url.split("/")[4]
    resp = requests.get(
        "https://fr.openfoodfacts.org/api/v0/produit/" + code + ".json")
    data = resp.json()
    nutri_img = data['product']["image_nutrition_url"]
    return render(request, 'substitute_food/product.html', locals())


def product_substitute_info(request, product_name, substitute_name):
    """Display the page of a product from a substitute search

    Arguments:
        product_name {string} -- The name of the product
        substitute_name {string} -- The name of the substitute

    Returns:
        template : "substitute_food//product.html"
    """
    product = Product.objects.get(productName=product_name)
    substitute = Product.objects.get(productName=substitute_name)
    url = substitute.productURL
    code = url.split("/")[4]
    resp = requests.get(
        "https://fr.openfoodfacts.org/api/v0/produit/" + code + ".json")
    data = resp.json()
    nutri_img = data['product']["image_nutrition_url"]
    return render(request, 'substitute_food/product.html', locals())

@login_required
def favorites(request):
    """Display the favorite page of user

    Models:
        Favorite

    Returns:
        template : "site/favoris.html"
    """
    if request.user.is_authenticated:
        user = request.user
        user_favorites = FavoriteProduct.objects.filter(user_rel=user).order_by('-created')
        return render(request, 'substitute_food/favorites.html', locals())
    else:
        pass


@login_required
def register_fav(request, product_name, substitute_name):
    """View used to register a favorite in user profile
    Arguments:
        product_name {string} -- The name of the product
        substitute_name {string} -- The name of the substitute
    Models:
        Product, FavoriteProduct
    Returns:
        template : "substitute_food/favorites.html"
    """
    if request.user.is_authenticated:
        user = request.user
        user_favorites = FavoriteProduct.objects.filter(user_rel=user)
        try:
            product = Product.objects.get(productName=product_name)
        except Product.DoesNotExist:
            messages.error(
                request, "Le produit sélectionné n'as pas été trouvé.")
            return render(request, 'substitute_food/favorites.html', locals())
        try:
            substitute = Product.objects.get(productName=substitute_name)
        except Product.DoesNotExist:
            messages.error(
                request, "Le produit sélectionné n'as pas été trouvé.")
            return render(request, 'substitute_food/favorites.html', locals())

        favorite = FavoriteProduct.objects.filter(product=product, substitute=substitute, user_rel=user)
        try:
            FavoriteProduct.objects.get(product=product, substitute=substitute, user_rel=user)
            messages.error(request, "Favori déja existant")
        except FavoriteProduct.DoesNotExist:
            FavoriteProduct.objects.create(product=product, substitute=substitute, user_rel=user)
            messages.success(request, "Favori bien enregistré")
        return render(request, 'substitute_food/favorites.html', locals())
    else:
        return redirect('login')


@login_required
def remove_fav(request, product_name, substitute_name):
    """View used to remove a favorite in user userfavorites
    Arguments:
        product_name {string} -- The name of the product
        substitute_name {string} -- The name of the substitutes

    Models:
        Product, UserFavoritesProduct

    Returns:
        template : "site/favoris.html"
    """
    if request.user.is_authenticated:
        user = request.user
        product = Product.objects.get(productName=product_name)
        substitute = Product.objects.get(productName=substitute_name)
        try:
            fav_to_delete = FavoriteProduct.objects.get(
                product=product, substitute=substitute, user_rel=user)
            fav_to_delete.delete()
            messages.success(request, "Favori supprimé !")
            return redirect('favorites')
        except FavoriteProduct.DoesNotExist:
            messages.error(
                request, "Ce favori n'existe pas.")
        user_favorite = FavoriteProduct.objects.filter(user_rel=user)
        return render(request, 'substitute_food/favorites.html', locals())
    else:
        return redirect('connexion')


def fill_view(request):
    """View used to show the progress of database filling

    It can be accessed in template with that view
    But it will only be used on admin templates
    """
    return render(request, 'admin/fill.html', locals())


def fill_data(request):
    """View used with AJAX to keep progress of database fill

    It can be accessed in template with that view
    But it will only be used on admin templates

    Returns:
        template : "admin/base_site.html"
    """
    page = request.GET.get('page', None)
    fill_thread = fill(page)
    fill_thread.start()
    fill_thread.join()
    data = {
        'is_taken': True
    }
    return JsonResponse(data)


def fill_success(request):
    """View used to return the success of database fill
    """
    messages.success(request, "Base de donnée remplie avec succès !")
    return render(request, 'admin/fill.html')


def del_data(request):
    """View used to launch the database delete function

    It can be accessed in template with that view
    But it will only be used on admin templates

    Returns:
        template : "admin/base_site.html"
    """
    delete_db()
    return redirect('/admin/')
