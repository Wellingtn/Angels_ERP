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
    path('vendedoras/<int:vendedora_id>/', views.detalhes_vendedora, name='detalhes_vendedora'),
    path('vendedoras/cadastro/', views.cadastro_vendedora, name='cadastro_vendedora'),
    path('clientes/', views.clientes, name='clientes'),
    path('produtos/cadastro/', views.cadastro_produto, name='cadastro_produto'),
    path('produtos/atualizar-quantidade/', views.atualizar_quantidade_produto, name='atualizar_quantidade_produto'),
]

