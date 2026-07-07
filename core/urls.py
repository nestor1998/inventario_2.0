from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from django.urls import include

urlpatterns = [
    path('', views.home, name='home'),
    path("api/", include("core.api.urls")),
    path('productos/', views.producto, name='product'),
    path('gestionar-stock/', views.gestionar_stock, name='gestionar_stock'),
    path('importar-productos/', views.import_products, name='import_products'),
    path('excel-productos/', views.excel_productos, name='excel_productos'),
    path('categoria/<str:category_name>/', views.categoria, name='category'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path("cotizaciones-web/", views.cotizaciones_web, name="cotizaciones_web"),    
]
