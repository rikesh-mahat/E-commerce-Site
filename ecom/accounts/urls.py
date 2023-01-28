from django.urls import path
from .views import login_user, register_user, activate_user, add_to_cart, cart, remove_cart, checkout_cart, logout_user, customer_profile


urlpatterns = [
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', register_user, name='register'),
    path('activate/<email_token>/', activate_user, name='activate' ),
    path('cart/', cart, name='cart'),
    path('add-to-cart/<uid>/', add_to_cart, name='add_to_cart'),
    path('remove-cart/<cart_item_uid>/', remove_cart, name='remove_cart'),
    path('checkout-cart/', checkout_cart, name='checkout-cart'),
    path('profile/', customer_profile, name='customer_profile')
]
