"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('veiculos/', views.lista_veiculos, name='lista_veiculos'),
    path('veiculos/novo/', views.cadastrar_veiculo, name='cadastrar_veiculo'),
    path('servidor/novo/', views.cadastrar_servidor, name='cadastrar_servidor'),
    path('sev/nova/', views.registrar_sev, name='registrar_sev'),
    path('sev/', views.lista_sev, name='lista_sev'),
]