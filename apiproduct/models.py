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
    quantity = models.IntegerField()


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
        self.price = self.proc.price + self.ram.price +self.hd.price +self.vcd.price + self.cab.price + self.mot.price +self.src.price
        super(Demand, self).save(*args, **kwargs)