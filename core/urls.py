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
    path('as_melhores/', views.as_melhores, name='as_melhores'),
    path('melhores_M/', views.melhores_M, name='melhores_M'),
    path('melhores_R/', views.melhores_R, name='melhores_R'),
    path('melhores_idg_r/', views.melhores_idg_r, name='melhores_idg_r'),
    path('melhores_prazo_r/', views.melhores_prazo_r, name='melhores_prazo_r'),
    path('melhores_acidentes_r/', views.melhores_acidentes_r, name='melhores_acidentes_r'),
    path('melhores_cadastro_r/', views.melhores_cadastro_r, name='melhores_cadastro_r'),
    path('melhores_arsesp_r/', views.melhores_arsesp_r, name='melhores_arsesp_r'),
    path('informacoes_contrato/<int:pk>', views.informacoes_contrato, name='informacoes_contrato'),
    path('processar_indicadores/', views.processar_indicadores, name='processar_indicadores'),
    path('iniciar_processamento/', views.iniciar_processamento, name='iniciar_processamento'),
    path('enviar_email_backend/', views.enviar_email_backend, name='enviar_email_backend'),
]
