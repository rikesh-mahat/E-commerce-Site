from django.contrib import admin
from .models import *
# Register your models here.
# admin.site.register([Profile, Cart, CartItems, Order])

class AdminProfile(admin.ModelAdmin):
    list_display = ['firstname', 'lastname' , 'email', 'mobile',  'address', 'mobile','status']
    
    def firstname(self, obj):
        return obj.user.first_name
    
    def lastname(self, obj):
        return obj.user.last_name
    
    search_fields = ['email', 'address']
  
admin.site.register(Profile, AdminProfile)

'''
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, null=True, blank=True,related_name='orders')
    ordered_by = models.CharField(max_length=200)
    shipping_address = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(null = True, blank=True)
    total = models.PositiveIntegerField()
    order_status = models.CharField(max_length=50, choices = ORDER_STATUS, default = ORDER_STATUS[0][0])
    payment_method = models.CharField(max_length = 50, choices = PAYMENT, default = PAYMENT[0][0])
    payment_completed = models.BooleanField(default=False, null = True, blank = True)
'''
class OrderAdmin(admin.ModelAdmin):
    list_display = ['ordered_by', 'shipping_address', 'mobile', 'email', 'total', 'payment', 'order_status']
    
    def payment(self, obj):
        status = "Paid" if obj.payment_completed else "Unpaid"
        return status
    list_editable = ['order_status']
    
admin.site.register(Order, OrderAdmin)