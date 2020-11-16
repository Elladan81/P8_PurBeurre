from django.db import models
from django.contrib.auth.models import User

from django.conf import settings


class Product(models.Model):
    """
    Store a product
    The product is unique

    Fields:
        productName {CharField} -- The name of the product (max_lenght=100)
        shops {TextField} -- The shops of the product (null=False)
        brands {TextField} -- The brands of the product (null=False)
        productURL {URLField} -- The url of the product
        nutriscore {CharField} -- The nutriscore of the product (max_lenght=1)
        imgURL {URLField} -- The url of the product image

    Returns:
        {string} -- The name of the product
    """
    product_name = models.CharField(max_length=100, unique=True)
    brands = models.TextField(null=False)
    product_url = models.URLField(verbose_name="URL du produit", unique=True)
    nutriscore = models.CharField(max_length=1)
    img_url = models.URLField(verbose_name="URL de l'image du produit", null=True)

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name = "Produit"
        ordering = ['product_name']


class Stores(models.Model):
    """ Store stores for product"""
    store_name = models.CharField(max_length=200, unique=True)
    products = models.ManyToManyField('Product', related_name='in_store')

    def __str__(self):
        return self.store_name

    class Meta:
        verbose_name = "Magasin"
        ordering = ['store_name']


class Category(models.Model):
    """Store a category
    """
    category_name = models.CharField(max_length=150, unique=True)
    products = models.ManyToManyField('Product', related_name='in_cat')

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = "Catégorie"
        ordering = ['category_name']


class FavoriteProduct(models.Model):
    """Store a favorite
    The favorite is unique

    Fields:
        substitute {Product} -- The substitute
        product {Product} -- The product

    Returns:
       {string} -- The name of the substitute and the product
    """
    user_rel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite', null=True)
    created = models.DateTimeField(auto_now_add=True)
    substitute = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='%(class)s_substitute')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='%(class)s_product')

    def __str__(self):
        return ("Substitut : " + str(self.substitute)
                + " / Produit : " + str(self.product))

    class Meta:
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        ordering = ['product']
