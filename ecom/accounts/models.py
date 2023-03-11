from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver

from products.models import Product
# Create your models here.
    
class Profile(BaseModel):
    user  = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=200, null = True, blank = True)
    profile_image = models.ImageField(upload_to="profile")
    address = models.CharField(max_length=200, null = True, blank = True)
    mobile = models.PositiveBigIntegerField(null=True, blank=True)
    status = models.BooleanField(default = False)
    
    def get_cart_count(self):
        return CartItems.objects.filter(cart__is_paid = False, cart__user = self.user).count()
    
    def __str__(self):
        return self.user.username
    
    

            
    
class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='carts', null=True, blank=True)
    is_checkedout = models.BooleanField(default=False)
    
    def __str__(self):
        return 'Cart Id ' + str(self.uid)
    
    
    def get_cart_total(self):
        cart_items = self.cart_items.all()
        price = []
        for cart_item in cart_items:
            price.append(cart_item.product.price)
        return sum(price)
    
    def get_total_cartitems(self):
        total = self.cart_items.all().count()
        return total
    
class CartItems(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True,related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product")
    
    
    def __str__(self):
        return self.product.product_name
   
ORDER_STATUS = (
    ("Order Received","Order Received"),
    ("Order Processing","Order Processing"),
    ("On the Way","On the Way"),
    ("Order Completed","Order Completed"),
    ("Order Cancelled","Order Cancelled"),
) 

PAYMENT = (
    ("Cash On Delivery", "Cash On Delivery"),
    ("Khalti", "Khalti"),
    ("Esewa", "Esewa"),
)  
class Order(BaseModel):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, null=True, blank=True,related_name='orders')
    ordered_by = models.CharField(max_length=200)
    shipping_address = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(null = True, blank=True)
    total = models.PositiveIntegerField()
    order_status = models.CharField(max_length=50, choices = ORDER_STATUS, default = ORDER_STATUS[0][0])
    payment_method = models.CharField(max_length = 50, choices = PAYMENT, default = PAYMENT[0][0])
    payment_completed = models.BooleanField(default=False, null = True, blank = True)
    def __str__(self):
        return "Order: " + str(self.uid)