from django.urls import path
from .views import *

urlpatterns = [
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', register_user, name='register'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/', reset_password, name='reset_password'),
    path('activate/<email_token>/', activate_user, name='activate' ),
    
    path('checkout-cart/<uid>/', checkout_cart, name='checkout_cart'),
    path('display_order/<uid>/', display_order, name = 'order'),
    path('profile/', customer_profile, name='customer_profile'),
    path('search/', search_items, name = "search"),
    path('verify-payment/', verify_payment, name='verify_payment'),
    path('cancel-order/<uid>/', cancel_order, name='cancel_order'),
    path('wishlist/', wishlist, name='wishlist'),
    path('add_wishlist/<uid>/', add_to_wishlist, name='add_wishlist'),
    path('remove_wishlist/<int:id>/', remove_wishlist_item, name='remove_wishlist'),
    path('clear_wishlist/', delete_all_wishlist_items, name='clear_wishlist'),
    path('change-password/', change_password, name='change_password')
    # path('buy_product/<uid>/', buy_item, name="buy"),
    #path('cart/', cart, name='cart'),
     # path('add-to-cart/<uid>/', add_to_cart, name='add_to_cart'),
     # path('remove-cart/<cart_item_uid>/', remove_cart, name='remove_cart'),
     
    # path('users/', display_users, name='display_users'),
    # path('disable/<uid>/', disable_user, name='disable_user'),
    # path('accounts/admin-dashboard/allorders/', all_orders, name='all_orders')
    # path('admin-login/', admin_login, name = "admin_login"),
    # path('admin-dashboard/', admin_dashboard, name = "admin_dashboard"),
    # path('admin-order/<uid>/', order_details, name="order_details"),
    # path('edit-admin-order/<uid>/', edit_order_details, name="edit_order_details"),
    # path('view-order/<uid>/', view_order, name="view_order"),
]
