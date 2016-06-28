

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.core.paginator import Paginator
from django.template import RequestContext
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.transaction import on_commit
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from cartapp.serializers import LineItemSerializer, OrderSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
from cartapp.permission import *
from cartapp.serializers import OrderSerializer, UserSerializer
from django.contrib.auth.models import User
import datetime


from models import *
from forms import * 

# Create your views here.

def create_product(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = ProductForm()

    t = get_template('cartapp/create_product.html')
    c = RequestContext(request, locals())
    return HttpResponse(t.render(c))
    
@login_required
def list_product(request):
     
    list_items = Product.objects.all()
    paginator = Paginator(list_items, 10)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        list_items = paginator.page(page)
    except:
        list_items = paginator.page(paginator.num_pages)

    t = get_template('cartapp/list_product.html')
    c = RequestContext(request, locals())
    return HttpResponse(t.render(c))    

def view_product(request, id):
    product_instance = Product.objects.get(id = id)
    
    t = get_template('cartapp/view_product.html')
    c = RequestContext(request, locals())
    return HttpResponse(t.render(c))

def edit_product(request, id):

    product_instance = Product.objects.get(id=id)
    
    form = ProductForm(request.POST or None, instance = product_instance)

    if form.is_valid():
        form.save()

    t = get_template('cartapp/edit_product.html')
    c = RequestContext(request, locals())
    return HttpResponse(t.render(c))

def store_view(request):
    products = Product.objects.all()
    cart = request.session.get('cart', None)

    t = get_template('cartapp/store.html')
    c = RequestContext(request, locals())
    return HttpResponse(t.render(c))

def view_cart(request):
    cart = request.session.get('cart', False)
    t = get_template('cartapp/view_cart.html')

    if not cart:
        cart = Cart()
        request.session['cart'] = cart
    c = RequestContext(request, locals())
    return HttpResponse(t.render(c))

def add_to_cart(request, id):
    product = Product.objects.get(id=id)
    cart = request.session.get('cart',  False)
    if not cart:
        cart = Cart()
        request.session['cart'] = cart
    cart.add_product(product)
    request.session['cart'] = cart
    return view_cart(request)

def clean_cart(request):
    request.session['cart'] = Cart()
    return view_cart(request)

#@on_commit
def create_order(request):
    order_form = OrderForm(request.POST or None)
    if order_form.is_valid():
        order = order_form.save()
        for item in request.session['cart'].items:
            item.order = order
            item.save()
        clean_cart(request)
        return store_view(request)
    
    t = get_template('cartapp/create_order.html')
    c = RequestContext(request, locals())
    return HttpResponse(t.render(c))


class JSONResponse(StreamingHttpResponse):

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

class OrderList(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def pre_save(self, obj):
        obj.owner = self.request.user

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsReadOnly)

class OrderDetail(APIView):
    def get(self, request, id, format=None):
        b = Order.objects.get(id=id)
        ser=OrderSerializer(b)
        return Response(ser.data)

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

def line_list(request):
    if request.method=='GET':
        b = LineItem.objects.all()
        ser = LineItemSerializer(b)
        return JSONResponse(ser.data)

#@csrf_exempt
class lineitem_list(generics.ListCreateAPIView):
    queryset = LineItem.objects.all()
    serializer_class = LineItemSerializer
    
#@csrf_exempt
class lineitem_detail(APIView):
    def get(self, request, id, format=None):
        b = LineItem.objects.get(id=id)
        ser=LineItemSerializer(b)
        return Response(ser.data)

    """
    List all code snippets, or create a new Lineitem.
    """
'''
    if request.method == 'GET':
        lineitems = request.session['cart'].items
        #lineitems = LineItem.objects.all()
        print lineitems
        serializer = LineItemSerializer(lineitems, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        data = JSONParser.parse(request)
        print 'ccc'
        serializer = LineItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)




def lineitem_detail(request, pk):
    """
    Retrieve, update or delete a code Lineitem.
    """
    try:
        lineitem = LineItem.objects.get(pk=pk)
    except LineItem.DoesNotExist:
        return HttpResponse(status=404)
    
    if request.method == 'GET':
        serializer = LineItemSerializer(lineitem)
        return JSONResponse(serializer.data)
    
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = LineItemSerializer(snippet, data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data)
        return JSONResponse(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        lineitem.delete()
        return HttpResponse(status=204)
'''

#class RESTforCart():
#    def get(self, request,*args, **kwargs):
#       return request.session['cart'].items


def post(self, request, *args, **kwargs):
    
    
    print request.POST['product']
    product = Product.objects.get(id=request.POST['product'])
    cart = request.session['cart']
    cart.add_product(product)
    request.session['cart'] = cart
    return request.session['cart'].items

def login_view(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        login(request, user)
        print request.user
        return list_product(request)
    else:
        return store_view(request)

def logout_view(request):
    logout(request)
    return store_view(request)

