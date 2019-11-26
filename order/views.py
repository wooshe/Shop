# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from main.utils import getUserCart, getDataForNavBaR, render_template, message
from order.models import Order
from order.payment import register_pay
from order.pochta import pr_address_normalize, pr_pre_calc
from shop.models import Notification, ProductSize, Product, ProductSale
from shopadmin.forms import NotificationForm
from user.forms import AddressForm


def cart_view(request, ):
    cart = getUserCart(request)

    cart.CalculatePrice()

    if request.user.is_authenticated:
        address_form = AddressForm(instance=request.user.profile)
        with_save = "true"
    else:
        address_form = AddressForm()
        with_save = "false"

    delivery_total = 0
    delivery_max_day = 0
    delivery_min_day = 0

    try:
        info = address_form.initial
        normalize = pr_address_normalize(info['country'], info['region'],
                                         info['area'], info['city'],
                                         info['street'], info['house'],
                                         info['room'], info['index'])

        if normalize['ret_status'] == 'success':
            delivery_total_ret = pr_pre_calc(normalize['body']['index'])
            delivery_total = delivery_total_ret['total_nds']
            delivery_max_day = delivery_total_ret['max-days']
            delivery_min_day = delivery_total_ret['min-days']

    except:
        pass

    delivery_and_cart_price = cart.price_all + delivery_total

    context = {
        'cart': cart,
        'address_form': address_form, 'with_save': with_save,
        'delivery_price': delivery_total, "delivery_and_cart_price": delivery_and_cart_price,
        'delivery_max_day': delivery_max_day, 'delivery_min_day': delivery_min_day
    }

    order_id = request.GET.get('order_id')
    if order_id != None and order_id != 'undefined':
        ord = Order.objects.get(id=order_id)
        cart.cart_from_order(ord)
        context['message_act'] = 'true'
        context['message'] = message("Оплата не произведена, попробуйте еще раз!", request)

    getDataForNavBaR(context, request)
    return render(request, 'cart.html', context)


def add_to_cart_view(request):
    if request.method == 'GET':
        cart = getUserCart(request)
        product_id = request.GET.get('product_id')
        size_id = request.GET.get('size_id')
        result = cart.add_to_cart(product_id, size_id)
        return JsonResponse({'cart_count': cart.items.count(), 'result': result})


def create_notification_view(request):
    if request.method == 'POST':
        user = request.user
        product_id = request.POST.get('product_id')
        size_id = request.POST.get('size_id')
        type = request.POST.get('type')
        noty_kind = request.POST.get('noty_kind')

        if type == 'notify_product':
            template = 'notification.html'
        else:
            template = 'notification_size.html'

        notification_form = NotificationForm(request.POST)
        if notification_form.is_valid():

            new_notification = Notification()
            new_notification.email = notification_form.cleaned_data['email']

            if type == 'notify_product':
                new_notification.product = Product.objects.get(id=product_id)
                new_notification.product_notify = True
            else:
                if noty_kind == 'noty_product':
                    new_notification.product = Product.objects.get(id=product_id)
                    new_notification.product_notify = True
                else:
                    new_notification.product_size = ProductSize.objects.get(id=size_id)
                    new_notification.product_notify = False

            if user.is_authenticated:
                new_notification.user = user
            else:
                new_notification.sk = str(request.session.session_key)
            new_notification.save()

            notification_form_response = render_template(template,
                                                         {'size_id': size_id, 'product_id': product_id, 'type': type,
                                                          'notification_form': NotificationForm()},
                                                         request)

            ctx = {'result': 'success', 'message': message("Вы подписались!", request),
                   'notification_form_response': notification_form_response}
            return JsonResponse(ctx)
        else:

            notification_form_response = render_template(template,
                                                         {'size_id': size_id, 'product_id': product_id, 'type': type,
                                                          'notification_form': notification_form},
                                                         request)
            return JsonResponse({'result': 'error', 'notification_form_response': notification_form_response})


def change_item_count_view(request):
    if request.method == 'GET':
        cart = getUserCart(request)
        item_id = request.GET.get('item_id')
        size_id = request.GET.get('size_id')
        count = request.GET.get('count')
        cart_item = cart.change_item_count(item_id, size_id, count)
        return JsonResponse(
            {'cart_item_price_all': cart_item.price_all, 'item_id': item_id, 'cart_price_all': cart.price_all})


def remove_from_cart_view(request):
    if request.method == 'GET':
        cart = getUserCart(request)
        product_id = request.GET.get('product_id')
        size_id = request.GET.get('size_id')
        cart.remove_from_cart(product_id, size_id)
        return JsonResponse(
            {'cart_count': cart.items.count(), 'cart_price_all': cart.price_all})


def remove_all_from_cart_view(request):
    if request.method == 'GET':
        cart = getUserCart(request)
        cart.remove_all_from_cart()
        return JsonResponse(
            {'cart_count': cart.items.count()})


def to_order_view(request):
    if request.method == 'GET':
        method = request.GET.get('method')

        if method == "check_form":

            address_form = AddressForm(request.GET)

            if address_form.is_valid():
                info = address_form.cleaned_data
                normalize = pr_address_normalize(info['country'], info['region'],
                                                 info['area'], info['city'],
                                                 info['street'], info['house'],
                                                 info['room'], info['index'])

                if normalize['ret_status'] == 'success':
                    delivery_total_ret = pr_pre_calc(normalize['body']['index'])
                    delivery_total = delivery_total_ret['total_nds']
                    delivery_max_day = delivery_total_ret['max-days']
                    delivery_min_day = delivery_total_ret['min-days']

                    address_change_form_response = render_template('address_change.html',
                                                                   {'address_form': address_form, 'with_save': "true"},
                                                                   request)

                    cart = getUserCart(request)

                    if cart.items.count() == 0:
                        return JsonResponse({'result': 'error'})

                    address_form.set_readonly()

                    sale_code = request.GET.get('sale_code')
                    sale_result = 0;

                    try:
                        sale = ProductSale.objects.get(promo=sale_code)
                        val = cart.price_all * Decimal(sale.sale) / 100
                        delivery_and_cart_price = cart.price_all - val + delivery_total
                        sale_result = sale.sale
                    except:
                        delivery_and_cart_price = cart.price_all + delivery_total

                    order_body_response = render_template('order_body.html',
                                                          {'delivery_max_day': delivery_max_day,
                                                           'delivery_min_day': delivery_min_day,
                                                           "delivery_and_cart_price": delivery_and_cart_price,
                                                           'delivery_price': delivery_total, 'cart': cart,
                                                           'address_form': address_form,
                                                           'with_save': "false", 'sale': sale_result},
                                                          request)

                    return JsonResponse(
                        {'result': 'success', 'address_change_form_response': address_change_form_response,
                         'order_body_response': order_body_response})
                else:
                    if request.user.is_authenticated:
                        with_save = "true"
                    else:
                        with_save = "false"

                    address_change_form_response = render_template('address_change.html',
                                                                   {'address_form': address_form,
                                                                    'with_save': with_save},
                                                                   request)
                    return JsonResponse(
                        {'address_change_form_response': address_change_form_response, 'result': 'error'})

            else:

                if request.user.is_authenticated:
                    with_save = "true"
                else:
                    with_save = "false"

                address_change_form_response = render_template('address_change.html',
                                                               {'address_form': address_form, 'with_save': with_save},
                                                               request)
                return JsonResponse({'address_change_form_response': address_change_form_response, 'result': 'error'})



        elif method == "order_confirm":
            address_form = AddressForm(request.GET)

            if address_form.is_valid():
                info = address_form.cleaned_data
                normalize = pr_address_normalize(info['country'], info['region'],
                                                 info['area'], info['city'],
                                                 info['street'], info['house'],
                                                 info['room'], info['index'])

                if normalize['ret_status'] == 'success':
                    delivery_total_ret = pr_pre_calc(normalize['body']['index'])
                    delivery_total = delivery_total_ret['total_nds']

                    cart = getUserCart(request)

                    if cart.items.count() == 0:
                        return JsonResponse({'result': 'error'})

                    order = Order()
                    order.save()

                    address_form = AddressForm(request.GET, instance=order)
                    if not address_form.is_valid():
                        return JsonResponse({'result': 'error'})

                    address_form.save()

                    order.order_from_cart(cart)

                    order.delivery_price = delivery_total

                    sale_code = request.GET.get('sale_code')


                    try:
                        sale = ProductSale.objects.get(promo=sale_code)
                        val = order.price_all * Decimal(sale.sale) / 100
                        order.delivery_cart_price = delivery_total + order.price_all - val

                        if sale.promo == 'delivery':
                            order.delivery_cart_price = order.price_all

                        order.sale = sale.sale
                        order.promo = sale.promo

                    except:
                        order.delivery_cart_price = delivery_total + order.price_all

                    order.save()

                    cart.remove_all_from_cart(delete=False)

                    if request.user.is_authenticated == False:
                        from_ = str(request.session.session_key)
                        order.sk = from_
                        order.save()
                        user_id = order.sk
                    else:
                        user_id = order.user.id
                        from_ = str(order.user.id)

                    responce = register_pay(request, order.id, order.delivery_cart_price, user_id, order.name,
                                            order.email, order.phone)

                    if responce['ret_status'] == 'success':

                        order.status = 'registered'
                        order.archive()
                        order.save()

                        return JsonResponse(
                            {'result': 'success',
                             'url': responce['redirect_url'] + "?session=" + responce['session']})
                    else:
                        cart.cart_from_order(order)
                        order.delete()
                        return JsonResponse({'result': 'error', 'message_act': 'true',
                                             'message': message('Произошла ошибка, попробуйте еще раз!', request), })
                else:
                    return JsonResponse({'result': 'error'})
            else:
                return JsonResponse({'result': 'error'})



        elif method == "calc":
            address_form = AddressForm(request.GET)
            info = address_form.data
            normalize = pr_address_normalize(info['country'], info['region'],
                                             info['area'], info['city'],
                                             info['street'], info['house'],
                                             info['room'], info['index'])

            if normalize['ret_status'] == 'success':

                delivery_total_ret = pr_pre_calc(normalize['body']['index'])

                delivery_total = delivery_total_ret['total_nds']

                return JsonResponse({'result': 'success', "delivery_total": delivery_total})
            else:
                return JsonResponse({'result': 'error', "delivery_total": "0"})

        elif method == "check_sale":
            sale_code = request.GET.get('sale_code')

            try:
                sale = ProductSale.objects.get(promo=sale_code)
                return JsonResponse({'result': 'success', "sale": str(sale.sale)})
            except:
                return JsonResponse({'result': 'error', "sale": "0"})
