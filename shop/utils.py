from uuid import uuid4

from django.utils.text import slugify
from transliterate import  translit

from bonafidesale import settings


def create_slug(field,id):
    try:
        slug = slugify(translit(field, reversed=True))
        result = slug + '-' + str(id)
    except:
        slug = slugify(field)
        result = slug + '-' + str(id)

    return result

def get_extension(full_current_path):
    return '.' + full_current_path.split('.')[1]


def handle_uploaded_file(f):
    path = settings.MEDIA_ROOT + '/shops/' + f.name
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path

def shop_main_photo(instance, filename):
    ext = get_extension(filename)
    fullpath = 'shops/'+ instance.slug+ '/main_photo/' + str(uuid4())+ ext
    return fullpath


def shop_photo(instance, filename):
    ext = get_extension(filename)
    fullpath = 'shop/'+'/shop_photo/' + str(uuid4())+ ext
    return fullpath

def product_photo(instance, filename):
    ext = get_extension(filename)
    fullpath = 'shop/'+'/'+instance.product.slug+'/'+ str(uuid4())+ ext
    return fullpath

def category_photo(instance, filename):
    ext = get_extension(filename)
    fullpath = 'category/'+'/'+instance.slug+'/'+ str(uuid4())+ ext
    return fullpath

