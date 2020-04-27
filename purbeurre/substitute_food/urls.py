from django.urls import path
from . import views

urlpatterns = [
    # post views
    path('search/', views.search, name="search"),
    path('find_substitute/<query>/<product_id>/', views.find_substitute, name="find_substitute"),
    path('favorites/', views.favorites, name='favorites'),
    path('product/<product_name>', views.product_info, name="product"),
    path('product/<product_name>/<substitute_name>/',
         views.product_substitute_info, name="substitute_product"),
    path('favorites/<product_name>/<substitute_name>/',
         views.register_fav, name="favorites_register"),
    path('remove/<product_name>/<substitute_name>/',
         views.remove_fav, name="favorites_remove"),
    path('admin/fill', views.fill_view, name="fill"),
    path('admin/ajax/fill', views.fill_data, name="fill_data"),
    path('admin/fill_success', views.fill_success, name="fill_success"),
    path('favorites/', views.favorites, name="favorites"),
    path('admin/delete', views.del_data, name="deleteDB"),
]