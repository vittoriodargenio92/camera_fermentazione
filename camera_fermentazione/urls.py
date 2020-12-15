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
from django.http import JsonResponse
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from api.views import RegisterChartViewSet, RegisterChartMegiaGiorniViewSet, FermentationViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register('fermentation', FermentationViewSet, basename='fermentation')
router.register('andamento-temperatura', RegisterChartViewSet, basename='andamento-temperatura')
router.register('media-temperatura-giorni', RegisterChartMegiaGiorniViewSet, basename='media-temperatura-giorni')


def webhook(requests):
    return JsonResponse(
        {
            "session": {
                "id": "11111",
                "params": {}
            },
            "prompt": {
                # "override": false,
                # "content": {
                #     "card": {
                #         "title": "Card Title",
                #         "subtitle": "Card Subtitle",
                #         "text": "Card Content",
                #         "image": {
                #             "alt": "Google Assistant logo",
                #             "height": 0,
                #             "url": "https://developers.google.com/assistant/assistant_96.png",
                #             "width": 0
                #         }
                #     }
                # },
                "firstSimple": {
                    "speech": "This is a card rich response.",
                    "text": ""
                }
            }
        }
    )


urlpatterns = [
    path('', admin.site.urls),
    path('api/', include(router.urls)),
    path('webhook/', webhook),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

