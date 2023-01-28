
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, authenticate, logout
import uuid
from base.emails import send_account_activation_mail
from . models import Profile, Cart, CartItems, Order
from django.http import HttpResponseRedirect
from products.models import Product
from django.urls import reverse
from django.contrib.auth.decorators import login_required


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
        cartObj = Cart.objects.filter(user = user)
        print(cartObj[len(cartObj)-1])
        # if not cartObj[0].is_checkedout:
         
        #     user_carts = request.user.carts.all()
            
        #     request.session['cart.uid'] = str(user_carts[0].uid)
        #     request.session['total_cart_items'] = user_carts[0].get_total_cartitems()
           

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
        return redirect('home')
    return render(request, 'accounts/checkout.html', context)


def customer_profile(request):
    return render(request, 'accounts/profile.html')