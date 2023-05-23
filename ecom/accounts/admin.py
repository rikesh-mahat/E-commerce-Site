from django.contrib import admin
from .models import *
# Register your models here.
# admin.site.register([Profile, Cart, CartItems, Order])

class AdminProfile(admin.ModelAdmin):
    list_display = ['firstname', 'lastname' , 'email', 'mobile',  'address', 'mobile','status']
    list_editable = ['status']
    def firstname(self, obj):
        return obj.user.first_name
    
    def lastname(self, obj):
        return obj.user.last_name
    
    search_fields = ['email', 'address']
  
admin.site.register(Profile, AdminProfile)


class OrderAdmin(admin.ModelAdmin):
    list_display = ['ordered_by', 'shipping_address', 'mobile', 'email', 'total', 'payment', 'order_status']
    list_filter = ['payment_completed']
    search_fields = ['ordered_by', 'shipping_address', 'mobile', 'email']
    def payment(self, obj):
        status = "Paid" if obj.payment_completed else "Unpaid"
        return status
    list_editable = ['order_status']
    
admin.site.register(Order, OrderAdmin)


class AdminCart(admin.ModelAdmin):
    list_display = ['User', 'Checked']
    
    def User(self, obj):
        return obj.user.first_name + " " + obj.user.last_name
    
    def Checked(self, obj):
        return "Checked Out" if obj.is_checkedout else "Not Checked Out"
    
admin.site.register(Cart, AdminCart)