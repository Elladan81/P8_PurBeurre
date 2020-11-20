from django.contrib import admin

# Register your models here.
from substitute_food.models import Product, Category, FavoriteProduct, Stores

admin.site.register(FavoriteProduct)

@admin.register(Stores)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('store_name',)
    list_filter = ('store_name',)
    search_fields = ('store_name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)
    list_filter = ('category_name',)
    search_fields = ('category_name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'brands', 'nutriscore')
    list_filter = ('brands', 'nutriscore')
    search_fields = ('product_name', 'brands', 'nutriscore')
