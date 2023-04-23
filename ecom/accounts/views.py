from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Order
import random
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, authenticate, logout
import uuid
from django.db.models import Q
from base.emails import send_account_activation_mail, send_forgotpassword_email
from accounts.models import Profile, Cart, CartItems, Order, ORDER_STATUS, PAYMENT
from django.http import HttpResponseRedirect
from products.models import Product
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import requests as req
from django.conf import settings

# Create your views here.
# assign cart to a user if he/she logins to the system





def login_user(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=email)

        if not user_obj.exists():
            messages.warning(request, "User does not exist please create an account first")
            return HttpResponseRedirect(request.path_info)

        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, "Verify your account first")
            return HttpResponseRedirect(request.path_info)

        if not user_obj[0].profile.status:
            messages.warning(request, "Your account has been disabled")
            return HttpResponseRedirect(request.path_info)

        user = authenticate(username=email, password=password)
        if user:
            print("authentication successful")
            login(request, user)
            if "next" in request.GET:
                print("next is present")
                next_url = request.GET.get("next")
                return redirect(next_url)
            else:
                print("this view working")
                return redirect('home')
        messages.warning(request, "Sorry the password doesn't match")
        
    return render(request, 'accounts/login.html')


def register_user(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        userObj = User.objects.filter(username=email)

        if userObj.exists():
            messages.warning(request, "Sorry the email is already in use")
            return HttpResponseRedirect(request.path_info)

        if pass1 != pass2:
            messages.warning(request, "Password do not match")
            return HttpResponseRedirect(request.path_info)

        registered_user = User.objects.create(first_name=first_name, last_name=last_name, email=email, username=email)
        registered_user.set_password(pass2)
        registered_user.save()

        email_token = str(uuid.uuid4())
        register_customer = Profile.objects.create(user=registered_user, address=address, mobile=mobile, email_token=email_token)
        register_customer.save()
        messages.info('An Email has been sent to you email for activation')
        send_account_activation_mail(email, email_token)

        if "next" in request.GET:
            next_url = request.GET.get("next")
            return redirect(next_url)
        else:
            return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/register.html')

def forgot_password(request):
    if request.method == "POST":
    # first check if user exist or not then only send verification code
        username = request.POST.get("email")
        userObj = User.objects.filter(username = username)
        print(username)
        if not userObj.exists():
            messages.warning(request, "User doesn't exist")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        auth_code = random.randint(100000, 999999)
        send_forgotpassword_email(username, auth_code)
        
        # store it in the session
        request.session['code'] = auth_code
        request.session['username'] = username
        
        messages.info(request, "A code has been sent to your email")
        return redirect('reset_password')
    return render(request, 'accounts/forgotpassword.html')

def reset_password(request):
    username = request.session.get('username')
    code = request.session.get('code')
    
    
    if request.method == "POST":
        user_code = request.POST.get('code')
        if int(code) != int(user_code):
            messages.warning(request, 'Invalid Code')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        
        if pass1 != pass2:
            messages.info(request, "Password do not match")
        
        user = User.objects.get(username = username)
        user.set_password(pass2)
        user.save()
            
        messages.info(request,"Your password has been changed succesfully")
        return redirect('login')
    
    return render(request, 'accounts/resetpassword.html')

def activate_user(request, email_token):
    try:
        user = Profile.objects.get(email_token=email_token)
        user.is_email_verified = True
        user.save()
        return redirect(request, 'login')
    except Exception as e:
        return HttpResponse('Invalid token')


def logout_user(request):
    logout(request)
    return redirect(reverse('home'))


def cart(request):
    assign_cart(request)
    load_cart(request)

    cart_uid = request.session.get('cart.uid', None)

    if cart_uid:
        cartObj = Cart.objects.get(uid=uuid.UUID(cart_uid))

        context = {
            'cart': cartObj,
            'cart_items': cartObj.cart_items.all()
        }
        if not cartObj.cart_items.all().count():
            messages.info(
                request, 'No items in cart. Please continue shopping')
        return render(request, 'accounts/cart.html', context)
    else:
        messages.info(request, 'Add items to your cart')
    return render(request, 'accounts/cart.html')


def add_to_cart(request, uid):
    assign_cart(request)
    load_cart(request)
    productObj = Product.objects.get(uid=uid)
    cart_uid = request.session.get('cart.uid', None)

    if cart_uid:

        cart = Cart.objects.get(uid=uuid.UUID(cart_uid))

    else:
        cart = Cart.objects.create(is_checkedout=False)
        request.session['cart.uid'] = str(cart.uid)

    cart_item_obj = CartItems.objects.filter(cart=cart, product=productObj)
    if cart_item_obj.exists():
        return redirect('cart')
    cart_item = CartItems.objects.create(cart=cart, product=productObj)
    cart_item.save()
    request.session['total_cart_items'] = cart.get_total_cartitems()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def remove_cart(request, cart_item_uid):
    try:
        assign_cart(request)
        load_cart(request)
        cart_item = CartItems.objects.get(uid=cart_item_uid)
        cart_item.delete()
        cartObj = Cart.objects.get(uid=cart_item.cart.uid)
        request.session['total_cart_items'] = cartObj.get_total_cartitems()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def checkout_cart(request):
    assign_cart(request)
    load_cart(request)
    cart_uid = request.session.get('cart.uid')
    cartObj= Cart.objects.get(uid = cart_uid)
    context ={
        'items' : cartObj.cart_items.all(),
        'cart': cartObj,
        'payments' : PAYMENT,
    }

    if request.method == "POST":
        cart = cartObj
        ordered_by = request.POST.get("username")
        email = request.POST.get("email")
        mobile  = request.POST.get("mobile")
        shipping_address = request.POST.get("address")
        total = cartObj.get_cart_total()

        orderObj = Order.objects.create(cart = cart, ordered_by = ordered_by, shipping_address = shipping_address, mobile = mobile, email = email, total = total)
        orderObj.save()
        cart.is_checkedout = True
        cart.save()
        del request.session['cart.uid']
        request.session['total_cart_items'] = 0
        payment = request.POST.get('payment')

        
        return redirect('home')
    return render(request, 'accounts/checkout.html', context)

def khalti_payment(context):
    pass

def customer_profile(request):
    userObj = request.user
    user = User.objects.get(id=userObj.id)

    orders = Order.objects.filter(cart__user=user).order_by('-created_at')
    context = {
        'orders': orders,
    }

    if request.method == "POST":
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.username = email
        user.save()

        profile = Profile.objects.get(user=user)
        profile.address = address
        profile.mobile = mobile
        profile.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'accounts/profile.html', context)


def admin_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=email)

        if not user_obj.exists():
            messages.warning(request, "No such admin account exists")
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username=email, password=password)

        if user_obj:
            login(request, user_obj)
            return redirect('admin_dashboard')

        messages.warning(request, "Sorry the credentials do not match")
        return HttpResponseRedirect(request.path_info)

    return render(request, 'adminpages/admin_login.html')


def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    pending_orders = Order.objects.filter(order_status="Order Received").order_by("-created_at")
    context = {
        'pending_orders': pending_orders
    }
    return render(request, 'adminpages/admin_dashboard.html', context)


def all_orders(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    all_orders = Order.objects.all().order_by("-created_at")
    context = {
        'all_orders': all_orders
    }
    return render(request, 'adminpages/allorders.html', context)

def order_details(request, uid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    orderObj = Order.objects.get(uid=uid)
    orderItems = orderObj.cart.cart_items.all()
    context = {
        'order': orderObj,
        'orderitems': orderItems,
    }
    return render(request, 'adminpages/orderdetail.html', context)


def edit_order_details(request, uid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    orderObj = Order.objects.get(uid=uid)
    allstatus = ORDER_STATUS

    context = {
        'order': orderObj,
        'allstatus': allstatus,
    }

    if request.method == "POST":
        status = request.POST.get('status')
        orderObj.order_status = status
        orderObj.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'adminpages/editorderdetail.html', context)


def view_order(request, uid):
    orderObj = Order.objects.get(uid=uid)
    order_items = CartItems.objects.filter(cart=orderObj.cart)
    context = {
        'items': order_items,
        'order': orderObj,
    }

    return render(request, 'accounts/view_order.html', context)


    
def search_items(request):

    if request.method == "GET":
        keyword = request.GET.get('keyword')
        results = Product.objects.filter(Q(product_name__icontains=keyword))
        context = {
            'keyword': keyword,
            'results': results,
        }
    return render(request, 'products/search.html', context)


@login_required()
def buy_item(request, uid):

    productObj = Product.objects.get(uid=uid)
    user = request.user

    # cart create gardiney ani sidhai checkout ma haldiney tyo cart lai done

    cart = Cart.objects.create(user=user, is_checkedout=True)

    # item in cart
    CartItems.objects.create(cart=cart, product=productObj)

    # context pass gardiney checkout form lai
    context = {
        'items': cart.cart_items.all(),
        'cart': cart,
        'payments': PAYMENT,
    }
    if request.method == "POST":
        cart = cart
        ordered_by = request.POST.get("username")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        shipping_address = request.POST.get("address")
        total = cart.get_cart_total()

        orderObj = Order.objects.create(
            cart=cart, ordered_by=ordered_by, shipping_address=shipping_address, mobile=mobile, email=email, total=total)
        orderObj.save()

        payment = request.POST.get('payment')

        if payment == "Esewa":
            return redirect(reverse('esewa') + '?o_id=' + str(orderObj.uid))

    return render(request, 'accounts/checkout.html', context)


def display_users(request):
    profile_list = Profile.objects.all()
    paginator = Paginator(profile_list, 1)  # Show 10 profiles per page
    page_number = request.GET.get('page')
    try:
        profiles = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer, use the first page
        profiles = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range (e.g. 9999), use the last page
        profiles = paginator.page(paginator.num_pages)
    return render(request, 'adminpages/users.html', {'profiles': profiles})


def disable_user(request, uid):
    user = Profile.objects.get(uid=uid)
    if user.status:
        user.status = False
    else:
        user.status = True
    user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
