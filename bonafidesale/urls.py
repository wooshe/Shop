from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.utils.functional import curry
from django.views.defaults import permission_denied, page_not_found, server_error, bad_request

from main.utils import global_search_view, shop_search_view, product_set_rating_view, favorite_product_add_remove_view, \
    permission_view, likely_product_add_remove_view
from main.views import main_view, about_view, delivery_view, return_view, catalog_view, police_view, user_confirm_view, \
    oferta_view, back_view
from order.views import cart_view, add_to_cart_view, remove_from_cart_view, remove_all_from_cart_view, \
    change_item_count_view, to_order_view, create_notification_view
from shop.views import product_view, product_add_comment_view
from shopadmin.views import shopadmin_view, category_remove_view, category_add_view, category_edit_view, \
    product_edit_view, product_remove_view, product_add_view, product_photo_remove_view, sale_remove_view, sale_add_view
from tester.views import tester_view
from user.utils import password_change_view, password_reset_handler_view, password_reset_change_view, login_view, \
    registration_view
from user.views import profile_view, anonymous_profile_view

handler400 = 'main.views.handler400'
handler403 = 'main.views.handler403'
handler404 = 'main.views.handler404'
handler500 = 'main.views.handler500'

urlpatterns = [

    url(r'^admin/', admin.site.urls),

    url(r'^$', main_view, name='main'),

    url(r'^catalog/$', catalog_view, name='catalog'),
    url(r'^catalog/(?P<category>[-\w]+)/$', catalog_view, name='catalog'),

    url(r'^about/$', about_view, name='about'),
    url(r'^return/$', return_view, name='return'),
    url(r'^delivery/$', delivery_view, name='delivery'),
    url(r'^police/$', police_view, name='police'),
    url(r'^user_confirm/$', user_confirm_view, name='user_confirm'),
    url(r'^oferta/$', oferta_view, name='oferta'),

    url(r'^back/$', back_view, name='back'),

    url(r'^global_search/$', global_search_view, name='global_search'),
    url(r'^shop_search/$', shop_search_view, name='shop_search'),

    url(r'^all/(?P<product_slug>[-\w]+)/$', product_view, name='product'),

    url(r'^cart/$', cart_view, name='cart'),

    url(r'^to_order/$', to_order_view, name='to_order'),

    url(r'^add_to_cart/$', add_to_cart_view, name='add_to_cart'),

    url(r'^change_item_count/$', change_item_count_view, name='change_item_count'),
    url(r'^remove_from_cart/$', remove_from_cart_view, name='remove_from_cart'),
    url(r'^remove_all_from_cart/$', remove_all_from_cart_view, name='remove_all_from_cart'),

    url(r'^create_notification/$', create_notification_view, name='create_notification'),

    url(r'^product_set_rating/$', product_set_rating_view, name='product_set_rating'),
    url(r'^product_add_comment/$', product_add_comment_view, name='product_add_comment'),
    url(r'^likely_product_add_remove/$', likely_product_add_remove_view, name='likely_product_add_remove'),

    url(r'^favorite_product_add_remove/$', favorite_product_add_remove_view, name='favorite_product_add_remove'),

    url(r'^profile/$', profile_view, name='profile'),

    url(r'^anonymous_profile/$', anonymous_profile_view, name='anonymous_profile'),

    url(r'^shopadmin/$', shopadmin_view, name='shopadmin'),

    url(r'^sale_remove/$', sale_remove_view, name='sale_remove'),
    url(r'^sale_add/$', sale_add_view, name='sale_add'),

    url(r'^category_edit/$', category_edit_view, name='category_edit'),
    url(r'^category_remove/$', category_remove_view, name='category_remove'),
    url(r'^category_add/$', category_add_view, name='category_add'),

    url(r'^product_edit/$', product_edit_view, name='product_edit'),
    url(r'^product_remove/$', product_remove_view, name='product_remove'),
    url(r'^product_add/$', product_add_view, name='product_add'),
    url(r'^product_photo_remove/$', product_photo_remove_view, name='product_photo_remove'),

    url(r'^tester/$', tester_view, name='tester'),

    url(r'^password_change/$', password_change_view, name='password_change'),
    url(r'^password_reset_change/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$', password_reset_change_view.as_view(),
        name='password_reset_change'),
    url(r'^password_reset_handler/$', password_reset_handler_view, name='password_reset_handler'),
    url(r'^login/$', login_view, name='login'),
    url(r'^logout/$', LogoutView.as_view(next_page=reverse_lazy('main')), name='logout'),
    url(r'^registration/$', registration_view, name='registration'),

    url(r'^permission/$', permission_view, name='permission'),
    url(r'^', include('social_django.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
