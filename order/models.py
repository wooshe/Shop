# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible

from shop.models import Product, ProductSize


@python_2_unicode_compatible
class Address(models.Model):
    name = models.CharField(max_length=120, verbose_name='Имя', null=True)
    surname = models.CharField(max_length=120, verbose_name='Фамилия', null=True)
    fathername = models.CharField(max_length=120, verbose_name='Отчество', null=True)
    phone = models.CharField(max_length=120, verbose_name='Телефон', null=True)
    email = models.EmailField(verbose_name='E-mail', null=True)
    country = models.CharField(max_length=120, verbose_name='Страна', default="Россия", null=True)
    region = models.CharField(max_length=120, verbose_name='Регион/Область', null=True)
    area = models.CharField(max_length=120, verbose_name='Район', null=True, blank=True)
    city = models.CharField(max_length=120, verbose_name='Город/Населенный пункт', null=True)
    street = models.CharField(max_length=120, verbose_name='Улица', null=True)
    house = models.CharField(max_length=120, verbose_name='Дом', null=True)
    room = models.CharField(max_length=120, verbose_name='Квартира', null=True, blank=True)
    index = models.CharField(max_length=120, verbose_name='Индекс', null=True)

    class Meta:
        abstract = True


ORDER_STATUS_CHOICES = (
    ('new', 'Новый, ожидается регистрация'),
    ('registered', 'Ожидается оплата'),
    ('ready_to_send', 'Готов к отправке'),
    ('sender', 'Отправлено'),
    ('finish', 'Завершен')
)


@python_2_unicode_compatible
class Order(Address):
    items = models.ManyToManyField('CartItem', blank=True, related_name='order', verbose_name="Товары в заказе")
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='order',
                             verbose_name="Пользователь")
    status = models.CharField(max_length=100, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_CHOICES[0][0],
                              verbose_name="Статус заказа")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    sk = models.TextField(verbose_name="Корзина гостя", blank=True)
    pay = models.BooleanField(default=False, verbose_name="Оплачено")

    send_confirm = models.BooleanField(default=False, verbose_name="Подтверждена доставка")

    pr_batch_name = models.TextField(max_length=100, verbose_name="Имя отправления", blank=True)
    pr_id = models.TextField(max_length=100, verbose_name="Номер отправления", blank=True)
    pr_barcode = models.TextField(max_length=100, verbose_name="Трек-номер", blank=True)
    pr_doc = models.BooleanField(default=False, verbose_name="Отправлено в ОПС")

    price_all = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name="Стоимость товаров")
    delivery_price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00,
                                         verbose_name="Стоимость доставки")
    delivery_cart_price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name="Итого")

    promo = models.CharField(max_length=100, verbose_name='Промокод', blank=True)
    sale = models.PositiveIntegerField(default=0, verbose_name='Скидка', blank=True)

    def archive(self):
        for it in self.items.all():
            it.archive_product_url = it.product.get_absolute_url()
            it.archive_product_name = it.product.name
            it.archive_product_id = it.product.id
            it.archive_product_base_price = it.product.base_price
            it.archive_product_sale = it.product.sale
            it.archive_product_price = it.product.price
            it.archive_size = it.size.size
            it.archive_count = it.count
            it.archive_price_all = it.price_all
            it.save()

    def group_name(self):
        return "user" + str(self.user.id) + "andshop_bonafidesale"

    def order_from_cart(self, cart):
        self.items.set(cart.items.all())
        self.user = cart.user
        self.CalculatePrice()

    def incr_buy_for_items(self):
        for item in self.items.all():
            item.product.incr_buy()

    def CalculatePrice(self):
        self.price_all = 0
        for item in self.items.all():
            self.price_all += item.CalculatePrice()
        self.save()

    def __str__(self):
        return str(self.id)


@python_2_unicode_compatible
class Cart(models.Model):
    items = models.ManyToManyField('CartItem', blank=True, related_name='cart', verbose_name="Товары в корзине")
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Пользователь")
    price_all = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name="Итого")
    sk = models.TextField(verbose_name="Корзина гостя", blank=True)

    def cart_from_order(self, order):
        self.items.set(order.items.all())
        self.user = order.user
        self.CalculatePrice()

    def __str__(self):
        try:
            ret = str(self.id) + " " + self.user.username
        except:
            ret = 'Не зарегистрированный'
        return ret

    def CalculatePrice(self):
        self.price_all = 0
        for item in self.items.all():
            self.price_all += item.CalculatePrice()
        self.save()
        return self.price_all

    def add_to_cart(self, product_id, size_id):

        product = Product.objects.get(id=product_id)
        size = ProductSize.objects.get(id=size_id)

        try:
            current_cart_item = self.items.get(Q(product=product) & Q(size_id=size_id))
            if current_cart_item.size != size:
                raise NameError('Not Item')

            if current_cart_item.count < size.count:
                current_cart_item.count += 1
            current_cart_item.CalculatePrice()
        except:
            new_cart_item = CartItem()
            new_cart_item.product = product
            new_cart_item.size = size
            new_cart_item.count = 1
            new_cart_item.CalculatePrice()
            self.items.add(new_cart_item)
        self.CalculatePrice()

        return "success"

    def change_item_count(self, item_id, size_id, count, ):

        cart_item = self.items.get(Q(id=int(item_id)) & Q(size_id=int(size_id)))
        cart_item.count = count
        cart_item.CalculatePrice()
        cart_item.save()
        self.CalculatePrice()
        return cart_item

    def remove_from_cart(self, product_id, size_id):

        product = Product.objects.get(id=product_id)
        cart_item = self.items.get(Q(product=product) & Q(size_id=size_id))
        self.items.remove(cart_item)
        cart_item.delete()
        self.CalculatePrice()

    def remove_all_from_cart(self, delete=True):

        for item in self.items.all():
            self.items.remove(item)
            if delete == True:
                item.delete()
        self.CalculatePrice()
        self.save()


@receiver(post_save, sender=User)
def create_or_update_user_cart(sender, instance, created, **kwargs):
    try:
        if created:
            Cart.objects.create(user=instance)
        instance.cart.save()
    except:
        return


@python_2_unicode_compatible
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Товар')
    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Размер')
    count = models.PositiveIntegerField(default=0, verbose_name='Кол-во')
    price_all = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Сумма')
    archive_product_url = models.SlugField(blank=True, max_length=120)
    archive_product_name = models.CharField(max_length=120, verbose_name='архив_Наименование', blank=True)
    archive_product_id = models.PositiveIntegerField(default=0, verbose_name='архив_ID', blank=True)

    archive_product_base_price = models.DecimalField(max_digits=9, decimal_places=2, default=0,
                                                     verbose_name='архив_Цена',
                                                     blank=True)
    archive_product_sale = models.PositiveIntegerField(default=0, verbose_name='архив_Скидка', blank=True)
    archive_product_price = models.DecimalField(max_digits=9, decimal_places=2, default=0,
                                                verbose_name='архив_Сумма со скидкой', blank=True)

    archive_size = models.CharField(max_length=100, verbose_name='архив_Размер', blank=True)
    archive_count = models.PositiveIntegerField(default=0, verbose_name='архив_Кол-во', blank=True)
    archive_price_all = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='архив_Сумма',
                                            blank=True)

    def CalculatePrice(self):
        self.price_all = self.product.price * int(self.count)
        self.save()
        return self.price_all

    def __str__(self):
        return "Элемент корзины для товара {0}".format(self.product.name)
