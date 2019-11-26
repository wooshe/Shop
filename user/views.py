# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urllib

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from main.utils import getDataForNavBaR, message, render_template, send_html_email
from order.models import Order
from order.payment import status_pay
from order.pochta import *
from user.forms import UserForm, AddressForm, PasswordChangeForm


def custom_redirect(url_name, *args, **kwargs):
    url = reverse(url_name, args=args)
    params = urllib.parse.urlencode(kwargs)
    return HttpResponseRedirect(url + "?%s" % params)


def notify_admin(request, order):
    if request.user.is_authenticated == False:
        from_ = str(request.session.session_key)
    else:
        from_ = str(order.user.id)

    channel_layer = get_channel_layer()

    ret_get_order = pr_get_order(order.id)

    email_send_status = False

    if ret_get_order['ret_status'] == 'error':

        retunrn_order = pr_order(order)

        if retunrn_order['ret_status'] == "success":
            ids = retunrn_order['result-ids']

            ret_get_shipment = pr_get_shipment(order.id)

            if ret_get_shipment['ret_status'] == 'error':
                ret_shipment = pr_shipment(ids)

                if ret_shipment['ret_status'] == "success":
                    result_ret_get_shipment = pr_get_shipment(order.id)

                    if result_ret_get_shipment['ret_status'] == "success":

                        order.pr_batch_name = result_ret_get_shipment['batch-name']
                        order.pr_barcode = result_ret_get_shipment['barcode']
                        order.pr_id = result_ret_get_shipment['id']
                        order.save()

                        ret_send = pr_send_doc(order.pr_batch_name)

                        if ret_send['ret_status'] == "success":
                            order.pr_doc = True
                            order.save()

                        send_html_email(request, 'buy_email.html', "Заказ №" + str(order.id), order.email,
                                        {'order': order})
                        email_send_status = True

    if email_send_status == False:
        send_html_email(request, 'buy_email.html', "Заказ №" + str(order.id), order.email, {'order': order})

    async_to_sync(channel_layer.group_send) \
        ("shopmain",
         {"type": "receive_json", "sender": "user", "command": "alarm",
          "order_id": str(order.id), "to": "shopmain", "from": from_,
          "event": "new_item"})


def order_update(request):
    if request.user.is_authenticated:
        not_pay_order = Order.objects.filter(Q(user=request.user) & Q(pay=False))
    else:
        not_pay_order = Order.objects.filter(Q(sk=request.session.session_key) & Q(pay=False))

    for order in not_pay_order:
        response = status_pay(order.id)
        if response['ret_status'] != 'error':
            if order.pay == False and (response['status'] == 'authorized' or response[
                'status'] == 'acknowledged') and order.status == 'registered':
                order.pay = True
                order.incr_buy_for_items()
                order.status = 'ready_to_send'
                order.save()
                notify_admin(request, order)


def profile_view(request):
    user = request.user

    if not user.is_authenticated:
        return custom_redirect('anonymous_profile', order_id=request.GET.get('order_id'),
                               success_pay=request.GET.get('success_pay'))

    if request.method == 'GET':

        if request.GET.get('method') == 'get_order':
            try:
                order = Order.objects.get(id=request.GET.get('order_id'))
                order_response = render_template('order_expand.html', {'order': order}, request)
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

        context = {}
        context['message_act'] = 'false'
        context['success_pay'] = 'False'

        order_id = request.GET.get('order_id')

        if str(order_id) != 'None' and str(request.GET.get('success_pay')) == 'None':

            context['order_id'] = order_id

            user_form = UserForm(instance=request.user)
            address_form = AddressForm(instance=request.user.profile)
            password_change_form = PasswordChangeForm()

            response = status_pay(order_id)

            url = reverse('profile')
            if response['ret_status'] != 'error':
                if response['status'] == 'authorized' or response['status'] == 'acknowledged':
                    url += '?success_pay=True&order_id=' + order_id
                    context['success_pay'] = 'True'

            context.update({
                'redirect_url': url,
                'user_form': user_form, 'address_form': address_form, 'with_save': "true",
                'password_change_form': password_change_form
            })

            getDataForNavBaR(context, request)
            return render(request, 'profile.html', context)

        elif str(order_id) != 'None' and str(request.GET.get('success_pay')) == 'True':
            pay_order = Order.objects.get(id=order_id)
            response = status_pay(pay_order.id)
            if response['ret_status'] != 'error':
                if pay_order.pay == False and (response['status'] == 'authorized' or response[
                    'status'] == 'acknowledged') and pay_order.status == 'registered':
                    pay_order.pay = True
                    pay_order.incr_buy_for_items()
                    pay_order.status = 'ready_to_send'
                    pay_order.save()
                    notify_admin(request, pay_order)
                    context['message_act'] = 'true'
                    context['message'] = message('Заказ совершен!', request)

        order_update(request)

        orders = Order.objects.filter(Q(user=user) & Q(pay=True))

        user_form = UserForm(instance=request.user)
        address_form = AddressForm(instance=request.user.profile)
        password_change_form = PasswordChangeForm()

        context.update({
            'orders': orders,
            'user_form': user_form, 'address_form': address_form, 'with_save': "true",
            'password_change_form': password_change_form
        })

        getDataForNavBaR(context, request)
        return render(request, 'profile.html', context)

    if request.method == 'POST':
        type_post = request.POST.get('type_post')

        if type_post == "user_form":

            user_form = UserForm(request.POST, instance=request.user)

            if user_form.is_valid():
                user_form.save()
                user_change_form_response = render_template('user_change.html',
                                                            {'user_form': user_form}, request)
                return JsonResponse({'user_change_form_response': user_change_form_response, 'result': 'success',
                                     'message': message("Профиль изменен!", request)})
            else:
                user_change_form_response = render_template('user_change.html',
                                                            {'user_form': user_form},
                                                            request)
                return JsonResponse({'user_change_form_response': user_change_form_response, 'result': 'error'})

        else:

            address_form = AddressForm(request.POST, instance=request.user.profile)

            if address_form.is_valid():
                address_form.save()

                address_change_form_response = render_template('address_change.html',
                                                               {'address_form': address_form, 'with_save': "true"},
                                                               request)
                return JsonResponse({'address_change_form_response': address_change_form_response, 'result': 'success',
                                     'message': message("Адрес изменен!", request)})
            else:
                address_change_form_response = render_template('address_change.html',
                                                               {'address_form': address_form, 'with_save': "true"},
                                                               request)
                return JsonResponse({'address_change_form_response': address_change_form_response, 'result': 'error'})


def anonymous_profile_view(request):
    user = request.user
    if user.is_authenticated:
        return custom_redirect('profile', order_id=request.GET.get('order_id'),
                               success_pay=request.GET.get('success_pay'))

    if request.method == 'GET':

        if request.GET.get('method') == 'get_order':
            try:
                order = Order.objects.get(id=request.GET.get('order_id'))
                order_response = render_template('order_expand.html', {'order': order}, request)
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

    context = {}
    context['message_act'] = 'false'
    context['success_pay'] = 'False'

    order_id = request.GET.get('order_id')

    if str(order_id) != 'None' and str(request.GET.get('success_pay')) == 'None':

        context['order_id'] = order_id
        response = status_pay(order_id)

        url = reverse('anonymous_profile')

        if response['ret_status'] != 'error':
            if response['status'] == 'authorized' or response['status'] == 'acknowledged':
                url += '?success_pay=True&order_id=' + order_id
                context['success_pay'] = 'True'

        context.update({
            'redirect_url': url,
        })

        getDataForNavBaR(context, request)
        return render(request, 'anonymous_profile.html', context)

    elif str(order_id) != 'None' and str(request.GET.get('success_pay')) == 'True':
        pay_order = Order.objects.get(id=order_id)
        response = status_pay(pay_order.id)
        if response['ret_status'] != 'error':
            if pay_order.pay == False and (response['status'] == 'authorized' or response[
                'status'] == 'acknowledged') and pay_order.status == 'registered':
                pay_order.pay = True
                pay_order.incr_buy_for_items()
                pay_order.status = 'ready_to_send'
                pay_order.save()
                notify_admin(request, pay_order)
                context['message_act'] = 'true'
                context['message'] = message('Заказ совершен!', request)

    context['success_pay'] = 'False'

    order_update(request)
    orders = Order.objects.filter(Q(sk=request.session.session_key) & Q(pay=True))

    context.update({
        'orders': orders,
    })

    getDataForNavBaR(context, request)
    return render(request, 'anonymous_profile.html', context)
