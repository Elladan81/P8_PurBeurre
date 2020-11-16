"""Module used to fill a database from the OpenFoodFacts API

Django website app is required

Django models used : Product, Category, Favorite
"""

from threading import Thread
import requests

from .models import Product, Category, FavoriteProduct, Stores
from googletrans import Translator



# Initialisation


def json_products_list(page_number):
    """Function used to create a json list of a OpenFoodFacts data page

    Arguments:
        page_number {integer} -- The number of the page that will be loaded

    Returns:
        data {json} -- The json object that contains OpenFoodFacts data
    """

    url_fr = f"https://fr.openfoodfacts.org/country/france/{page_number}.json"
    response = requests.get(url_fr)
    data = response.json()
    return data


def product_correct(product):
    """Function used to verify if the product can be inserted in the database
    It checks that the product has the required tags and is complete

    Arguments:
        product {json} -- The product json object

    Returns:
        {bool} -- If true the product can be added to database
    """

    if product['states_hierarchy'][1] == "en:complete" \
            and product["image_front_url"] is not "" \
            and len(product['nutrition_grades']) < 2:
        return True
    else:
        return False


class fill(Thread):
    """Function used to fill the database

    Django webSite models used : Product, Category
    """

    def __init__(self, page):
        Thread.__init__(self)
        self.page = page

    def run(self):
        try:
            products = json_products_list(self.page)
            for product in products['products']:
                try:
                    if product_correct(product):
                        p_name = product['product_name'].replace('/', '-')
                        try:
                            productobj = Product.objects.get(
                                product_name=p_name)
                            if productobj.product_url is None:
                                productobj.product_url = (
                                    product["image_front_url"])
                        except Product.DoesNotExist:
                            productobj = Product.objects.create(
                                product_name=p_name,
                                brands=str(product['brands']).lower().title().replace(",", ", "),
                                product_url=product['url'],
                                nutriscore=product['nutrition_grades'],
                                img_url=product['image_front_url'])
                            for category in product['categories'].split(','):
                                # SQL request storing Categories
                                translator = Translator()
                                raw_name = translator.translate(str(category), dest='fr')
                                cat_name = str(raw_name.text).lower().title()
                                try:
                                    cat = Category.objects.get(
                                        category_name=cat_name)
                                    cat.products.add(productobj)
                                except Category.DoesNotExist:
                                    cat = Category.objects.create(
                                        category_name=cat_name)
                                    cat.products.add(productobj)
                            for store in product['stores'].split(','):
                                # SQL request storing Stores
                                store_name = str(store).lower().title()
                                try:
                                    cat = Stores.objects.get(
                                        store_name=store_name)
                                    cat.products.add(productobj)
                                except Stores.DoesNotExist:
                                    cat = Stores.objects.create(
                                        store_name=store_name)
                                    cat.products.add(productobj)
                except KeyError:
                    continue
        finally:
            pass


def delete_db():
    """Function used to clear database

    Django webSite models used : Product, Category, Favorite
    """

    Category.objects.all().delete()
    FavoriteProduct.objects.all().delete()
    Product.objects.all().delete()
    Stores.objects.all().delete()


class fill_cron(Thread):
    """Function used to fill the database

    Django webSite models used : Product, Category
    """

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        for i in range(100):
            fill_thread = fill(i)
            fill_thread.start()
