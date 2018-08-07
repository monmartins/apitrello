# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.validators import MaxLengthValidator
from django.db import models
from django.contrib.auth.models import User
import uuid, datetime

# Create your models here.


class Product(models.Model):
    name = models.CharField( max_length=30,validators=[MaxLengthValidator(30)])
    CATEGORY = (
        ('PROC', 'Processadores'),
        ('RAM', 'Memória RAM'),
        ('HD', 'Disco Rígido'),
        ('VCD', 'Placa de Vídeo'),
        ('CAB', 'Gabinete'),
        ('MOT', 'Placa mãe'),
        ('SRC', 'Fonte'),
    )
    category = models.CharField(
        max_length=3,
        choices=CATEGORY
    )
    date_joined = models.DateField(
        auto_now_add=True
    )

    id =  models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    especification = models.TextField(validators=[MaxLengthValidator(200)])

    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
            return "%s " % (self.name)



class Stock(models.Model):
    id =  models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.TextField(validators=[MaxLengthValidator(25)], editable=False)
    quantity = models.IntegerField()
    def save(self, *args, **kwargs):
        self.product_name = self.product.name
        super(Stock, self).save(*args, **kwargs)


class Demand(models.Model):
    id =  models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user_product')
    STATUS = (
        ('PER', 'Pedido Realizado'),
        ('SES', 'Separação em Estoque'),
        ('EMM', 'Em montagem Rígido'),
        ('RET', 'Realização de testes'),
        ('CDO', 'Concluído'),
    )
    status = models.CharField(
        max_length=3,
        choices=STATUS,
        default='PER'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    proc = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='proc_product')
    ram = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='ram_product')
    hd = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='hd_product')
    vcd = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='vcd_product')
    cab = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='cab_product')
    mot = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='mot_product')
    src = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='src_product')

    def save(self, *args, **kwargs):
        list_comp = [self.proc,self.ram,self.hd,self.vcd,self.cab,self.mot,self.src]
        stock_quantity_negative = [] 
        val = False
        #Have in Stock?
        # stock = Stock.objects.all()
        for i in list_comp:
            try:
                if (Stock.objects.get(product_name=i.name)).quantity==0:
                    val = False
                    break
                elif (Stock.objects.get(product_name=i.name)).quantity>0:
                    stock_quantity_negative.append(i.name)
                    val = True
                    continue
            except Stock.DoesNotExist:
                val = False
                break
        #Each category only
        # 
        if val:
            for i in list_comp:
                count=0
                for j in list_comp:
                    if i.category in j.category:
                        count=count+1
                    if count >= 2:
                        val = False
                        break
        #Is category correct?
        if val and list_comp[0].category in 'PROC' and \
        list_comp[1].category in 'RAM' and\
        list_comp[2].category in 'HD' and \
        list_comp[3].category in 'VCD' and \
        list_comp[4].category in 'CAB' and \
        list_comp[5].category in 'MOT' and \
        list_comp[6].category in 'SRC' :
            pass
        else:
            val = False

        if val:
            #update Stock
            for i in stock_quantity_negative:
                Stock.objects.filter(product_name=i).update(quantity=(Stock.objects.get(product_name=i)).quantity-1)
            #update price
            self.price = self.proc.price + self.ram.price +self.hd.price +self.vcd.price + self.cab.price + self.mot.price +self.src.price
            super(Demand, self).save(*args, **kwargs)