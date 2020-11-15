from django.contrib import admin

# Register your models here.
from substitute_food.models import Product, Category, FavoriteProduct

admin.site.register(Category)
admin.site.register(FavoriteProduct)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'shops', 'brands', 'nutriscore')
    list_filter = ('product_name', 'shops', 'brands', 'nutriscore')
    search_fields = ('product_name', 'shops', 'brands', 'nutriscore')
