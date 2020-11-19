from random import choice
import requests
from django.contrib import messages
import logging
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .database_fill import fill, delete_db
from .models import Product, FavoriteProduct

logger = logging.getLogger(__name__)

# Create your views here.
def search(request):
    """Display the page for product search"""
    query = str(request.GET.get('product_name'))
    if query != "":
        products = Product.objects.annotate(search=SearchVector('product_name', 'brands')).filter(
            search=query).order_by('-nutriscore')[:21]
        if products:
            random_img = Product.objects.get(id=choice([p.id for p in products])).img_url
        else:
            random_img = None
        logger.info('New Search', exc_info=True, extra={'request': request})
        return render(request, 'substitute_food/search.html', {"query": query,
                                                               "products": products,
                                                               "random_img": random_img})
    else:
        messages.warning(request, "Pour faire une recherche, merci d'entrer un produit dans la barre de recherche...")
        return redirect('purbeurre_website:index')


def find_substitute(request, query, product_id):
    """Display the page of a product"""
    product = Product.objects.get(id=product_id)
    product_by_category = {}
    categories = product.in_cat.all()
    product_in_dict = []
    for cat in categories:
        # query db product : if query in product name, bands,
        # shops in same category, exclude products with nutriscore lower
        substitutes = Product.objects.annotate(search=SearchVector('product_name', 'brands', 'in_store')).filter(
            search=query).filter(in_cat__category_name=cat).order_by('nutriscore').exclude(
            product_name=product).exclude(
            nutriscore__gt=product.nutriscore)[:9]
        # if not enough substitutes with the same query, look for other product in same cat
        if substitutes.count() < 3:
            substitutes = Product.objects.filter(in_cat__category_name=cat).order_by('nutriscore').exclude(
                product_name=product).exclude(
                nutriscore__gt=product.nutriscore)[:9]
        filtered_substitutes = [sub for sub in substitutes if sub.id not in product_in_dict]
        if len(filtered_substitutes) > 0:
            product_by_category[cat.category_name] = filtered_substitutes
            for f in filtered_substitutes:
                product_in_dict.append(f.id)
    return render(request, 'substitute_food/find_substitute.html', {"product": product,
                                                                    "categories": categories,
                                                                    "product_by_category": product_by_category})


def product_info(request, product_id):
    """Display the page of a product"""
    product = Product.objects.get(id=product_id)
    resp = requests.get("https://fr.openfoodfacts.org/api/v0/produit/" + product.product_url.split("/")[4] + ".json")
    data = resp.json()
    product_nutri_img = data['product']["image_nutrition_url"]
    return render(request, 'substitute_food/product.html', {"product": product,
                                                            "resp": resp,
                                                            "data": data,
                                                            "product_nutri_img": product_nutri_img})


def product_substitute_info(request, product_id, substitute_id):
    """Display the page of a product from a substitute search"""
    product = Product.objects.get(id=product_id)
    substitute = Product.objects.get(id=substitute_id)
    data_product = requests.get(
        "https://fr.openfoodfacts.org/api/v0/produit/" + product.product_url.split("/")[4] + ".json").json()
    data_substitute = requests.get(
        "https://fr.openfoodfacts.org/api/v0/produit/" + substitute.product_url.split("/")[4] + ".json").json()
    product_nutri_img = data_product['product']["image_nutrition_url"]
    substitute_nutri_img = data_substitute['product']["image_nutrition_url"]
    return render(request, 'substitute_food/product.html', {"product": product,
                                                            "substitute": substitute,
                                                            "product_nutri_img": product_nutri_img,
                                                            "substitute_nutri_img": substitute_nutri_img
                                                            })


@login_required
def favorites(request):
    """Display user's favorites"""
    user = request.user
    user_favorites = FavoriteProduct.objects.filter(user_rel=user).order_by('-created')
    if user_favorites.count() != 0:
        random_image = Product.objects.get(id=choice([p.product.id for p in user_favorites])).img_url
        return render(request, 'substitute_food/favorites.html',
                      {"user_favorites": user_favorites, "random_image": random_image})
    else:
        messages.warning(request, "Vous n'avez pas encore de produit enregistré dans vos favoris")
    return redirect('purbeurre_website:index')


@login_required
def register_fav(request, product_id, substitute_id):
    """View used to register a favorite in user profile"""
    product = Product.objects.get(id=product_id)
    substitute = Product.objects.get(id=substitute_id)
    fav_reg = FavoriteProduct.objects.get_or_create(product=product, substitute=substitute, user_rel=request.user)
    if fav_reg[1] == True:
        messages.success(request, "Favori bien enregistré !")
    else:
        messages.warning(request, 'Ce favori existe déjà')
    return redirect('favorites')


@login_required
def remove_fav(request, product_id, substitute_id):
    """View used to remove a favorite in user_favorites"""
    product = Product.objects.get(id=product_id)
    substitute = Product.objects.get(id=substitute_id)
    try:
        fav_to_delete = FavoriteProduct.objects.get(product=product, substitute=substitute, user_rel=request.user)
        fav_to_delete.delete()
        messages.success(request, "Favori supprimé !")
        return redirect('favorites')
    except FavoriteProduct.DoesNotExist:
        messages.error(request, "Vous ne pouvez pas supprimer ce produit.")
    return redirect('favorites')


@login_required
def fill_view(request):
    """View used to show the progress of database filling"""
    return render(request, 'admin/fill.html', locals())


@login_required
def fill_data(request):
    """View used with AJAX to keep progress of database fill"""
    page = request.GET.get('page', None)
    fill_thread = fill(page)
    fill_thread.start()
    fill_thread.join()
    data = {
        'is_taken': True
    }
    return JsonResponse(data)


@login_required
def fill_success(request):
    """View used to return the success of database fill"""
    messages.success(request, "Base de donnée remplie avec succès !")
    return render(request, 'admin/fill.html')


@login_required
def del_data(request):
    """View used to launch the database delete function"""
    delete_db()
    return redirect('/admin/')
