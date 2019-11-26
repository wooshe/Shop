import os

from django.template import Library

register = Library()

@register.filter
def procent_off(price,sale):
    return round(price*100/(100-sale),2)


@register.filter
def get_pre_photo(url):

    result = os.path.dirname(url) + '/pre_' + os.path.basename(url)

    return result

@register.filter
def get_item(dictionary, key):
    try:
        ret = dictionary.get(key)
        return ret
    except:
        return


@register.filter
def get_items(dictionary, args):
    if args is None:
        return False
    arg_list = [arg.strip() for arg in args.split(',')]

    k1 = int(arg_list[0])
    k2 = int(arg_list[1])

    return dictionary[k1][k2]