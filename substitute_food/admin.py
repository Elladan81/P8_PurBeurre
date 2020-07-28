from django.contrib import admin

# Register your models here.
from substitute_food.models import Product, Category, FavoriteProduct

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(FavoriteProduct)