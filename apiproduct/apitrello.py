# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests, json
#5b68f89994fcb43d83820da0 
TOKEN = '70518db137383f1c54096206149f9ea133f658bfc549ef6551994df440241f91'
KEY = '9238b082437c1752cc7b660098e5dcdf'
AUTH = {'key':KEY,'token':TOKEN}
URLEXTERNAL = "http://djangotrello.ddns.net"
URLWEBHOOK = "https://api.trello.com/1/webhooks/"
BOARD_ID = ""

url = "https://api.trello.com/1/"

def __init__():
    global BOARD_ID
    response = requests.request("GET", url+'members/me/boards', params=AUTH)
    exists=False
    for i in json.loads(response.text):
        if("apiprodutosloja" in i['url']):
            BOARD_ID=i['id']
            exists=True
            break
        else:
            continue
    if not exists:
        querystring = {"name":"API_PRODUTOS_LOJA",'key':KEY,'token':TOKEN}
        response = requests.request("POST", url+'boards/', params=querystring)
        BOARD_ID=json.loads(response.text)['id']
        response = requests.request("GET", url+'boards/'+BOARD_ID+'/lists', params=AUTH)
        for i in  json.loads(response.text):
            querystring = {"closed":"true",'key':KEY,'token':TOKEN}
            response= requests.request("PUT", url+'lists/'+i['id'], params=querystring)

        querystring = {"name":"Concluído","idBoard":BOARD_ID,'key':KEY,'token':TOKEN}
        response = requests.request("POST", url+'lists/', params=querystring)


        querystring = {"name":"Realização de testes","idBoard":BOARD_ID,'key':KEY,'token':TOKEN}
        requests.request("POST", url+'lists/', params=querystring)


        querystring = {"name":"Em montagem","idBoard":BOARD_ID,'key':KEY,'token':TOKEN}
        requests.request("POST", url+'lists/', params=querystring)



        querystring = {"name":"Separação em estoque","idBoard":BOARD_ID,'key':KEY,'token':TOKEN}
        requests.request("POST", url+'lists/', params=querystring)


        querystring = {"name":"Pedido Realizado","idBoard":BOARD_ID,'key':KEY,'token':TOKEN}
        requests.request("POST", url+'lists/', params=querystring)


def create_card(name,desc,type_card):
    global BOARD_ID
    LIST_ID=""
    response = requests.request("GET", url+'boards/'+BOARD_ID+'/lists', params=AUTH)
    for i in  json.loads(response.text):
        if(i['name'][:4] in type_card[:4] and i['name'][:-4] in type_card[:-4]):
            LIST_ID=i['id']
            break
    querystring = {"name":name,"desc":desc,"idList":LIST_ID,"keepFromSource":"all",'key':KEY,'token':TOKEN}
    response = requests.request("POST", url+'cards', params=querystring)
    querystring = {"active":True, "callbackURL":URLEXTERNAL+"/webhook","idModel":json.loads(response.text)['id'],'key':KEY,'token':TOKEN}
    requests.request("POST", URLWEBHOOK, params=querystring)


def update_card(name,type_card):
    global BOARD_ID
    LIST_ID=""
    CARD_ID=""
    if type_card in 'PER':
        type_card = 'Pedido Realizado'
    elif type_card in 'SES':
        type_card = 'Separação em Estoque'
    elif type_card in 'EMM':
        type_card = 'Em montagem Rígido'
    elif type_card in 'RET':
        type_card = 'Realização de testes'
    elif type_card in 'CDO':
        type_card = 'Concluído'
    response = requests.request("GET", url+'boards/'+BOARD_ID+'/lists', params=AUTH)
    for i in  json.loads(response.text):
        if(i['name'][:4] in type_card[:4] and i['name'][:-2] in type_card[:-2]):
            LIST_ID=i['id']
            break
    response = requests.request("GET", url+'boards/'+BOARD_ID+'/cards', params=AUTH)
    for i in  json.loads(response.text):
        print(i['name'])
        if(i['name'] in name):
            CARD_ID=i['id']
            break

    querystring = {"idList":LIST_ID,'key':KEY,'token':TOKEN}
    response = requests.request("PUT", url+'cards/'+CARD_ID, params=querystring)