from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from products.models import Product, Category, ProductImages, Comment
from accounts.models import Cart
from accounts.views import assign_cart, load_cart
from .forms import ProductForm
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .forms import ProductForm
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
    
    comments = productObj.comments.all()
    context = {
        'product' : productObj,
        'comments' : comments 
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
    assign_cart(request)
    load_cart(request)
    allcategoryObj = Category.objects.all()
    context = {
        'allcategory' : allcategoryObj,
    }
    del_buy_cart(request)
    
        
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
      

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/edit_product.html'
    success_url = reverse_lazy('my_product')
    
    
def delete_comment(request, uid):
    comment = Comment.objects.get(uid = uid)
    comment.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))