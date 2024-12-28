from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('estoque/', views.estoque, name='estoque'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('vendedoras/', views.vendedoras, name='vendedoras'),
    path('clientes/', views.clientes, name='clientes'),
]

