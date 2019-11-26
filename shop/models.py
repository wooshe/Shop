# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from decimal import Decimal

from PIL import Image
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from shop.utils import create_slug, product_photo, category_photo


class RatingLike(models.Model):
    like = models.PositiveIntegerField(default=0, verbose_name='Количество лайков')

    rating = models.DecimalField(max_digits=16, decimal_places=1, default=5.0, verbose_name='Рейтинг')
    rating_count = models.PositiveIntegerField(default=1, verbose_name='Количество пользователей выбравших рейтинг')
    rating_sum = models.PositiveIntegerField(default=5, verbose_name='Сумма рейтинга')

    class Meta:
        abstract = True

    def add_like(self):
        self.like += 1
        self.save()
        return self.like

    def dislike(self):
        self.like -= 1
        self.save()
        return self.like

    def set_rating(self, value):
        self.rating_count += 1
        self.rating_sum += int(value)
        self.rating = self.rating_sum / self.rating_count
        self.save()
        return self.rating


@python_2_unicode_compatible
class ProductSale(models.Model):

    promo = models.CharField(max_length=100, verbose_name='Промокод')
    sale = models.PositiveIntegerField(default=0, verbose_name='Скидка')

    def __str__(self):
        return "Промокод " + str(self.sale) + " %"


@python_2_unicode_compatible
class ProductComment(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_comment',
                                verbose_name="Продукт")
    comment = models.TextField(max_length=1000, verbose_name='Комментарий')
    author = models.CharField(max_length=100, verbose_name='Автор', default='Пользователь')

    def __str__(self):
        return "Комментарий продукта " + self.product.name


# @python_2_unicode_compatible
# class ShopPhoto(models.Model):
#     author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shop_photo', verbose_name="Автор")
#     shop = models.ForeignKey('Shop', on_delete=models.CASCADE, related_name='shop_photo', verbose_name="Магазин")
#     image = models.ImageField(upload_to=shop_photo, verbose_name='Изображения', blank=True,
#                               default='default/photo_mag.jpg')
#
#     def save(self, *args, **kwargs):
#         if self.pk is None:
#             saved_image = self.image
#             self.image = None
#             super(ShopPhoto, self).save(*args, **kwargs)
#             self.image = saved_image
#
#         super(ShopPhoto, self).save(*args, **kwargs)
#
#     def __str__(self):
#         return "Фотографии магазина " + self.shop.name
#
#
# @receiver(pre_delete, sender=ShopPhoto)
# def shop_photo_delete(sender, instance, **kwargs):
#     if instance.image.url != '/media/default/photo_mag.jpg':
#         instance.image.delete()
#
#
# @python_2_unicode_compatible
# class Shop(RatingLike):
#     author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shop', verbose_name="Автор")
#     name = models.CharField(max_length=120, verbose_name='Название')
#     slug = models.SlugField(blank=True)
#     description = models.TextField(verbose_name='Описание')
#     main_photo = models.ImageField(upload_to=shop_main_photo, verbose_name='Главное изображение', blank=True,
#                                    default='default/photo_mag.jpg')
#
#     def save(self, *args, **kwargs):
#         if self.pk is None:
#             saved_image = self.main_photo
#             self.main_photo = None
#             super(Shop, self).save(*args, **kwargs)
#             self.main_photo = saved_image
#
#         self.slug = create_slug(self.name, self.id)
#         super(Shop, self).save(*args, **kwargs)
#
#     def __str__(self):
#         return self.name
#
#     def get_absolute_url(self):
#         return reverse('shop', kwargs={'shop_slug': self.slug})
#
#
# @receiver(pre_delete, sender=Shop)
# def shop_delete(sender, instance, **kwargs):
#     if instance.main_photo.url != '/media/default/photo_mag.jpg':
#         instance.main_photo.delete()


@python_2_unicode_compatible
class ProductPhoto(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_photo', verbose_name="Автор")
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_photo', verbose_name="Товар")
    image = models.ImageField(upload_to=product_photo, verbose_name='Изображение', blank=True,
                              default='default/photo_product.jpg', max_length=500)

    def get_pre_photo(self):
        result = os.path.dirname(self.image.url) + '/pre_' + os.path.basename(self.image.url)
        return result

    def save(self, *args, **kwargs):
        if self.pk is None:
            saved_image = self.image
            self.image = None
            super(ProductPhoto, self).save(*args, **kwargs)
            self.image = saved_image

        super(ProductPhoto, self).save(*args, **kwargs)

        im = Image.open(self.image)
        size = int(im.width * 0.5), int(im.height * 0.5)
        im.thumbnail(size)
        im.save(os.path.dirname(self.image.path) + '/pre_' + os.path.basename(self.image.path))

    def __str__(self):
        return "Фотографии " + self.product.name


@receiver(pre_delete, sender=ProductPhoto)
def product_photo_delete(sender, instance, **kwargs):
    try:
        if instance.image.url != '/media/default/photo_product.jpg':
            instance.image.delete()
    except:
        pass


SIZE_CHOICES = (
    ('Без размера', 'Без размера'),
    ('XXXL', 'XXXL'),
    ('XXL', 'XXL'),
    ('Xl', 'Xl'),

    ('L', 'L'),
    ('M', 'M'),
    ('S', 'S'),

    ('XS', 'XS'),
    ('XXS', 'XXS'),
    ('XXXS', 'XXXS'),
)


@python_2_unicode_compatible
class ProductSize(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='size')
    size = models.CharField(max_length=100, choices=SIZE_CHOICES, verbose_name='Размер')
    count = models.PositiveIntegerField(default=0, verbose_name='Кол-во')

    def __str__(self):
        return "Размер " + self.product.name

    def __init__(self, *args, **kwargs):
        super(ProductSize, self).__init__(*args, **kwargs)
        self.__last_count = self.count

    def get(self, request, *args, **kwargs):
        self.requset = request

    def save(self, *args, **kwargs):
        if self.__last_count == 0 and self.count > 0:
            notification = self.notification.all()
            for notify in notification:
                if notify.email != None:

                    from main.utils import send_html_email
                    send_html_email(None, 'notify_size_email.html', "Товар появился в продаже", notify.email,
                                    {"notify": notify, 'size':self.size})

                    notify.delete()

            notification = self.product.notification.all()
            for notify in notification:
                if notify.email != None:

                    from main.utils import send_html_email
                    send_html_email(None, 'notify_product_email.html', "Товар появился в продаже", notify.email,
                                    {"notify": notify})

                    notify.delete()



        super(ProductSize,self).save(*args, **kwargs)


@python_2_unicode_compatible
class Notification(models.Model):
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, related_name='notification', blank=True, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='notification', blank=True,
                                     null=True)
    product_notify = models.BooleanField(default=True, blank=True, verbose_name='Оповещение о продукте')
    email = models.EmailField(verbose_name='E-mail', null=True, blank=True)
    sk = models.TextField(verbose_name="Гость", blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='notification',
                             verbose_name="Пользователь")

    def __str__(self):
        if self.product_notify == True:
            return "Уведомление о товаре: " + self.product.name
        else:
            return "Уведомление о товаре: " + self.product_size.product.name + ' Размер: ' + self.product_size.size



class Available(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)

class Archive(models.Manager):
    def get_queryset(self):
        return super().get_queryset().all()

@python_2_unicode_compatible
class Product(RatingLike):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product', verbose_name="Автор")
    category = TreeForeignKey('Category', on_delete=models.CASCADE, verbose_name='Категория', related_name='category')
    slug = models.SlugField(blank=True, max_length=120)
    name = models.CharField(max_length=120, verbose_name='Наименование')
    description = models.TextField(blank=True, max_length=2000, verbose_name='Описание')

    image_default = models.ImageField(verbose_name='Изображение по умолчанию', blank=True,
                                      default='default/photo_product.jpg', max_length=500)

    model = models.CharField(blank=True, max_length=100, verbose_name='Модель')
    material = models.CharField(blank=True, max_length=100, verbose_name='Материал')
    color = models.CharField(blank=True, max_length=100, verbose_name='Цвет')

    base_price = models.DecimalField(max_digits=9, decimal_places=2, default=100, verbose_name='Цена')
    sale = models.PositiveIntegerField(default=0, verbose_name='Скидка', blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, default=100, verbose_name='Сумма со скидкой')

    objects = Available()
    archive = Archive()

    count_buy = models.PositiveIntegerField(default=0, verbose_name='Число продаж')
    count_view = models.PositiveIntegerField(default=0, verbose_name='Число просмотров')

    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    with_size = models.BooleanField(default=False, blank=True, verbose_name='Есть размер')


    def save(self, *args, **kwargs):
        if self.pk is None:
            super(Product, self).save(*args, **kwargs)

        delta = self.base_price * (self.sale /Decimal(100))
        self.price = self.base_price - delta
        self.slug = create_slug(self.name, self.id)



        super(Product, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.save()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product', kwargs={'product_slug': self.slug})

    def incr_buy (self):
        self.count_buy = self.count_buy + 1
        self.save()

    def incr_view(self):
        self.count_view = self.count_view + 1
        self.save()

@python_2_unicode_compatible
class Category(MPTTModel):
    title = models.CharField(max_length=120, verbose_name='Название')
    slug = models.SlugField(blank=True, max_length=120)
    image = models.ImageField(upload_to=category_photo, verbose_name='Изображение', blank=True,
                              default='default/photo_product.jpg', max_length=500)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Автор", related_name='category')
    parent = TreeForeignKey('Category', on_delete=models.CASCADE, null=True, verbose_name="Родительская категория",
                            blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['id']

    def save(self, *args, **kwargs):
        if self.pk is None:
            super(Category, self).save(*args, **kwargs)

        self.slug = create_slug(self.title, self.id)
        with Category.objects.disable_mptt_updates():
            super(Category, self).save(*args, **kwargs)
        Category.objects.rebuild()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('catalog', kwargs={'category': self.slug})
