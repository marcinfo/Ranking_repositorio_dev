from django.contrib import admin
from .models import Profile,tb_dados_contrato,tb_modalidade_interior,tb_modalidade_metropolitana,tb_log_email


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'photo']
@admin.register(tb_modalidade_metropolitana)
class tb_modalidade_metropolitanaAdmin(admin.ModelAdmin):
    list_display = ['id','mes_ano_referencia','contrato','idg','ida','ide','idr','entrega_cadastro',
                    'seg_capacitacao']

@admin.register(tb_modalidade_interior)
class tb_modalidade_interiorAdmin(admin.ModelAdmin):
    list_display = ['id','mes_ano_referencia','contrato','idg_interior','servicos_arsesp','entrega_cadastro',
                    'acidente_trabalho']
@admin.register(tb_dados_contrato)
class tb_dados_contratoAdmin(admin.ModelAdmin):
    list_display = ['id','r_m','inserido','cadastrado_por','numemro_contrato',
                    'nome_contratada','administrador','data_inicio','data_fim','staff_1','staff_2']
    filter=['r_m','cadastrado_por','numemro_contrato','nome_contratada','administrador']
    ordering = ['numemro_contrato','administrador',]
    search =['r_m','cadastrado_por','numemro_contrato','nome_contratada','administrador']
