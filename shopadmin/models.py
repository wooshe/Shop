# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save,post_save
from django.utils.text import slugify
from django.urls import reverse
from transliterate import translit
from decimal import Decimal
from django import forms
from PIL import Image
import os
import glob

