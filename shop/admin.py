# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

from django.contrib import admin
from django.db import models
from mptt.admin import MPTTModelAdmin

from shop.models import Product, Category, ProductPhoto, ProductSize, Notification, ProductSale


class ProductPhotoInline(admin.TabularInline):
    fk_name = 'product'
    model = ProductPhoto

class ProductSizeInline(admin.TabularInline):
    fk_name = 'product'
    model = ProductSize




@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductSizeInline, ProductPhotoInline,]
    list_display = ['name', 'slug','author','category','price', 'with_size','count_buy','count_view','deleted']
    readonly_fields = ["price",]

    list_per_page = sys.maxsize

    def get_queryset(self, request):
        return self.model.archive.all()

    class Media:
        js = ('/static/js/admin/ad.js',)

    # def delete_queryset(self, request, queryset):
    #
    #     for q in queryset:
    #         q.deleted = True
    #         q.save()


admin.site.register(Notification)
admin.site.register(ProductSize)
admin.site.register(ProductPhoto)
admin.site.register(ProductSale)

admin.site.register(Category,MPTTModelAdmin,list_display=(
        'title',
        'parent',
    ),ordering = ('title',))