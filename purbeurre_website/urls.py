from django.urls import path
from . import views

app_name= 'purbeurre_website'
urlpatterns = [
    # post views
    path('', views.index, name='index'),
]