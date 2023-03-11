from django.urls import path
from .views import *

urlpatterns = [
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', register_user, name='register'),
    path('activate/<email_token>/', activate_user, name='activate' ),
    path('cart/', cart, name='cart'),
    path('add-to-cart/<uid>/', add_to_cart, name='add_to_cart'),
    path('remove-cart/<cart_item_uid>/', remove_cart, name='remove_cart'),
    path('checkout-cart/', checkout_cart, name='checkout-cart'),
    path('profile/', customer_profile, name='customer_profile'),
    path('admin-login/', admin_login, name = "admin_login"),
    path('admin-dashboard/', admin_dashboard, name = "admin_dashboard"),
    path('admin-order/<uid>/', order_details, name="order_details"),
    path('edit-admin-order/<uid>/', edit_order_details, name="edit_order_details"),
    path('view-order/<uid>/', view_order, name="view_order"),
    path('search/', search_items, name = "search"),
    path('esewa-request/', esewa_request, name = 'esewa'),
    path('esewa-verify/', esewa_verify, name = 'esewa_verify'),
    path('buy_product/<uid>/', buy_item, name="buy"),
    path('users/', display_users, name='display_users'),
    path('disable/<uid>/', disable_user, name='disable_user')
]
