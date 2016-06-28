from django.core.urlresolvers import reverse
#from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from models import *

class LineItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = LineItem
        field = ('product', 'unit_price', 'quantity', 'order')
    def update(self, instance, validated_data):
        instance.product = validated_data['product']
        instance.unit_price = validated_data['unit_price']
        instance.quantity = validated_data['quantity']
        instance.order = validated_data['order']

        instance.save()
        return instance

    def create(self, validated_data):
        return LineItem.objects.create(**validated_data)


class OrderSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Order
        field = ('name', 'address', 'email', 'owner')

#   def restore_object(self, attrs, instance=None):
#     if instance:
#          instance.name = attrs['name']
#          instance.address = attrs['address']
#          instance.email = attrs['email']
#          return instance
#      return Order(**attrs)

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.address = validated_data['address']
        instance.email = validated_data['email']
        instance.owner = validated_data['owner']
        instance.save()
        return instance

    def create(self, validated_data):
        return Order.objects.create(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = User
        field = ('id', 'username', 'order')


