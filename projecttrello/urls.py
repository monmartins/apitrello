"""projecttrello URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import url, include
from rest_framework import routers
from apiproduct import views as views_product
from apiproduct.apitrello import __init__ as trello

trello()

router = routers.DefaultRouter()
router.register(r'users', views_product.UserViewSet)
router.register(r'product', views_product.ProductViewSet)
router.register(r'stock', views_product.StockViewSet,'stock')
router.register(r'demand', views_product.DemandViewSet)

urlpatterns = [

    url(r'^', include(router.urls)),
    url(r'^webhook', views_product.webhook, name='webhook'),


    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^admin/', admin.site.urls),
]
