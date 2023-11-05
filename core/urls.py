from django.urls import path, include

from . import views
from .views import index

urlpatterns = [
    path('', index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit'),
    path('processar/', views.processar, name='processar'),
    path('informar_indice/', views.informar_indice, name='informar_indice'),
    path('indicadores_M/', views.indicadores_M, name='indicadores_M'),
    path('indicadores_R/', views.indicadores_R, name='indicadores_R'),
    path('cadastrar_contrato/', views.cadastrar_contrato, name='cadastrar_contrato'),
    path('menu_indices/', views.menu_indices, name='menu_indices'),
    path('menu_contratos/', views.menu_contratos, name='menu_contratos'),
    path('as_melhores/', views.as_melhores, name='as_melhores'),
    path('melhores_M/', views.melhores_M, name='melhores_M'),
    path('melhores_R/', views.melhores_R, name='melhores_R'),
    path('enviar_email_backend/', views.enviar_email_backend, name='enviar_email_backend'),
]
