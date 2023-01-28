from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register([ProductImages, Category])

class ProductImageAdmin(admin.StackedInline):
    model = ProductImages
    
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]


admin.site.register(Product, ProductAdmin)

