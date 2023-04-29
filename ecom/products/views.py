from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from products.models import Product, Category, ProductImages, Comment
from accounts.models import Cart
from .forms import ProductForm
from django.core.paginator import Paginator
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .forms import ProductForm
# Create your views here.


    
def home(request):
    products = Product.objects.all().order_by('-created_at')
    paginator = Paginator(products, 4)
    page_number = request.GET.get('page', 1)
    productsData = paginator.get_page(page_number)
    
   
    return render(request, 'products\home.html', {'products': productsData})

def get_product(request, slug):
   
    productObj  = Product.objects.get(slug=slug)
    productObj.view_count += 1
    productObj.save()
    
    
    other_products = Product.objects.all()
    paginator = Paginator(other_products, 5)
    page_number = request.GET.get('p')
    other_products_data = paginator.get_page(page_number)
    
    comments = productObj.comments.all()
    paginator = Paginator(comments, 4)
    page_number = request.GET.get('page')
    commentsData = paginator.get_page(page_number)
    
    
    context = {
        'product' : productObj,
        'comments' : commentsData,
        'products': other_products_data,
        'slug' : slug
    }
    if request.method == "POST":
        user_comment = request.POST.get('comment')
        user = request.user
        product = productObj
        
        comment =  Comment.objects.create(user = user, text = user_comment, product = product)
        comment.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
    return render(request, 'products\product.html', context)



def get_all_products(request):
    
    allcategoryObj = Category.objects.all()
    context = {
        'allcategory' : allcategoryObj,
    }
    
    
        
    return render(request, 'products/allproducts.html', context)



def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user  # Set the owner field to the current user
            product.save()
            # Save product images
            for image in request.FILES.getlist('product_images'):
                ProductImages.objects.create(product=product, image=image)
            return redirect('home')
    else:
        form = ProductForm()
    return render(request, 'products/create_product.html', {'form': form})



def display_user_product(request):
    if request.user.is_authenticated:
        user_products = Product.objects.filter(owner = request.user)
        context = {'products' : user_products}
        print(user_products)
        return render(request, 'products/user_product.html', context)
    
    
def delete_product(request, uid):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, uid = uid)
        product.delete()
    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 
      



def update_product(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.instance.owner = request.user
            form.save()
            return redirect('my_product')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/edit_product.html', {'form': form})


    
    
def delete_comment(request, uid):
    comment = Comment.objects.get(uid = uid)
    comment.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))