from django import forms
from .models import Product, ProductImages


class ProductForm(forms.ModelForm):
    product_images = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    class Meta:
        model = Product
        fields = ['product_name', 'category', 'price', 'product_description', 'owner']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'product_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'product_images': forms.ClearableFileInput(attrs={'multiple': True}),
            'owner': forms.HiddenInput(),
        }
