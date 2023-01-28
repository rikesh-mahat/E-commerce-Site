from django.urls import path
from .views import home, get_product, get_all_products


urlpatterns = [
    path('', home, name='home'),
    path('product/<slug>/', get_product, name='get_product'),
    path('allproducts/', get_all_products, name='all_category')
]
