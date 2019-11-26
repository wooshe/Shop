from __future__ import unicode_literals

from urllib.parse import urlparse

from bootstrap4.renderers import FormRenderer
from bootstrap4.utils import render_template_file
from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.db.models import Max, Min
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

from order.models import Cart
from shop.models import Category, Product
from shopadmin.forms import NotificationForm
from user.forms import LoginForm, RegistrationForm, PasswordResetForm

def get_permission(request):
    user = request.user

    if user.is_superuser:
        return True
    else:
        raise PermissionDenied()
        return False

def getCart(request):
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        cart.sk = str(request.session.session_key)
        cart.save()
    except:
        cart = Cart()
        cart.sk = str(request.session.session_key)
        cart.save()
        request.session['cart_id'] = cart.id
    return cart


def getUserCart(request):
    user = request.user
    if user.is_authenticated:
        if user.cart.items.count() == 0:
            try:
                cart_id = request.session['cart_id']
                temp_cart = Cart.objects.get(id=cart_id)
                cart = user.cart
                cart.price_all = temp_cart.price_all
                for item in temp_cart.items.all():
                    cart.items.add(item)
                cart.save()
            except:
                cart = user.cart
        else:
            cart = user.cart
    else:
        cart = getCart(request)
    return cart


def getUserCartCount(request):
    cart = getUserCart(request)
    return cart.items.count()


def getDataForNavBaR(ctx, request):
    cart_count = getUserCartCount(request)

    login_form = LoginForm()
    registration_form = RegistrationForm()
    password_reset_form = PasswordResetForm()

    notification_form = NotificationForm()
    category_menu = Category.objects.all()

    ctx.update({
        'cart_count': cart_count, 'login_form': login_form,
        'registration_form': registration_form, 'password_reset_form': password_reset_form,
        'notification_form': notification_form, 'category_menu': category_menu,
    })


def render_template(template_name, ctx, request):
    t = loader.get_template(template_name)
    return t.render(ctx, request=request)


def message(text, request):
    return render_to_string('message.html', {'message_text': text})


def global_search_view(request):
    if request.method == 'GET':
        result = {}
        query = request.GET.get('query')

        main_page = urlparse(request.META.get('HTTP_REFERER')).path

        if main_page == '/main/':
            redirect = "False"
            url = ''
        else:
            redirect = "True"
            url = reverse('main')

        products_of_category = Product.objects.all()

        result['redirect'] = redirect
        result['url'] = url

        return JsonResponse({'result': result})


def sorter(product, sort_type, sort_value):
    if sort_type == "sort_by_price":
        if sort_value == "sort_from_max":
            product = product.order_by('-price')
        elif sort_value == "sort_from_zero":
            product = product.order_by('price')

    elif sort_type == "sort_by_pop":
        if sort_value == "sort_from_max":
            product = product.order_by('-count_buy')
        elif sort_value == "sort_from_zero":
            product = product.order_by('count_buy')

    elif sort_type == "sort_by_rating":
        if sort_value == "sort_from_max":
            product = product.order_by('-rating')
        elif sort_value == "sort_from_zero":
            product = product.order_by('rating')

    return product


def range_filter(product, price_from, price_to):
    product = product.filter(Q(price__gte=price_from) & Q(price__lte=price_to))
    return product


def get_min_max(product, context):
    if product.count() == 0:
        context.update({"min_price": "0", "max_price": "0"})
        return

    min_price = product.aggregate(Min('price'))
    max_price = product.aggregate(Max('price'))

    min_price = str(min_price.get('price__min'))
    max_price = str(max_price.get('price__max'))

    context.update({"min_price": min_price, "max_price": max_price})


def get_min_max_safe(product, context, from_price, to_price):
    min_price = product.aggregate(Min('price'))
    max_price = product.aggregate(Max('price'))

    min_price = str(min_price.get('price__min'))
    max_price = str(max_price.get('price__max'))

    context.update({"min_price": min_price, "max_price": max_price, "from_price": from_price, "to_price": to_price})


def shop_search_view(request):
    if request.method == 'GET':

        response = {}
        response['pagination_end'] = 'False'

        res = []
        category_select_id = request.GET.get('category_select_id')
        sort_type = request.GET.get('sort_type')
        sort_value = request.GET.get('sort_value')
        price_from = request.GET.get('price_from')
        price_to = request.GET.get('price_to')
        event = request.GET.get('event')
        query = request.GET.get('query')
        page = request.GET.get('page')

        l = 0
        h = settings.PAGINATION_ELEMENT

        print(query, category_select_id, sort_type, sort_value, price_from, price_to, event)

        if event == "shop_search":
            result = {}
            products_of_category = Product.objects.annotate(search=SearchVector('name', 'description')).filter(
                search=query)
            price = get_min_max(products_of_category, response)

            products_of_category = sorter(products_of_category, sort_type, sort_value)

            if products_of_category.count() == 0:
                t = loader.get_template('not_find.html')
                response["min_price"] = "0"
                response["max_price"] = "0"
            else:
                t = loader.get_template('shop_products.html')

        elif event == "category_change":
            if category_select_id == "all":
                products_of_category = Product.objects.all()
            elif category_select_id == "sale":
                products_of_category = Product.objects.all().filter(sale__gt=0)
            else:
                cat = Category.objects.get(id=category_select_id).get_descendants(include_self=True)
                products_of_category = Product.objects.filter(category__in=cat)

            price = get_min_max(products_of_category, response)

            products_of_category = sorter(products_of_category, sort_type, sort_value)

            if products_of_category.count() == 0:
                t = loader.get_template('not_find.html')
                response["min_price"] = "0"
                response["max_price"] = "0"
            else:
                t = loader.get_template('shop_products.html')

        elif event == "sort_change":

            if category_select_id == None:
                result = {}
                products_of_category = Product.objects.annotate(search=SearchVector('name', 'description')).filter(
                    search=query)
            else:
                if category_select_id == "all":
                    products_of_category = Product.objects.all()
                elif category_select_id == "sale":
                    products_of_category = Product.objects.all().filter(sale__gt=0)
                else:
                    cat = Category.objects.get(id=category_select_id).get_descendants(include_self=True)
                    products_of_category = Product.objects.filter(category__in=cat)

            price = get_min_max(products_of_category, response)
            products_of_category = sorter(products_of_category, sort_type, sort_value)

            if products_of_category.count() == 0:
                t = loader.get_template('not_find.html')
                response["min_price"] = "0"
                response["max_price"] = "0"
            else:
                t = loader.get_template('shop_products.html')


        elif event == "range_change":
            if category_select_id == None:
                result = {}
                products_of_category = Product.objects.annotate(search=SearchVector('name', 'description')).filter(
                    search=query)
            else:
                if category_select_id == "all":
                    products_of_category = Product.objects.all()
                elif category_select_id == "sale":
                    products_of_category = Product.objects.all().filter(sale__gt=0)
                else:
                    cat = Category.objects.get(id=category_select_id).get_descendants(include_self=True)
                    products_of_category = Product.objects.filter(category__in=cat)

            price = get_min_max_safe(products_of_category, response, price_from, price_to)
            products_of_category = sorter(products_of_category, sort_type, sort_value)
            products_of_category = products_of_category.filter(Q(price__gte=price_from) & Q(price__lte=price_to))

            if products_of_category.count() == 0:
                t = loader.get_template('not_find.html')
            else:
                t = loader.get_template('shop_products.html')


        elif event == "pagination":

            l = (int(page) - 1) * settings.PAGINATION_ELEMENT
            h = l + settings.PAGINATION_ELEMENT

            if category_select_id == None:
                result = {}
                products_of_category = Product.objects.annotate(search=SearchVector('name', 'description')).filter(
                    search=query)
            else:
                if category_select_id == "all":
                    products_of_category = Product.objects.all()
                elif category_select_id == "sale":
                    products_of_category = Product.objects.all().filter(sale__gt=0)
                else:
                    cat = Category.objects.get(id=category_select_id).get_descendants(include_self=True)
                    products_of_category = Product.objects.filter(category__in=cat)

            price = get_min_max_safe(products_of_category, response, price_from, price_to)
            products_of_category = sorter(products_of_category, sort_type, sort_value)
            products_of_category = products_of_category.filter(Q(price__gte=price_from) & Q(price__lte=price_to))

            t = loader.get_template('shop_products.html')

        products_of_category = products_of_category[l:h]

        if products_of_category.count() < 20:
            response['pagination_end'] = 'True'

        try:
            user_favorite_product = request.user.profile.favorite_product.all()
        except:
            user_favorite_product = None

        ctx = {'request': request, 'user_favorite_product': user_favorite_product, 'products': products_of_category}
        responset = t.render(ctx)
        response["product_model"] = responset
        response["event"] = event
        response["page"] = page

        return JsonResponse(response)


def favorite_product_add_remove_view(request):
    if request.method == 'GET':
        product_id = request.GET.get('product_id')
        method = request.GET.get('method')
        product = Product.objects.get(id=product_id)
        user = request.user
        if method == 'add':
            if product not in user.profile.favorite_products.all():
                user.profile.favorite_products.add(product)
            else:
                method = 'nothing'
        elif method == 'remove':
            if product in user.profile.favorite_products.all():
                user.profile.favorite_products.remove(product)
            else:
                method = 'nothing'
        return JsonResponse({'product_id': product_id, 'method': method})


def likely_product_add_remove_view(request):
    if request.method == 'GET':
        product_id = request.GET.get('product_id')
        method = request.GET.get('method')
        product = Product.objects.get(id=product_id)
        user = request.user
        if method == 'add':
            if product not in user.profile.likely_products.all():
                user.profile.likely_products.add(product)
                product.add_like()
            else:
                method = 'nothing'
        elif method == 'remove':
            if product in user.profile.likely_products.all():
                user.profile.likely_products.remove(product)
                product.dislike()
            else:
                method = 'nothing'
        return JsonResponse({'product_id': product_id, 'method': method, 'like': product.like})


def product_set_rating_view(request):
    if request.method == 'GET':
        value = request.GET.get('value')
        product_id = request.GET.get('product_id')
        product = Product.objects.get(id=product_id)
        product.set_rating(value)

        user = request.user

        if product not in user.profile.rating_products.all():
            user.profile.rating_products.add(product)
            product.set_rating(value)

        response = {"rating": product.rating, }

        return JsonResponse(response)


def send_html_email(request, template, subject, email, context):

    try:
        if request == None:
            site_name = "bonafidesale.ru"
            domain = "bonafidesale.ru"
        else:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain

        context.update({"site_name": site_name, "domain": domain})

        html_content = render_to_string(template, context)  # render with dynamic value
        text_content = strip_tags(html_content)  # Strip the html tag. So people can see the pure text at least.

        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except:
        return


def permission_view(request):
    context = {}
    getDataForNavBaR(context, request)
    return render(request, 'permission.html', context)


def render_errors(self, type="all"):
    form_errors = None
    if type == "all":
        form_errors = self.get_fields_errors() + self.form.non_field_errors()
    elif type == "fields":
        form_errors = self.get_fields_errors()
    elif type == "non_fields":
        form_errors = self.form.non_field_errors()

    if self.required_css_class != 'not_message':
        if form_errors:
            return render_template_file(
                "bootstrap4/form_errors.html",
                context={
                    "errors": form_errors,
                    "form": self.form,
                    "layout": self.layout,
                    "type": type,
                },
            )

    return ""


FormRenderer.render_errors = render_errors
