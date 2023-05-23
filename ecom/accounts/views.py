from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests
from .models import *
import random
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate, logout
import uuid
from django.db.models import Q
from base.emails import *
from accounts.models import Profile, Cart, CartItems, Order, ORDER_STATUS, PAYMENT
from django.http import HttpResponseRedirect
from products.models import Product
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import re


# code for password checking
def check_password(pass1, pass2):
    
    # message  returned at last
    msg = "valid" 
    
    if len(pass1) < 8:    # if password length is less than 8 characters
        msg = "Password should minimum 8 characters long"
        return msg
    pattern = r'[a-zA-Z]'
    
    if not re.search(pattern, pass1):  # if password only contains only numbers
        msg = "All numeric password not allowed, please use some characters and alphabets"
        return msg
    
    if not re.search(r'\d', pass1):  # if password only contains alphabes and no numbers
        msg = "Please use some numbers along with alphabets"
        return msg
     
    if pass1 != pass2:  # if password do not match
        msg = "Password do not match"
        return msg
    
    return msg  # return the msg 



# mobile number validation
def validate_mobile_number(mobile):
    #  provide the regex pattern (should be 10 digit number)
    pattern = re.compile(r'^\d{10}$')
    return bool(pattern.match(mobile))   # return true if number is 10 digit else return false
    

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

        # validate user mobile
        mobile_validation = validate_mobile_number(mobile)  # validate_mobile_number function
        
        # if mobile number not valid notify the user
        if not mobile_validation:
            messages.warning(request, "Please enter a valid mobile number")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        
         # check for the user password 
        msg = check_password(pass1, pass2)  # check_password function
        
        # if function return other msg instead of valid notify user what is wrong
        if msg.lower() != "valid":
                messages.warning(request, msg)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        registered_user = User.objects.create(first_name=first_name, last_name=last_name, email=email, username=email)
        registered_user.set_password(pass2)
        registered_user.save()

        email_token = str(uuid.uuid4())
        register_customer = Profile.objects.create(user=registered_user, address=address, mobile=mobile, email_token=email_token)
        register_customer.save()
        messages.info(request, 'An Email has been sent to you email for activation')
        
        username = registered_user.first_name + registered_user.last_name
        send_account_activation_mail(username, email, email_token)
        
        if "next" in request.GET:
            next_url = request.GET.get("next")
            return redirect(next_url)
        else:
            return redirect('login')
        
        
    return render(request, 'accounts/register.html')

def forgot_password(request):
    if request.method == "POST":
        

    # first check if user exist or not then only send verification code
        username = request.POST.get("email")
        userObj = User.objects.filter(email = username)
        if not userObj.exists():
            messages.warning(request, "User doesn't exist")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        auth_code = random.randint(100000, 999999)
        profile = Profile.objects.get(user  = userObj[0])
        profile.email_code = auth_code
        profile.save()
        
        
        user = User.objects.get(username = username)
        fullname = user.first_name + user.last_name
        send_verification_code(fullname, auth_code, username)
        
        # store it in the session
        request.session['username'] = username
        
        messages.info(request, "A code has been sent to your email")
        return redirect('reset_password')
    return render(request, 'accounts/forgotpassword.html')

def reset_password(request):
    username = request.session.get('username')
    user = User.objects.get(email = username)
    code = user.profile.email_code
    
   
    if request.method == "POST":
        
        user_code = request.POST.get('code')
        print(code, user_code)
        if int(code) != int(user_code):
            messages.warning(request, 'Invalid Code')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        
      
        msg = check_password(pass1, pass2)  
        
        if msg.lower() != "valid":
                messages.warning(request, msg)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        user = User.objects.get(username = username)
        user.set_password(pass2)
        user.save()
            
        messages.info(request,"Your password has been changed succesfully")
        return redirect('login')
    
    return render(request, 'accounts/resetpassword.html')

def activate_user(request, email_token):
 
    user = Profile.objects.get(email_token=email_token)
    user.is_email_verified = True
    user.save()
    return redirect(request, 'login')
   


def logout_user(request):
    logout(request)
    return redirect(reverse('home'))



def get_or_create_cart(request):
    cartid = request.session.get('cart.uid')

    if request.user.is_authenticated:
        if cartid:
            cart = Cart.objects.get(id=cartid)
            if cart.user is None:
                cart.user = request.user
                cart.save()
        else:
            check_cart = Cart.objects.filter(user=request.user).last()
            if check_cart is not None and not check_cart.is_checkedout:
                cart = check_cart
            else:
                cart = Cart.objects.create(user=request.user)
            request.session['cartid'] = str(cart.uid)
    else:
        if cartid:
            cart = Cart.objects.get(id=cartid)
        else:
            cart = Cart.objects.create()
            request.session['cart.uid'] = cart.uid

    return cart

# def cart(request):
#     cart = get_or_create_cart(request)

#     if cart.uid:
        
#         context = {
#             'cart': cart,
#             'cart_items': cart.cart_items.all()
#         }
#         if not cart.cart_items.all().count():
#             messages.info(
#                 request, 'No items in cart. Please continue shopping')
#         return render(request, 'accounts/cart.html', context)
#     else:
#         messages.info(request, 'Add items to your cart')
#     return render(request, 'accounts/cart.html')


# def add_to_cart(request, uid):
#     cart = get_or_create_cart(request)
#     productObj = Product.objects.get(uid=uid)
#     cart_uid = request.session.get('cart.uid', None)

#     if cart_uid:

#         cart = Cart.objects.get(uid=uuid.UUID(cart_uid))

#     else:
#         cart = Cart.objects.create(is_checkedout=False)
#         request.session['cart.uid'] = str(cart.uid)

#     cart_item_obj = CartItems.objects.filter(cart=cart, product=productObj)
#     if cart_item_obj.exists():
#         return redirect('cart')
#     cart_item = CartItems.objects.create(cart=cart, product=productObj)
#     cart_item.save()
#     request.session['total_cart_items'] = cart.get_total_cartitems()

#     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# def remove_cart(request, cart_item_uid):
#     try:
#         cart = get_or_create_cart(request)
#         cart_item = CartItems.objects.get(uid=cart_item_uid)
#         cart_item.delete()
#         cartObj = Cart.objects.get(uid=cart_item.cart.uid)
#         request.session['total_cart_items'] = cartObj.get_total_cartitems()
#     except Exception as e:
#         print(e)
#     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def checkout_cart(request, uid):
    user  = request.user
    product = Product.objects.get(uid = uid)
    
    if product.owner == user:
        messages.warning(request, "Cannot buy your own product")
        return redirect('my_product')
    if user.is_authenticated:
        profile = user.profile
        
        cart = get_or_create_cart(request)
        if cart.get_total_cartitems() > 0:
           item = cart.cart_items.all()[0]
           item.delete()
        item = CartItems.objects.create(cart = cart, product = product)
                
        
        if request.method == "POST":
            orderer = request.POST.get('firstname') + " " + request.POST.get('lastname')
            shipping_address = request.POST.get('address')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            payment = request.POST.get('payment')
            
           
            order = Order.objects.create(ordered_by = orderer, cart = cart, shipping_address = shipping_address, email = email, mobile = mobile, total =  product.price)
            if payment == 'Cashondelivery':
                order.payment = PAYMENT[0][0]
                order.save()
                
                cart.is_checkedout = True
                cart.save()
                
                product.is_sold = True
                product.save()
                
                cartid = request.session.get('cart.uid')
                if cartid:
                   del request.session['cart.uid']
                
                username = user.first_name + " " + user.last_name 
                send_invoice_email(username, order, email)
                
                owner = product.owner.first_name + " " + product.owner.last_name
                send_congratulation_email(owner, order, product.owner.username)
                return redirect('home')
            elif payment == 'Khalti':
                order.payment = PAYMENT[1][1]
                order.save()
                
                return redirect(reverse('order', kwargs={'uid': order.uid}))
                
    return render(request, 'accounts/checkout.html', {'item':product, 'profile' : profile})

@login_required()
def display_order(request, uid):
    order = Order.objects.get(uid = uid)
    print(order)
    cart =  order.cart
    print(cart)
    cart_items = cart.cart_items.all()
    print(cart_items)
    context = {
        'items' : cart_items,
        'cart' : cart,
        'order' : order
    }
    return render(request, 'accounts/khalti.html', context)

def verify_payment(request):
    user = request.user
    
    if request.method == "GET":
        token = request.GET.get("token")
        amount = request.GET.get("amount")
        order_id = request.GET.get("order_id")
        print("\n\n\n", order_id)
        data = {"success" : "True"}
        
        
        url = "https://khalti.com/api/v2/payment/verify/"
        
        payload = {
                    'token': token,
                    'amount': amount
                }
        headers = {
            'Authorization': 'Key test_secret_key_b799d0896a034ec8beb7d4fc9f5e2e75'
        }
        
        response = requests.post(url, payload, headers=headers)
        resp_dict = response.json()
        if resp_dict.get("idx"):
            # returning the payment status
            success = True
            # tracing the order id and editing
            order = Order.objects.get(uid = order_id)
            order.payment_completed = True
            order.save()
            
            cart = order.cart
            cart.is_checkedout = True
            cart.save()
            
            product = cart.cart_items.all()[0]
            item = product.product
            item.is_sold = True
            item.save()
            
            cartid = request.session.get('cart.uid')
            if cartid:
                del request.session['cart.uid']
            
            
        else:
            success = False
        
        data = {
            'success' : success
        }
        
    return JsonResponse(data)


@login_required()
def customer_profile(request):
    delete_orders(request)
    userObj = request.user
    user = User.objects.get(id=userObj.id)
    profile = user.profile
    carts = Cart.objects.filter(user = userObj).order_by('-created_at')
    
    
    orders = []
    for cart in carts:
        if cart.is_checkedout:
            order = Order.objects.filter(cart = cart)
            if order.exists():
                orders.append(order[0])
            
    count = len(orders)
    
    for order in orders:
        print(order.uid)
   
    context = {
        'orders' : orders,
        'profile' : profile,
        'count' : count
    }

    if request.method == "POST":
        files = request.FILES.get('profile')
        
        
        if files:
            profile.profile_image = files
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        profile.email = email
        profile.mobile = mobile
        profile.address = address
        profile.save()
        
        userObj.first_name = fname
        userObj.last_name = lname
        userObj.save()
        
        
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'accounts/myprofile.html', context)


# def admin_login(request):
#     if request.method == "POST":
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         user_obj = User.objects.filter(username=email)

#         if not user_obj.exists():
#             messages.warning(request, "No such admin account exists")
#             return HttpResponseRedirect(request.path_info)

#         user_obj = authenticate(username=email, password=password)

#         if user_obj:
#             login(request, user_obj)
#             return redirect('admin_dashboard')

#         messages.warning(request, "Sorry the credentials do not match")
#         return HttpResponseRedirect(request.path_info)

#     return render(request, 'adminpages/admin_login.html')


# def admin_dashboard(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#     pending_orders = Order.objects.filter(order_status="Order Received").order_by("-created_at")
#     context = {
#         'pending_orders': pending_orders
#     }
#     return render(request, 'adminpages/admin_dashboard.html', context)


# def all_orders(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#     all_orders = Order.objects.all().order_by("-created_at")
#     context = {
#         'all_orders': all_orders
#     }
#     return render(request, 'adminpages/allorders.html', context)

# def order_details(request, uid):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#     orderObj = Order.objects.get(uid=uid)
#     orderItems = orderObj.cart.cart_items.all()
#     context = {
#         'order': orderObj,
#         'orderitems': orderItems,
#     }
#     return render(request, 'adminpages/orderdetail.html', context)


# def edit_order_details(request, uid):
#     if not request.user.is_authenticated:
#         return redirect('admin_login')
#     orderObj = Order.objects.get(uid=uid)
#     allstatus = ORDER_STATUS

#     context = {
#         'order': orderObj,
#         'allstatus': allstatus,
#     }

#     if request.method == "POST":
#         status = request.POST.get('status')
#         orderObj.order_status = status
#         orderObj.save()
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#     return render(request, 'adminpages/editorderdetail.html', context)


# def view_order(request, uid):
#     orderObj = Order.objects.get(uid=uid)
#     order_items = CartItems.objects.filter(cart=orderObj.cart)
#     context = {
#         'items': order_items,
#         'order': orderObj,
#     }

#     return render(request, 'accounts/view_order.html', context)


    
def search_items(request):

    if request.method == "GET":
        keyword = request.GET.get('keyword')
        results = Product.objects.filter(Q(product_name__icontains=keyword))
        
        paginator = Paginator(results, 4)
        page_number = request.GET.get('page', 1)
        productsData = paginator.get_page(page_number)
        context = {
            'keyword': keyword,
            'results': productsData,
        }
        
        
    return render(request, 'products/search.html', context)


# @login_required()
# def buy_item(request, uid):

#     productObj = Product.objects.get(uid=uid)
#     user = request.user

#     # cart create gardiney ani sidhai checkout ma haldiney tyo cart lai done

#     cart = Cart.objects.create(user=user, is_checkedout=True)

#     # item in cart
#     CartItems.objects.create(cart=cart, product=productObj)

#     # context pass gardiney checkout form lai
#     context = {
#         'items': cart.cart_items.all(),
#         'cart': cart,
#         'payments': PAYMENT,
#     }
#     if request.method == "POST":
#         cart = cart
#         ordered_by = request.POST.get("username")
#         email = request.POST.get("email")
#         mobile = request.POST.get("mobile")
#         shipping_address = request.POST.get("address")
#         total = cart.get_cart_total()

#         orderObj = Order.objects.create(
#             cart=cart, ordered_by=ordered_by, shipping_address=shipping_address, mobile=mobile, email=email, total=total)
#         orderObj.save()

#         payment = request.POST.get('payment')

        

#     return render(request, 'accounts/checkout.html', context)


# def display_users(request):
#     profile_list = Profile.objects.all()
#     paginator = Paginator(profile_list, 1)  # Show 10 profiles per page
#     page_number = request.GET.get('page')
#     try:
#         profiles = paginator.page(page_number)
#     except PageNotAnInteger:
#         # If page_number is not an integer, use the first page
#         profiles = paginator.page(1)
#     except EmptyPage:
#         # If page_number is out of range (e.g. 9999), use the last page
#         profiles = paginator.page(paginator.num_pages)
#     return render(request, 'adminpages/users.html', {'profiles': profiles})


# def disable_user(request, uid):
#     user = Profile.objects.get(uid=uid)
#     if user.status:
#         user.status = False
#     else:
#         user.status = True
#     user.save()
#     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def cancel_order(request, uid):
    order = Order.objects.get(uid = uid)
    cart = order.cart
    print("\n\n\n\n")
    print(cart)
    print("\n\n\n\n")
    if cart.uid:
        product  = cart.cart_items.first()
        product.product.is_sold = False
        product.product.save()
    order.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def check_wishlist(request):
    
    # check if user is authenticated
     if request.user.is_authenticated:
        
        # get the user
        user = request.user
        
        # filter for the wishlist of user
        wishlist = Wishlist.objects.filter(user = user)
        
        # check if there is any wishlist and if yes return the wishlist
        if wishlist.exists():
            return wishlist[0]

        # if there is not wishlist then create a new wishlist for that user
        wishlist = Wishlist.objects.create(user = user)

        # return the wishlist
        return wishlist
    
    
    
### wishlist VIEW
@login_required
def wishlist(request):
    
    # get the wishlist of user from check wishlist function
    wishlist = check_wishlist(request)
    
    # getting all the items present in the wishlist
    wishlist_items = wishlist.wishlist_items.all()
    
    # message
    message = ""
    
    # if there are not items in wishlist notify the user about no items in wishlist
    if len(wishlist_items) == 0:
        message = "You do not have any item in wishlist"
        
    # pass wishlist, wishlist_items and message to wishlist page
    context = {
        'wishlist' : wishlist,
        'cart_items' : wishlist_items,
        'message' : message
    }
    return render(request, 'accounts/wishlist.html', context)



# add to wishlist VIEW
@login_required
def add_to_wishlist(request, uid):
    
    # get the item form database using id
    item = Product.objects.get(uid = uid)
    
    # get the wishlist for check_wishlist function
    wishlist = check_wishlist(request)
    
    # get the user
    user  = request.user
    
    # if the item is not in wishlist then only create a new wishlist item (adding item to wishlist)
    if not wishlist.wishlist_items.filter(item = item).exists():
        wishlist_item = WishlistItems.objects.create(wishlist = wishlist, item = item)
    
    # redirect the user to wishlist page after adding the product
    return redirect('wishlist')



# removing the item from wishlist VIEW
@login_required
def remove_wishlist_item(request, id):
    # get the wishlist item using its id
    item = WishlistItems.objects.get(id = id)
    
    # delete the item
    item.delete()
    
    # return to the same page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# clear the wishlist VIEW
@login_required
def delete_all_wishlist_items(request):
    
    # getting the user 
    user = request.user
    
    # gettin the wishlist of that user
    wishlist = Wishlist.objects.get(user = user)
    
    # deleting the wishlist from database
    wishlist.delete()
    
    # returning to the same page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def delete_orders(request):
    if request.user.is_authenticated:
        carts = Cart.objects.filter(user = request.user)
        if carts.exists():
            for cart in carts:
                if cart.uid and not cart.is_checkedout:
                        cart.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                