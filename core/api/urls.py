from django.urls import path
from .views import CotizacionesApi

urlpatterns = [
    path('cotizaciones/', CotizacionesApi.as_view(), name='cotizaciones_api'),
]
