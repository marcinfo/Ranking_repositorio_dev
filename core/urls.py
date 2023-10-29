from django.urls import path, include

from . import views
from .views import index

urlpatterns = [
    path('', index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit'),
    path('processar/', views.mostra_ocorrencia, name='processar'),
    path('cadastrar_contrato/', views.cadastrar_contratoForm, name='cadastrar_contratos'),
    path('Indicadores/', views.cadastrar_contratoForm, name='Indicadores'),
    path('visualizar_indices/', views.mostra_tabela, name='visualizar_indices'),
    path('visualizar_imagem/<int:pk>', views.visualizar_imagem, name='visualizar_imagem'),
    path('enviar_email_backend/', views.enviar_email_backend, name='enviar_email_backend'),
]
