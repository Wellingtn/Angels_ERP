from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('vendedoras/contrato/<int:vendedora_id>/', views.download_contrato, name='download_contrato'),
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/cadastro/', views.cadastro_cliente, name='cadastro_cliente'),
    path('clientes/editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/excluir/<int:cliente_id>/', views.excluir_cliente, name='excluir_cliente'),
    path('produtos/cadastro/', views.cadastro_produto, name='cadastro_produto'),
    path('produtos/atualizar-quantidade/', views.atualizar_quantidade_produto, name='atualizar_quantidade_produto'),
    path('editar-produto/<int:produto_id>/', views.editar_produto, name='editar_produto'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

