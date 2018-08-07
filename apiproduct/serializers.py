from django.contrib.auth.models import User
from rest_framework import serializers
from apiproduct.models import Product, Stock, Demand


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True}}
        fields = ('url','username', 'email', 'password')

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ('url','id','name','especification','category','price')

class StockSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Stock
        fields = ('url','id','product','quantity')

class DemandSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Demand
        extra_kwargs = {'price': {'read_only': True}}
        fields = ('url','id','user','status','price','proc','ram','hd','vcd' ,'cab','mot','src')