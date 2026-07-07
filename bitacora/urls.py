from django.urls import path
from . import views

urlpatterns = [
    path('', views.bitacora, name='bitacora'),
    path('nuevo/', views.registrar, name='nuevo'),
    path('eventos/<str:event_type>/', views.eventos, name='eventos'),
]