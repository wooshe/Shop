# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import random
import string

import json

from django.core.files import File
from django.shortcuts import render

from bonafidesale import settings
from shop.models import Category, Product, ProductPhoto, ProductSize


def main_cat(title,author,parent=None):
    cat = Category()
    cat.author = author
    cat.title = title
    cat.parent = parent
    cat.save()
    return cat

def main_product(author,category,name,description,material,model,color):
    pr = Product()
    pr.author = author
    pr.category = category
    pr.name = name
    pr.description = description
    pr.material=material
    pr.model=model
    pr.color=color
    pr.price = random.uniform( 100, 2000 )
    pr.like = random.randint(0,1000)
    pr.rating = random.uniform(1, 5)
    pr.rating_count = 500
    pr.rating_sum = int(pr.rating*500)
    pr.save()


def tester_view(request):
    if request.method == 'POST':

        if request.POST.get('form_type') == 'category_main_add':
            file_path = os.path.join(settings.STATIC_ROOT, 'category.json')
            json_data = open(file_path).read()
            data = json.loads(json_data)

            for cat in data:
                try:
                    par = Category.objects.get(title=cat['parent'])
                except:
                    par = None
                main_cat(cat['title'],request.user,par)

        elif request.POST.get('form_type') == 'rating':
            pr = Product.objects.all()

            for p in pr:

                sum = 0
                cnt = 0
                rat = 0

                people = range(10, random.randint(22, 100))

                for pe in people:
                    cnt = cnt + 1
                    sum = sum + random.randint(3, 5)

                rat = sum / cnt

                p.rating_sum = sum
                p.rating_count = cnt
                p.rating = rat
                p.like = 0
                p.save()


        elif request.POST.get('form_type') == 'category_main_remove':
            Category.objects.all().delete()

        elif request.POST.get('form_type') == 'category_add':
            pass

        elif request.POST.get('form_type') == 'category_remove':
            pass

        elif request.POST.get('form_type') == 'product_add':
            file_path = os.path.join(settings.STATIC_ROOT, 'products_.json')
            json_data = open(file_path).read()
            data = json.loads(json_data)

            for cat in data:
                categor = Category.objects.get(title=cat['kategor'])
                main_product(request.user,categor,cat['name'],cat['description'],cat['material'],cat['model'],cat['color'])


            file_path = os.path.join(settings.STATIC_ROOT, 'images.json')
            json_data = open(file_path).read()
            data = json.loads(json_data)

            for cat in data:

                try:
                    pr = Product.objects.get(name=cat['name'])
                    ph = ProductPhoto()
                    ph.author = request.user
                    ph.product = pr
                    reopen = open(os.path.join(settings.STATIC_ROOT, cat['image']),"rb")
                    django_file = File(reopen)
                    ph.image = django_file
                    ph.save()
                except Exception as e:
                    print(e)


            file_path = os.path.join(settings.STATIC_ROOT, 'size.json')
            json_data = open(file_path).read()
            data = json.loads(json_data)

            for cat in data:

                try:
                    pr = Product.objects.get(name=cat['name'])
                    ph = ProductSize()
                    ph.count = 10
                    ph.product = pr
                    ph.size = cat['size']
                    ph.save()
                    pr.save()
                except Exception as e:
                    print(e)


        elif request.POST.get('form_type') == 'product_remove':
            Product.objects.all().delete()

        elif request.POST.get('form_type') == 'shop_remove':
            pass

        elif request.POST.get('form_type') == 'shop_add':
            pass

    context = {}
    return render(request, 'tester.html', context)
