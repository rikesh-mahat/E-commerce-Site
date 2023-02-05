from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from .models import Product, Category
from accounts.models import Cart
from accounts.views import assign_cart, load_cart
# Create your views here.

def del_buy_cart(request):
    if request.META.get('HTTP_REFERER'):
        if "buy_product" in request.META.get('HTTP_REFERER'):
            carts = Cart.objects.filter(user = request.user).order_by('-created_at')
            carts[0].delete()
    
def home(request):
    assign_cart(request)
    load_cart(request)
    products = Product.objects.all()
    context = {
        'products' : products
    }
    
    del_buy_cart(request)
    return render(request, 'products\home.html', context)

def get_product(request, slug):
    assign_cart(request)
    load_cart(request)
    productObj  = Product.objects.get(slug=slug)
    productObj.view_count += 1
    productObj.save()
    context = {
        'product' : productObj
    }
    
    return render(request, 'products\product.html', context)



def get_all_products(request):
    assign_cart(request)
    load_cart(request)
    allcategoryObj = Category.objects.all()
    context = {
        'allcategory' : allcategoryObj,
    }
    del_buy_cart(request)
    
        
    return render(request, 'products/allproducts.html', context)


