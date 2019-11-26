# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from order.models import CartItem, Cart, Order


class CartAdmin(admin.ModelAdmin):
    list_display = ['id','user', 'price_all']
    list_filter = ['id','user', 'price_all']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'date', 'status', 'price_all', 'pay', 'pr_barcode', 'send_confirm']
    list_filter = ['id', 'user', 'date', 'status', 'price_all', 'pay', 'pr_barcode', 'send_confirm']


class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'count', 'price_all']
    list_filter = ['id', 'product', 'count', 'price_all']


admin.site.register(Order, OrderAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
