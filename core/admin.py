from django.contrib import admin
from .models import Profile,tb_dados_contrato,tb_modalidade_interior,tb_modalidade_metropolitana,\
    tb_log_email,tb_unidades,tb_referencia_contrato


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
                    'nome_contratada','gestor_1','gestor_2','resp_contratada','administrador','superintendente','data_inicio','data_fim','staff_1','staff_2']
    filter=['r_m','cadastrado_por','numemro_contrato','nome_contratada','administrador']
    ordering = ['numemro_contrato','administrador',]
    search =['r_m','cadastrado_por','numemro_contrato','nome_contratada','administrador']

@admin.register(tb_unidades)
class tb_unidadesAdmin(admin.ModelAdmin):
    list_display = ['id','inserido','inserido_por','num_unidade','sigla_unidade','nome_unidade','superintendente']

@admin.register(tb_referencia_contrato)
class tb_referencia_contratoAdmin(admin.ModelAdmin):
    list_display = ['id','status','unidade','administrador','mes_ano_referencia','resp_preenchimento','contrato','data_hora_preenchimento',
                    'staf_1','staf_2']
