from django.urls import path

from .views import home, get_product, get_all_products, create_product, display_user_product, delete_product, ProductUpdateView


urlpatterns = [
    path('', home, name='home'),
    path('product/<slug>/', get_product, name='get_product'),
    path('allproducts/', get_all_products, name='all_category'),
    path('products/create/', create_product, name='create_product'),
    path('myproducts/', display_user_product, name='my_product'),
    path('delete_product/<uid>/', delete_product, name='delete_product'),
    path('edit_product/<slug:slug>/', ProductUpdateView.as_view(), name='edit_product'),
]
