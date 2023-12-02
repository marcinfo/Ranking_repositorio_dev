from django.urls import path, include

from . import views
from .views import index

urlpatterns = [
    path('', index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit'),
    path('sistema/', views.sistema, name='sistema'),
    #path('contratos/', views.informar_indice, name='informar_indice'),
    path('indicadores_M/', views.indicadores_M, name='indicadores_M'),
    path('indicadores_R/', views.indicadores_R, name='indicadores_R'),
    path('cadastrar_contrato/', views.cadastrar_contrato, name='cadastrar_contrato'),
    path('menu_indices/', views.menu_indices, name='menu_indices'),
    path('menu_contratos/', views.menu_contratos, name='menu_contratos'),
    path('contratos_pendentes/', views.contratos_pendentes, name='contratos_pendentes'),
    path('visualizar_contratos/', views.visualizar_contratos, name='visualizar_contratos'),
    path('status_contrato/', views.status_contrato, name='status_contrato'),
    path('ranking/', views.ranking, name='ranking'),
    path('melhores_idg/', views.melhores_idg, name='melhores_idg'),
    path('melhores_isap/', views.melhores_isap, name='melhores_isap'),
    path('melhores_ida/', views.melhores_ida, name='melhores_ida'),
    path('melhores_ide/', views.melhores_ide, name='melhores_ide'),
    path('melhores_idr/', views.melhores_idr, name='melhores_idr'),
    path('melhores_comgas/', views.melhores_comgas, name='melhores_comgas'),
    path('melhores_cadastro/', views.melhores_cadastro, name='melhores_cadastro'),
    path('melhores_capacitacao/', views.melhores_capacitacao, name='melhores_capacitacao'),
    path('melhores_seguranca/', views.melhores_seguranca, name='melhores_seguranca'),
    path('melhores/', views.melhores, name='melhores'),
    path('melhores_interior/', views.melhores_interior, name='melhores_interior'),
    path('melhores_interior_idg/', views.melhores_interior_idg, name='melhores_interior_idg'),
    path('melhores_interior_arsesp/', views.melhores_interior_arsesp, name='melhores_interior_arsesp'),

    path('melhores_interior_seguranca/', views.melhores_interior_seguranca, name='melhores_interior_seguranca'),
    path('melhores_interior_cadastro/', views.melhores_interior_cadastro, name='melhores_interior_cadastro'),

    path('informacoes_contrato/<int:pk>', views.informacoes_contrato, name='informacoes_contrato'),
    path('processar_indicadores/', views.processar_indicadores, name='processar_indicadores'),
    path('iniciar_processamento/', views.iniciar_processamento, name='iniciar_processamento'),
    path('enviar_email_backend/', views.enviar_email_backend, name='enviar_email_backend'),
    path('contatos/', views.contatos, name='contatos'),
]
