from django.shortcuts import render, redirect
from .models import Product, Category
from accounts.views import assign_cart, load_cart
# Create your views here.
def home(request):
    assign_cart(request)
    load_cart(request)
    products = Product.objects.all()
    context = {
        'products' : products
    }
    
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
    
        
    return render(request, 'products/allproducts.html', context)


