from random import choice
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
def search(request):
    """Display the page for product search
    """
    query = request.GET.get('product_name')
    if query != "":
        try:
            products = Product.objects.annotate(search=SearchVector('product_name', 'brands')).filter(
                search=query).order_by('-nutriscore')[:21]
            if products:
                random_img = Product.objects.get(id=choice([p.id for p in products])).img_url
                return render(request, 'substitute_food/search.html', {"query": query,
                                                                       "products": products,
                                                                       "random_img": random_img})
        except Product.DoesNotExist:
            return render(request, 'substitute_food/search.html', locals())
    else:
        messages.warning(request, "Pour faire une recherche, merci d'entrer un produit dans la barre de recherche...")
        return redirect('purbeurre_website:index')


def find_substitute(request, query, product_id):
    """Display the page of a product
        """
    product = Product.objects.get(id=product_id)
    product_by_category = {}
    categories = product.category_set.all()[:6]
    product_in_dict = []
    for cat in categories:
        substitutes = Product.objects.annotate(search=SearchVector('product_name', 'brands')).filter(
            search=query).filter(category=cat).order_by('nutriscore').exclude(product_name=product)[:9]
        if substitutes.count() < 3:
            substitutes = Product.objects.filter(category=cat).order_by('nutriscore').exclude(product_name=product)[:9]
        filtered_substitutes = [sub for sub in substitutes if sub.id not in product_in_dict]
        if len(filtered_substitutes) > 0:
            product_by_category[cat.category_name] = filtered_substitutes
            for f in filtered_substitutes:
                product_in_dict.append(f.id)
    return render(request, 'substitute_food/find_substitute.html', {"product": product,
                                                                    "categories": categories,
                                                                    "product_by_category": product_by_category})


def product_info(request, product_id):
    """Display the page of a product
    """
    product = Product.objects.get(id=product_id)
    resp = requests.get("https://fr.openfoodfacts.org/api/v0/produit/" + product.product_url.split("/")[4] + ".json")
    data = resp.json()
    nutri_img = data['product']["image_nutrition_url"]
    return render(request, 'substitute_food/product.html', locals())


def product_substitute_info(request, product_id, substitute_id):
    """Display the page of a product from a substitute search
    """
    product = Product.objects.get(id=product_id)
    substitute = Product.objects.get(id=substitute_id)
    data = requests.get("https://fr.openfoodfacts.org/api/v0/produit/"+ substitute.product_url.split("/")[4] + ".json").json()
    nutri_img = data['product']["image_nutrition_url"]
    return render(request, 'substitute_food/product.html', locals())


@login_required
def favorites(request):
    """Display user's favorites
    """
    user = request.user
    user_favorites = FavoriteProduct.objects.filter(user_rel=user).order_by('-created')
    if user_favorites:
        random_image = Product.objects.get(id=choice([p.product.id for p in user_favorites])).img_url
    return render(request, 'substitute_food/favorites.html', locals())


@login_required
def register_fav(request, product_id, substitute_id):
    """View used to register a favorite in user profile
    """
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
    """View used to remove a favorite in user_favorites
    """
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


def fill_view(request):
    """View used to show the progress of database filling
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
