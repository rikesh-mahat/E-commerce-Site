from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, authenticate, logout
import uuid
from django.db.models import Q
from base.emails import send_account_activation_mail
from accounts.models import Profile, Cart, CartItems, Order, ORDER_STATUS, PAYMENT
from django.http import HttpResponseRedirect
from products.models import Product
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import requests as req


# Create your views here.
# assign cart to a user if he/she logins to the system
def assign_cart(request):
    cart_id = request.session.get('cart.uid',None)
    if cart_id:
        cart_obj = Cart.objects.get(uid = cart_id)
        if request.user.is_authenticated:
            cart_obj.user = User.objects.get(id = request.user.id)
            cart_obj.save()


def load_cart(request):
    if request.user.id:
        user = request.user
        cartObj = Cart.objects.filter(user = user).order_by('created_at')
        if cartObj.count():
            if not cartObj[0].is_checkedout:
                user_carts = request.user.carts.all()
                request.session['cart.uid'] = str(user_carts[0].uid)
                request.session['total_cart_items'] = user_carts[0].get_total_cartitems()
           

def login_user(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user_obj = User.objects.filter(username = email)
        
        if not user_obj.exists():
            messages.warning(request, "User does not exist please create an account first")
            return HttpResponseRedirect(request.path_info)
        
        
        if not user_obj[0].profile.is_email_verified:
            messages.warning(request,"Verify your account first")
            return HttpResponseRedirect(request.path_info)
        
        
        
        if not user_obj[0].profile.status:
            messages.warning(request, "Your account has been disabled")
            return HttpResponseRedirect(request.path_info)
        
        user_obj = authenticate(username = email, password = password)
        if user_obj:
            login(request, user_obj)
            if "next" in request.GET:
                next_url = request.GET.get("next")
                return redirect(next_url)
            else:
                return redirect('/')
        
        messages.warning(request,"Sorry the credentials do not match")    
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
        
        userObj = User.objects.filter(username = email)
        
        if userObj.exists():
            messages.warning(request, "Sorry the email is already in use")
            return HttpResponseRedirect(request.path_info)
            
        if pass1 != pass2:
            messages.warning(request, "Password do not match")
            return HttpResponseRedirect(request.path_info)
        
        registered_user = User.objects.create(first_name = first_name, last_name = last_name, email = email, username = email)
        registered_user.set_password(pass2)
        registered_user.save()
        
        
        
        
        email_token = str(uuid.uuid4())
        register_customer = Profile.objects.create(user = registered_user, address = address, mobile = mobile, email_token = email_token)
        register_customer.save()
        send_account_activation_mail(email, email_token)
        
   
        
        if "next" in request.GET:
                next_url = request.GET.get("next")
                return redirect(next_url)
        else:
                return HttpResponseRedirect(request.path_info)
        
        
        
        
    return render(request,'accounts/register.html')

def activate_user(request, email_token):
    try:
        user = Profile.objects.get(email_token=email_token)
        user.is_email_verified = True
        user.save()
        return redirect(request,'login')
    except Exception as e:
        return HttpResponse('Invalid token')
    
    
def logout_user(request):
    logout(request)
    print("============================")
    print("logging out the user from home")
    return redirect(reverse('home'))
    
def cart(request):
    assign_cart(request)
    load_cart(request)
    # user_cart = Cart.objects.get(user = request.user, is_paid = False)
    # if not user_cart.user.profile.get_cart_count():
    #     messages.info(request,f"Hello {user_cart.user.first_name.capitalize()}, no items in cart. Continue to shop and add items to your cart")
    # context = {
    #     'cart' : user_cart,
    #     'cart_items' : user_cart.cart_items.all(),
    # }
  
    
    cart_uid = request.session.get('cart.uid',None)
    
    if cart_uid:
        cartObj = Cart.objects.get(uid = uuid.UUID(cart_uid))
        
        context = {
            'cart' : cartObj,
            'cart_items' : cartObj.cart_items.all()
        }
        if not cartObj.cart_items.all().count():
            messages.info(request, 'No items in cart. Please continue shopping')
        return render(request, 'accounts/cart.html', context)
    else:
        messages.info(request, 'Add items to your cart')    
    return render(request,'accounts/cart.html') 
    

def add_to_cart(request,uid):
    assign_cart(request)
    load_cart(request)
    productObj = Product.objects.get(uid=uid)
    cart_uid = request.session.get('cart.uid', None)
    
    if cart_uid:
        
        cart = Cart.objects.get(uid = uuid.UUID(cart_uid))
       
    else:
        cart = Cart.objects.create(is_checkedout = False)
        request.session['cart.uid'] = str(cart.uid)
        print("=====================================================")
        print("the cart didn't exit so we created it haha")
        
    cart_item_obj = CartItems.objects.filter(cart = cart, product = productObj)
    if cart_item_obj.exists():
        return redirect('cart')
    cart_item = CartItems.objects.create(cart = cart, product = productObj)
    cart_item.save()
    request.session['total_cart_items'] = cart.get_total_cartitems()
# user = request.user
    
    # cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)
    
    # # if cart.user.profile.uid != user.profile.uid:
    
    # cart_item_obj = CartItems.objects.filter(cart = cart, product = product)
    # if cart.cart_items.count() > 0:
    #     if cart_item_obj.exists():
    #         return redirect('cart')
    # cart_item = CartItems.objects.create(cart=cart, product = product)
    # cart_item.save()
  
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def remove_cart(request, cart_item_uid):
    try:
        assign_cart(request)
        load_cart(request)
        cart_item = CartItems.objects.get(uid = cart_item_uid)
        cart_item.delete()
        cartObj = Cart.objects.get(uid = cart_item.cart.uid)
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
        
        if payment == "Esewa":
            return redirect(reverse('esewa') + '?o_id=' + str(orderObj.uid))
        
        return redirect('home')
    return render(request, 'accounts/checkout.html', context)

def esewa_request(request):
    o_id = request.GET.get('o_id')
    order = Order.objects.get(uid = o_id)
    context = {
        'order' : order
    }
    return render(request, 'accounts/esewa.html', context)


def esewa_verify(request):
    import xml.etree.ElementTree as ET
    o_id = request.GET.get('o_id')
    amt = request.GET.get('amt')
    refId = request.GET.get('refId')
    url ="https://uat.esewa.com.np/epay/transrec"
    d = {
        'amt': amt,
        'scd': 'EPAYTEST',
        'rid': refId,
        'pid': o_id,
    }
    resp = req.post(url, d)
    root = ET.fromstring(resp.content)
    status = root[0].strip()
    
    order_id = o_id.split('_')[1]
    orderObj = Order.objects.get(uid = order_id)
    if status == 'Success':
        orderObj.payment_completed = True
        orderObj.save()
        return redirect('home')
    else:
        return redirect('/esewa-request/?o_id='+str(order_id))  
    return redirect('home')

def customer_profile(request):
    userObj = request.user
    user = User.objects.get(id = userObj.id)
    
    orders = Order.objects.filter(cart__user = user).order_by('-created_at')
    context ={
        'orders' : orders,
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
       
        
        
        profile = Profile.objects.get(user = user)
        profile.address = address
        profile.mobile = mobile
        profile.save()
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 
        
        
    return render(request, 'accounts/profile.html', context)


def admin_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user_obj = User.objects.filter(username = email)
        
        if not user_obj.exists():
            messages.warning(request, "No such admin account exists")
            return HttpResponseRedirect(request.path_info)
        
        user_obj = authenticate(username = email, password = password)
        
        if user_obj:
            login(request, user_obj)
            return redirect('admin_dashboard')
        
        messages.warning(request,"Sorry the credentials do not match")
        return HttpResponseRedirect(request.path_info)
            
    return render(request, 'adminpages/admin_login.html')


def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    pending_orders = Order.objects.filter(order_status = "Order Received").order_by("-created_at")
    context = {
        'pending_orders' : pending_orders
    }    
    return render(request, 'adminpages/admin_dashboard.html', context)


def order_details(request, uid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    orderObj = Order.objects.get(uid = uid)
    orderItems = orderObj.cart.cart_items.all()
    context = {
        'order' : orderObj,
        'orderitems' : orderItems,
    }
    return render(request, 'adminpages/orderdetail.html', context)




def edit_order_details(request, uid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    orderObj = Order.objects.get(uid = uid)
    allstatus = ORDER_STATUS
    
    context = {
        'order' : orderObj,
        'allstatus' : allstatus,
    }
    
    if request.method == "POST":
        status = request.POST.get('status')
        orderObj.order_status = status
        orderObj.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 
    
    return render(request, 'adminpages/editorderdetail.html', context)



def view_order(request, uid):
    orderObj = Order.objects.get(uid = uid)
    order_items = CartItems.objects.filter(cart = orderObj.cart)
    context = {
        'items' : order_items,
        'order' : orderObj,
    }
    
    return render(request, 'accounts/view_order.html', context)


def search_items(request):
    
    if request.method == "GET":
        keyword = request.GET.get('keyword')
        results = Product.objects.filter(Q(product_name__icontains = keyword))
        context = {
            'keyword' : keyword,
            'results' : results,
        }
    return render(request, 'products/search.html', context)

@login_required()
def buy_item(request, uid):
    
    
    productObj = Product.objects.get(uid = uid)
    user = request.user
    
    # cart create gardiney ani sidhai checkout ma haldiney tyo cart lai done
    
    cart = Cart.objects.create(user = user, is_checkedout = True)
    
    # item in cart
    CartItems.objects.create(cart = cart, product = productObj)
    
    # context pass gardiney checkout form lai
    context ={
        'items' : cart.cart_items.all(),
        'cart': cart,
        'payments' : PAYMENT,
    }
    if request.method == "POST":
        cart = cart
        ordered_by = request.POST.get("username")
        email = request.POST.get("email")
        mobile  = request.POST.get("mobile")
        shipping_address = request.POST.get("address")
        total = cart.get_cart_total()
        
        orderObj = Order.objects.create(cart = cart, ordered_by = ordered_by, shipping_address = shipping_address, mobile = mobile, email = email, total = total)
        orderObj.save()
        
        payment = request.POST.get('payment')
        
        if payment == "Esewa":
            return redirect(reverse('esewa') + '?o_id=' + str(orderObj.uid))
        
    
   
    return render(request, 'accounts/checkout.html', context)
    
    
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def display_users(request):
    profile_list = Profile.objects.all()
    paginator = Paginator(profile_list, 1) # Show 10 profiles per page
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
    user = Profile.objects.get(uid = uid)
    if user.status:
        user.status = False
    else:
        user.status = True
    user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))