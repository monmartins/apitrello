# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import json

from django.db.models import Model
from django.contrib.auth.models import User
from rest_framework import viewsets
from apiproduct.serializers import UserSerializer, ProductSerializer, StockSerializer, DemandSerializer
from apiproduct.models import Product, Stock, Demand
import apiproduct.apitrello as trello
from rest_framework.response import Response
from rest_framework import status

import copy, json, datetime
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST



def pretty_request(request):
    headers = ''
    for header, value in request.META.items():
        if not header.startswith('HTTP'):
            continue
        header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
        headers += '{}: {}\n'.format(header, value)

    return (
        '{method} HTTP/1.1\n'
        'Content-Length: {content_length}\n'
        'Content-Type: {content_type}\n'
        '{headers}\n\n'
        '{body}'
    ).format(
        method=request.method,
        content_length=request.META['CONTENT_LENGTH'],
        content_type=request.META['CONTENT_TYPE'],
        headers=headers,
        body=request.body,
)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows product to be viewed or edited.
    """
    queryset = Product.objects.all().order_by('-date_joined')
    serializer_class = ProductSerializer
    def put(self, *args, **kwargs):
        if Product.objects.filter(pk=json.loads(self.request.body.decode('utf-8'))['id']).update(json.loads(self.request.body.decode('utf-8'))):
            return Response(json.loads("200"))
        else:
            return Response(json.loads("400"))
    def delete(self, *args, **kwargs):
        if Product.objects.filter(pk=json.loads(self.request.body.decode('utf-8'))['id']).delete():
            return Response(json.loads("200"))
        else:
            return Response(json.loads("400"))

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    def put(self, *args, **kwargs):
        if Stock.objects.filter(pk=json.loads(self.request.body.decode('utf-8'))['id']).update(quantity=json.loads(self.request.body.decode('utf-8'))['quantity']):
            return Response(json.loads("200"))
        else:
            return Response(json.loads("400"))
    def delete(self, *args, **kwargs):
        if Stock.objects.filter(pk=json.loads(self.request.body.decode('utf-8'))['id']).delete():
            return Response(json.loads("200"))
        else:
            return Response(json.loads("400"))

class DemandViewSet(viewsets.ModelViewSet):
    queryset = Demand.objects.all()
    serializer_class = DemandSerializer
    def create(self, request, *args, **kwargs):
        datamd = request.data.copy()
        datamd['status'] = 'PER'
        serializer = self.get_serializer(data=datamd)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        name = "Pedido "+serializer.data['id']
        desc = "  Cliente:\n    nome: "+str(User.objects.filter(pk=str(serializer.data['user']).split("/")[-2]).first())+\
        "\n email: "+(User.objects.filter(pk=str(serializer.data['user']).split("/")[-2]).first()).email+"\n\n"+\
        "Componentes:\n"+\
        "   Placa de Vídeo "+ serializer.data['vcd'].name+\
        "   Processador "+serializer.data['proc'].name +\
        "   Disco Rígido "+serializer.data['hd'].name+\
        "   Memória "+serializer.data['ram'].name+\
        "   Placa Mãe "+ serializer.data['mot'].name+\
        "   Gabinete "+ serializer.data['cab'].name+\
        "   Fonte "+ serializer.data['src'].name
        trello.create_card(name,desc,"Pedido Realizado")
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def update(self, request, *args, **kwargs):
        if Demand.objects.filter(pk=str(request.data['id'].encode('ascii'))).update(status=str(request.data['status'])):
            demand = Demand.objects.filter(pk=str(request.data['id'])).first()
            name = "Pedido "+str(demand.id)
            trello.update_card(name,str(request.data['status']))
            return Response(request.data, status=status.HTTP_200_OK)
        else:
            return Response(json.loads("400"), status=status.HTTP_400_BAD_REQUEST)

    def put(self, *args, **kwargs):
        if Demand.objects.filter(pk=json.loads(self.request.body.decode('utf-8'))['id']).update(status=json.loads(self.request.body.decode('utf-8'))['status']):
            demand = Demand.objects.filter(pk=json.loads(self.request.body.decode('utf-8'))['id']).first()
            name = "Pedido "+str(demand.id)
            trello.update_card(name,json.loads(self.request.body.decode('utf-8'))['status'])
            return Response(json.loads("200"), status=status.HTTP_200_OK)
        else:
            return Response(json.loads("400"), status=status.HTTP_400_BAD_REQUEST)
    def delete(self, *args, **kwargs):
        if Demand.objects.filter(pk=json.loads(self.request.body.decode('utf-8'))['id']).delete():
            return Response(json.loads("200"), status=status.HTTP_200_OK)
        else:
            return Response(json.loads("400"), status=status.HTTP_400_BAD_REQUEST)

from django.views.decorators.http import require_http_methods
@csrf_exempt
@require_http_methods(["HEAD", "POST"])
def webhook(request):
    if request.method in 'HEAD':
        return HttpResponse(status=200)
    if request.method in 'POST':
        DEMAND_ID = json.loads(request.body)['model']['name'].split(" ")[1]
        LIST_NAME = json.loads(request.body)['action']['data']['listAfter']['name']
        if LIST_NAME in 'Pedido Realizado':
            LIST_NAME = 'PER'
        elif LIST_NAME in 'Separação em Estoque':
            LIST_NAME = 'SES'
        elif LIST_NAME in 'Em montagem Rígido':
            LIST_NAME = 'EMM'
        elif LIST_NAME in 'Realização de testes':
            LIST_NAME = 'RET'
        elif LIST_NAME in 'Concluído':
            LIST_NAME = 'CDO'
        LIST_ID = str(json.loads(request.body)['action']['display']).split("listAfter")[1].split("}")[0].split("id':")[1]
        Demand.objects.filter(pk=DEMAND_ID).update(status=LIST_NAME)
        return HttpResponse(status=200)