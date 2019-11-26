# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from main.utils import getDataForNavBaR, message, render_template, get_permission
from order.models import Order
from order.pochta import pr_get_doc, pr_tracking
from shop.models import Category, Product, ProductPhoto, ProductSize, ProductSale
from shopadmin.forms import CategoryForm, ProductForm, StatusForm, SizeForm, SaleForm


def update(request, categorys, ctx):
    get_permission(request)
    category_response = render_template('shopadmin_category_main.html', {'category': categorys}, request)
    category_form_response = render_template('shopadmin_category_form.html', {'category_form': CategoryForm()},
                                             request)

    EmptySizeFormSet = modelformset_factory(ProductSize, form=SizeForm, can_delete=True, extra=3)
    empty_size_formset = EmptySizeFormSet(queryset=ProductSize.objects.none(), prefix="empty_form")

    product_form_response = render_template('shopadmin_product_form.html', {'empty_size_formset': empty_size_formset,
                                                                            'product_form': ProductForm()},
                                            request)
    products = Product.objects.all()
    main_product_response = render_template('shopadmin_product_main.html', {'products': products}, request)
    ctx.update({'main_product_response': main_product_response, 'product_form_response': product_form_response,
                'category_form_response': category_form_response, 'category_response': category_response, })


def category_remove_view(request):
    get_permission(request)
    if request.method == 'GET':
        category_id = request.GET.get('category_id')
        user = request.user
        category = Category.objects.get(id=category_id)

        if category.author != user:
            return HttpResponseRedirect(reverse('permission'))

        if request.GET.get('method') == 'get_about_delete':

            related_category = category.get_descendants(include_self=True)
            for r in related_category:
                r.related_product = Product.objects.filter(category=r)
            category_related = render_template('shopadmin_category_related.html',
                                               {'category': category, 'related_category': related_category}, request)
            return JsonResponse({'result': 'success', 'category_related': category_related, })

        elif request.GET.get('method') == 'delete':
            category.delete()
            categorys = Category.objects.all()
            ctx = {'result': 'success', 'message': message("Категория удалена!", request)}
            update(request, categorys, ctx)
            return JsonResponse(ctx)


def category_edit_view(request):
    get_permission(request)
    if request.method == 'GET':
        category_id = request.GET.get('category_id')
        user = request.user
        category = Category.objects.get(id=category_id)
        category_form_edit = CategoryForm(instance=category, self_cat_id=category_id)
        try:
            parent = category.parent.id
        except:
            parent = None

        category_form_edit_response = render_template('shopadmin_category_form_edit.html',
                                                      {'category_form_edit': category_form_edit}, request)

        return JsonResponse({'result': 'success', 'category_form_edit_response': category_form_edit_response,
                             'parent': parent})

    if request.method == 'POST':
        user = request.user

        category_form_edit = CategoryForm(request.POST)
        if category_form_edit.is_valid():

            cat = Category.objects.get(id=request.POST.get('category_id'))

            category_form_edit.save(cat, user)

            categorys = Category.objects.all()

            ctx = {'result': 'success', 'message': message("Категория изменена!", request)}
            update(request, categorys, ctx)
            return JsonResponse(ctx)
        else:
            category_form_edit_response = render_template('shopadmin_category_form_edit.html',
                                                          {'category_form_edit': category_form_edit}, request)
            return JsonResponse({'result': 'error', 'category_form': category_form_edit_response})


def category_add_view(request):
    get_permission(request)
    if request.method == 'POST':
        user = request.user

        category_form = CategoryForm(request.POST)
        if category_form.is_valid():

            cat = Category()
            category_form.save(cat, user)
            categorys = Category.objects.all()

            ctx = {'result': 'success', 'message': message("Категория добавлена!", request)}
            update(request, categorys, ctx)
            return JsonResponse(ctx)
        else:
            category_form_response = render_template('shopadmin_category_form.html', {'category_form': category_form},
                                                     request)
            return JsonResponse({'result': 'error', 'category_form': category_form_response})

def sale_add_view(request):
    get_permission(request)
    if request.method == 'POST':
        user = request.user

        sale_form = SaleForm(request.POST)
        if sale_form.is_valid():

            sal = ProductSale()
            sal.promo = sale_form.cleaned_data['promo']
            sal.sale  = sale_form.cleaned_data['sale']
            sal.save()



            sale_response = render_template('shopadmin_sale.html',
                                                    {'sal': sal},
                                                    request)

            ctx = {'result': 'success','sale_response':sale_response, 'message': message("Промокод добавлен!", request)}
            return JsonResponse(ctx)
        else:
            sale_form_response = render_template('shopadmin_sale_form.html', {'sale_form': sale_form},
                                                     request)
            return JsonResponse({'result': 'error', 'sale_form_response': sale_form_response})

def sale_remove_view(request):
    get_permission(request)
    if request.method == 'GET':
        sale_id = request.GET.get('sale_id')
        user = request.user
        sale = ProductSale.objects.get(id=sale_id)
        sale.delete()
        return JsonResponse({'result': 'success', 'message': message("Промокод удален!", request)})

def product_remove_view(request):
    get_permission(request)
    if request.method == 'GET':
        product_id = request.GET.get('product_id')
        user = request.user
        product = Product.objects.get(id=product_id)
        if product.author != user:
            return HttpResponseRedirect(reverse('permission'))

        product.delete()
        return JsonResponse({'result': 'success', 'message': message("Товар удален!", request)})


def product_photo_remove_view(request):
    get_permission(request)
    if request.method == 'GET':
        photo_id = request.GET.get('photo_id')
        photo = ProductPhoto.objects.get(id=photo_id)
        photo.delete()
        return JsonResponse({'result': 'success', })


def product_edit_view(request):
    get_permission(request)
    if request.method == 'GET':
        product_id = request.GET.get('product_id')
        user = request.user

        product = Product.objects.get(id=product_id)
        product_form_edit = ProductForm(instance=product)
        photos = product.product_photo.all()

        SizeFormSet = modelformset_factory(ProductSize, form=SizeForm, can_delete=True, extra=1)
        size_formset = SizeFormSet(queryset=ProductSize.objects.filter(product=product))

        product_form_edit_response = render_template('shopadmin_product_form_edit.html',
                                                     {'size_formset': size_formset, 'product': product,
                                                      'product_form_edit': product_form_edit, 'photos': photos},
                                                     request)
        return JsonResponse({'product_form_edit_response': product_form_edit_response, 'result': 'success'})

    if request.method == 'POST':
        user = request.user

        product_form_edit = ProductForm(request.POST)

        type_post = request.POST.get('type_post')

        SizeFormSet = modelformset_factory(ProductSize, form=SizeForm, can_delete=True, extra=1)
        size_formset = SizeFormSet(request.POST)

        if product_form_edit.is_valid() and size_formset.is_valid():

            if type_post == "check_form":
                return JsonResponse({'result': 'success_check_form'})
            elif type_post == "confirm_form":

                size_formset.save(commit=False)

                for object in size_formset.deleted_objects:
                    object.delete()

                for object in size_formset.changed_objects:
                    object[0].save()

                for object in size_formset.new_objects:
                    object.product = Product.objects.get(id=request.POST.get('product_id'))
                    object.save()

                new_product = Product.objects.get(id=request.POST.get('product_id'))
                product_form_edit.save(new_product, request, user)
                products = Product.objects.all()
                main_product_response = render_template('shopadmin_product_main.html', {'products': products}, request)

                return JsonResponse({'main_product_response': main_product_response, 'result': 'success',
                                     'message': message("Продукт изменен!", request)})
        else:
            photos = None
            product = Product.objects.get(id=request.POST.get('product_id'))
            product_form_edit_response = render_template('shopadmin_product_form_edit.html',
                                                         {'size_formset': size_formset, 'product': product,
                                                          'product_form_edit': product_form_edit,
                                                          'photos': photos},
                                                         request)
            return JsonResponse({'product_form_edit_response': product_form_edit_response, 'result': 'error'})


def product_add_view(request):
    get_permission(request)
    if request.method == 'POST':
        user = request.user
        product_form = ProductForm(request.POST)

        type_post = request.POST.get('type_post')

        EmptySizeFormSet = modelformset_factory(ProductSize, form=SizeForm, can_delete=True)
        empty_size_formset = EmptySizeFormSet(request.POST, prefix="empty_form")

        if product_form.is_valid() and empty_size_formset.is_valid():

            if type_post == "check_form":
                return JsonResponse({'result': 'success_check_form'})
            elif type_post == "confirm_form":

                new_product = Product()
                product_form.save(new_product, request, user)

                empty_size_formset.save(commit=False)

                for object in empty_size_formset.new_objects:
                    object.product = new_product
                    object.save()

                products = Product.objects.all()
                main_product_response = render_template('shopadmin_product_main.html', {'products': products}, request)
                EmptySizeFormSet = modelformset_factory(ProductSize, form=SizeForm, can_delete=True, extra=3)
                empty_size_formset = EmptySizeFormSet(queryset=ProductSize.objects.none(), prefix="empty_form")
                photos = None
                product_form_response = render_template('shopadmin_product_form.html',
                                                        {'product_form': ProductForm(),
                                                         'empty_size_formset': empty_size_formset, 'photos': photos},
                                                        request)
                return JsonResponse(
                    {'product_form_response': product_form_response, 'main_product_response': main_product_response,
                     'result': 'success',
                     'message': message("Продукт добавлен!", request)})
        else:
            photos = None
            product_form_response = render_template('shopadmin_product_form.html',
                                                    {'product_form': product_form,
                                                     'empty_size_formset': empty_size_formset, 'photos': photos},
                                                    request)
            return JsonResponse({'product_form_response': product_form_response, 'result': 'error'})


@login_required(login_url='permission')
def shopadmin_view(request):
    get_permission(request)
    method = request.GET.get('method')

    if method == 'doc_download':

        try:
            order = Order.objects.get(id=request.GET.get('id'))
            ret = pr_get_doc(order.pr_batch_name)
            if ret['ret_status'] == 'success':
                return JsonResponse({'h': reverse('main') + ret['url'], 'result': 'success'})
            else:
                return JsonResponse({'result': 'error'})
        except:
            return JsonResponse({'result': 'error'})

    elif method == 'get_track':

        try:
            order = Order.objects.get(id=request.GET.get('id'))
            tracking = pr_tracking(order.pr_barcode)
            if tracking['ret_status'] == 'success':
                return JsonResponse({'status': tracking['status'], 'result': 'success'})
            else:
                return JsonResponse({'result': 'error'})
        except:
            return JsonResponse({'result': 'error'})

    if request.GET.get('method') == 'get_order':
        try:
            order = Order.objects.get(id=request.GET.get('order_id'))
            order_response = render_template('order_expand.html', {'admin':'true','order': order}, request)
            return JsonResponse({'order_response': order_response, 'result': 'success'})
        except:
            return JsonResponse({'result': 'error'})

    if request.GET.get('method') == 'order_confirm_delivery':
        try:
            order = Order.objects.get(id=request.GET.get('order_id'))
            order.send_confirm = True
            order.save()
            return JsonResponse({'result': 'success'})
        except:
            return JsonResponse({'result': 'error'})

    orders = Order.objects.all()
    statusForm = StatusForm()

    product_form = ProductForm()
    products = Product.objects.all()[0:10]

    category_form = CategoryForm()
    category = Category.objects.all()

    sale_form = SaleForm()
    sale = ProductSale.objects.all()


    SizeFormSet = modelformset_factory(ProductSize, form=SizeForm)
    size_formset = SizeFormSet()

    EmptySizeFormSet = modelformset_factory(ProductSize, form=SizeForm, can_delete=True, extra=3)
    empty_size_formset = EmptySizeFormSet(queryset=ProductSize.objects.none(), prefix="empty_form")
    context = {
        'product_form': product_form, 'sale_form': sale_form, 'product_form_edit': ProductForm(), 'products': products, 'photos': None,
        'category': category, 'category_form': category_form, 'category_form_edit': CategoryForm(),
        'related_category': None,
        'orders': orders, 'statusForm': statusForm, 'size_formset': size_formset,
        'empty_size_formset': empty_size_formset, 'sale':sale
    }
    getDataForNavBaR(context, request)
    return render(request, 'shopadmin.html', context)
