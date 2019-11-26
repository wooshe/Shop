# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.postgres.search import *
from django.db.models import Min, Max
from django.http import JsonResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext

from bonafidesale import settings
from main.utils import getUserCart, getDataForNavBaR, get_min_max, sorter, send_html_email
from shop.models import Product, Category

import math

from shop.views import get_random_objects


def handler400(request, exception=None, template_name="e400.html"):
    context = {}
    getDataForNavBaR(context, request)
    return render(request, 'e400.html', context, status=400)

def handler403(request, exception=None, template_name="e403.html"):
    context = {}
    getDataForNavBaR(context, request)
    return render(request, 'permission.html', context, status=403)

def handler404(request, exception=None, template_name="e404.html"):
    context = {}
    getDataForNavBaR(context, request)
    return render(request, 'e404.html', context, status=404)

def handler500(request, exception=None, template_name="e500.html"):
    context = {}
    getDataForNavBaR(context, request)
    return render(request, 'e500.html', context, status=500)


def about_view(request):
    context = {}
    getDataForNavBaR(context, request)
    return render(request, 'about.html', context)


def delivery_view(request):
    context = {}
    getDataForNavBaR(context, request)
    return render(request, 'delivery.html', context)


def return_view(request):
    context = {}
    getDataForNavBaR(context, request)
    return render(request, 'return.html', context)


def police_view(request):
    context = {}
    getDataForNavBaR(context, request)
    return render(request, 'police.html', context)


def user_confirm_view(request):
    context = {}
    getDataForNavBaR(context, request)
    return render(request, 'user_confirm.html', context)


def oferta_view(request):
    context = {}
    getDataForNavBaR(context, request)
    return render(request, 'oferta.html', context)


def back_view(request):
    try:
        name = request.GET.get('name')
        email = request.GET.get('email')
        phone = request.GET.get('phone')
        message = request.GET.get('message')

        context = {"email": email, "phone": phone, "name": name, "message": message, }
        send_html_email(request, 'back.html', 'Вопрос с сайта', "support@bonafidesale.ru", context)
    except:
        return JsonResponse({'null': "null"})

    return JsonResponse({'null': "null"})


def catalog_view(request, category=None):
    cart = getUserCart(request)

    query = request.GET.get('query')

    active_link = None

    if query != None:
        all_product = Product.objects.annotate(search=SearchVector('name', 'description')).filter(search=query)

    elif category == 'all' or category == None:
        all_product = Product.objects.all()
        active_link = "catalog"

    elif category == 'sale':
        all_product = Product.objects.all().filter(sale__gt=0)
        active_link = "sale"

    elif category != None:
        cat = Category.objects.get(slug=category)
        active_link = cat.get_absolute_url()
        all_product = Product.objects.filter(category=cat)

    if query == None:
        query = ''
    context = {}
    get_min_max(all_product, context)

    if all_product.count() <= 20:
        all_pagination_end = 'True'
    else:
        all_pagination_end = 'False'

    all_product = sorter(all_product, "sort_by_price", 'sort_from_zero')[0:settings.PAGINATION_ELEMENT]

    context.update({'products': all_product, 'cart': cart, 'active_link': active_link, 'query': query,
                    'all_pagination_end': all_pagination_end})

    getDataForNavBaR(context, request)
    return render(request, 'catalog.html', context)


def main_view(request):
    cart = getUserCart(request)

    # all_product = Product.objects.all().exclude(Q(size__isnull=True))

    all_product = Product.objects.all()[0:10]
    min_price = all_product.aggregate(Min('price'))
    max_price = all_product.aggregate(Max('price'))

    min_price = str(min_price.get('price__min'))
    max_price = str(max_price.get('price__max'))

    pop_products = Product.objects.all().order_by('-count_buy')

    pop_products = get_random_objects(pop_products[0:40], 10)

    rating_products = Product.objects.all().order_by('-rating')

    rating_products = get_random_objects(rating_products[0:40], 10)

    context = {'min_price': min_price, 'max_price': max_price,
               'products': all_product, 'cart': cart, 'cat_range': range(2), 'pop_products': pop_products,
               'rating_products': rating_products}

    getDataForNavBaR(context, request)

    category_menu = context['category_menu']
    count = math.ceil((category_menu.count() / 2))
    range_group = range(count)

    bbx = {}
    cur = -1
    p = 0

    for cat in category_menu:

        if p % 2 == 0:
            cat.top = True
        else:
            cat.top = False

        p = p + 1

    for g in range_group:
        val = {}
        cur = cur + 1
        val[0] = g + cur
        val[1] = cur + 1 + g

        bbx[g] = val

    context.update({'group': bbx})

    return render(request, 'main.html', context)
