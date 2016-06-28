from django.conf.urls import url, include
from django.contrib import admin
from models import *
from views import *

urlpatterns = [

    url(r'product/create/$', create_product, name='create_product'),
    url(r'product/list/$', list_product, name='list'),
    url(r'product/edit/(?P<id>[^/]+)/$', edit_product, name='edit'),
    url(r'product/view/(?P<id>[^/]+)/$', view_product, name='view'),
    url(r'store/$', store_view, name='store'),
    url(r'cart/view/', view_cart, name='cart'),
    url(r'cart/add/(?P<id>[^/]+)/$', add_to_cart, name='add'),
    url(r'cart/clean/', clean_cart, name='clean'),
    url(r'lineitems/(?P<id>[0-9]+)/$', lineitem_detail.as_view()),
    url(r'lineitems/$', lineitem_list.as_view()),
    url(r'order/create/$', create_order, name='create_order'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
