"""camera_fermentazione URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.views import RegisterChartViewSet, RegisterChartMegiaGiorniViewSet, FermentationViewSet
from camera_fermentazione.celery import reset_all

router = routers.DefaultRouter(trailing_slash=False)
router.register('fermentation', FermentationViewSet, basename='fermentation')
router.register('andamento-temperatura', RegisterChartViewSet, basename='andamento-temperatura')
router.register('media-temperatura-giorni', RegisterChartMegiaGiorniViewSet, basename='media-temperatura-giorni')


@api_view()
def reset(request, slug=None):
    # reset_all.delay()
    return Response({'slug': slug})


urlpatterns = [
    path('', admin.site.urls),
    path('reset/<str:slug>', reset),
    path('api/', include(router.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

