# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible

from order.models import Address
from shop.models import Product


@python_2_unicode_compatible
class Profile(Address):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    social = models.BooleanField(default=False, verbose_name="Вход через соц.сеть")

    favorite_products = models.ManyToManyField(Product, related_name='favorite_products', blank=True,
                                              verbose_name="Избранные товары")

    rating_products = models.ManyToManyField(Product, related_name='rating_products', blank=True,
                                             verbose_name="Рейтинг товаров")

    likely_products = models.ManyToManyField(Product, related_name='likely_products', blank=True,
                                             verbose_name="Лайки товаров")


    def __str__(self):
        return "Профиль для " + self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    try:
        if created:
            Profile.objects.create(user=instance)
            instance.profile.social = instance.social_auth.exists()
            instance.profile.name = instance.first_name
            instance.profile.surname = instance.last_name
            instance.profile.email = instance.email
            instance.profile.save()
        return
    except:
        return
