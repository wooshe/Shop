# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import random

from django.db import models
from django.db.models import Max, Min
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from main.utils import getDataForNavBaR
from shop.models import Category, Product
from shopadmin.forms import ProductCommentForm


def shop_view(request, shop_slug):
    # shop = Shop.objects.get(slug=shop_slug)
    #
    # if request.method == 'POST':
    #     return HttpResponseRedirect(reverse('shop', kwargs={'shop_slug': shop_slug}))
    # else:
    #     products_of_shop = Product.objects.filter(shop=shop)
    #     category_menu = Category.objects.filter(Q(shop=shop) | Q(parent=None))
    #
    # min_price = products_of_shop.aggregate(Min('price'))
    # max_price = products_of_shop.aggregate(Max('price'))
    #
    # min_price = str(min_price.get('price__min'))
    # max_price = str(max_price.get('price__max'))
    #
    #
    # context = {'min_price': min_price, 'max_price': max_price, 'shop': shop,
    #            'products': products_of_shop, 'category_menu': category_menu}
    # getDataForNavBaR(context, request)
    return render(request, 'shop.html', {})


def product_add_comment_view(request):
    if request.method == 'GET':
        product_comment_form = ProductCommentForm(request.GET)
        if product_comment_form.is_valid():
            product = Product.objects.get(id=request.GET.get('product_id'))


def get_random_objects(obj, count):
    ret = []

    try:
        rand = random.sample(range(0, obj.count()), count)
        for i in rand:
            ret.append(obj[i])
    except:
        pass

    return ret


def product_view(request, product_slug):
    archive = False
    try:
        product = Product.objects.get(slug=product_slug)
        product.incr_view()

    except models.ObjectDoesNotExist:
        product = Product.archive.get(slug=product_slug)
        archive = True

    obraz_products = get_random_objects(Product.objects.all(), 5)
    equal_products = get_random_objects(Product.objects.filter(category=product.category), 5)
    category_menu = Category.objects.all()

    context = {'category_menu': category_menu, 'product': product,
               'equal_products': equal_products, 'obraz_products': obraz_products, 'archive': archive}
    getDataForNavBaR(context, request)
    return render(request, 'product.html', context)
