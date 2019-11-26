# -*- coding: utf-8 -*-
from django import forms
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from order.models import Order
from shop.models import Category, Product, ProductPhoto, ProductSize, ProductComment, ProductSale


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('title', 'parent')

    def __init__(self, *args, **kwargs):
        self_cat_id = kwargs.pop('self_cat_id', None)
        super(CategoryForm, self).__init__(*args, **kwargs)  # populates the post

        if self_cat_id is None:
            self.fields['parent'].queryset = Category.objects.all()
        else:
            self.fields['parent'].queryset = Category.objects.all().exclude(
                id=self_cat_id)

    def clean(self):
        pass

    def save(self, cat, user):
        title = self.cleaned_data['title']
        parent = self.cleaned_data['parent']
        cat.author = user
        cat.title = title
        cat.parent = parent
        cat.save()


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('category', 'name', 'description', 'model', 'material', 'color', 'base_price', 'sale', 'price', 'deleted', 'with_size')

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)  # populates the post
        self.fields['category'].queryset = Category.objects.all()
        self.fields['deleted'].widget.attrs['disabled'] = True
        self.fields['price'].widget.attrs['disabled'] = True

    def clean(self):
        pass

    def save(self, new_product, request, user):
        category = self.cleaned_data['category']
        name = self.cleaned_data['name']
        description = self.cleaned_data['description']
        model = self.cleaned_data['model']
        material = self.cleaned_data['material']
        color = self.cleaned_data['color']
        with_size = self.cleaned_data['with_size']
        sale = self.cleaned_data['sale']
        base_price = self.cleaned_data['base_price']

        new_product.author = user
        new_product.category = category
        new_product.name = name
        new_product.description = description
        new_product.model = model
        new_product.material = material
        new_product.color = color
        new_product.with_size = with_size
        new_product.sale = sale
        new_product.base_price = base_price
        new_product.save()

        file_list = request.FILES.getlist('image')
        if file_list.__len__() > 0:

            for file in file_list:
                new_photo = ProductPhoto()

                new_photo.author = request.user
                new_photo.product = new_product
                new_photo.image = file
                new_photo.save()


class StatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('status',)


class SizeForm(forms.ModelForm):
    class Meta:
        model = ProductSize
        fields = ('size', 'count', 'id')

class SaleForm(forms.ModelForm):
    class Meta:
        model = ProductSale
        fields = ('promo', 'sale', 'id')


class ProductCommentForm(forms.ModelForm):
    class Meta:
        model = ProductComment
        fields = ('comment',)


class NotificationForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput)

    def __init__(self, *args, **kwargs):
        super(NotificationForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = 'Email'
        self.fields['email'].help_text = 'Email'
