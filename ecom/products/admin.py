from django.contrib import admin
from .models import *
# Register your models here.


class ProductImageAdmin(admin.StackedInline):
    model = ProductImages
    


class AdminProduct(admin.ModelAdmin):
    inlines = [ProductImageAdmin]
    list_display = ['product_name', 'product_description', 'slug', 'owner', 'price', 'sold', 'category']

    search_fields = ['product_name', 'price']

    def sold(self, obj):
        status = "Sold" if obj.is_sold else "Unsold"
        return status

    list_editable = ['category']
    
admin.site.register(Product, AdminProduct)



class AdminCategory(admin.ModelAdmin):
    list_display = ['category_name']
    search_fields = ['category_name']
    
    
admin.site.register(Category, AdminCategory)