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
    path('vendedoras/acerto/', views.acerto_vendedora, name='acerto_vendedora'),
    path('vendedoras/<int:vendedora_id>/acerto/', views.acerto_vendedora, name='acerto_vendedora_com_id'),
    path('vendedoras/cadastro/', views.cadastro_vendedora, name='cadastro_vendedora'),
    path('vendedoras/contrato/<int:vendedora_id>/', views.download_contrato, name='download_contrato'),
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/cadastro/', views.cadastro_cliente, name='cadastro_cliente'),
    path('clientes/editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/excluir/<int:cliente_id>/', views.excluir_cliente, name='excluir_cliente'),
    path('produtos/cadastro/', views.cadastro_produto, name='cadastro_produto'),
    path('produtos/atualizar-quantidade/', views.atualizar_quantidade_produto, name='atualizar_quantidade_produto'),
    path('get_vendedora_info/', views.get_vendedora_info, name='get_vendedora_info'),
    path('concluir_acerto/', views.concluir_acerto, name='concluir_acerto'),
    path('get_produto_info/', views.get_produto_info, name='get_produto_info'),
    path('api/cliente/<int:cliente_id>/historico-compras/', views.historico_compras_cliente, name='historico_compras_cliente'),
    path('nova-venda/', views.nova_venda, name='nova_venda'),
    path('api/produto/<str:codigo>/', views.get_produto_info, name='get_produto_info'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

