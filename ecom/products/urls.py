from django.urls import path

from .views import home, get_product, get_all_products, create_product, display_user_product, delete_product, update_product, delete_comment


urlpatterns = [
    path('', home, name='home'),
    path('product/<slug>/', get_product, name='get_product'),
    path('allproducts/', get_all_products, name='all_category'),
    path('products/create/', create_product, name='create_product'),
    path('myproducts/', display_user_product, name='my_product'),
    path('create-product/', create_product, name='create-product'),
    path('delete_product/<uid>/', delete_product, name='delete_product'),
    path('edit_product/<slug:slug>/', update_product, name='edit_product'),
    path('delete_comment/<uid>/', delete_comment, name='delete_comment')
]
