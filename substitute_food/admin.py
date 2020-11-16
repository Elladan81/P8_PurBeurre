from django.contrib import admin

# Register your models here.
from substitute_food.models import Product, Category, FavoriteProduct, Stores

admin.site.register(Category)
admin.site.register(FavoriteProduct)
admin.site.register(Stores)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'brands', 'nutriscore')
    list_filter = ( 'brands', 'nutriscore')
    search_fields = ('product_name', 'brands', 'nutriscore')
