from datetime import datetime,date,timedelta
from dateutil.relativedelta import relativedelta
from .models import tb_dados_contrato,tb_referencia_contrato
from django.db.models import Q
from celery import shared_task

@shared_task
def teste_celery():
    print('teste agendamento tesk celery')
@shared_task
def gerar_mes_referencia():
    data=date.today() - relativedelta(months=1)
    mes_ano_format=data.strftime("%B/%Y")
    lista_contratos = tb_dados_contrato.objects.\
        values_list('numemro_contrato','administrador','unidade', 'superintendente','staff_1','staff_1').\
        filter(Q(Q(ativo = 'SIM') & Q(data_fim__gte = date.today()) & Q(data_inicio__lte = date.today())))
    if lista_contratos.count != 0:
        for cont in lista_contratos:
            ref=mes_ano_format
            num_contra=cont[0]
            admin=cont[1]
            unidade=cont[2]
            superintendente=cont[3]
            staff_1=cont[4]
            staff_2=cont[5]

            verificar_referencia = tb_referencia_contrato.objects.all().\
                filter(mes_ano_referencia=ref,contrato=num_contra)
            if verificar_referencia.count() == 0:
                salva_ref = tb_referencia_contrato.objects.\
                    create(mes_ano_referencia=ref,contrato=num_contra,administrador=admin,status='ABERTO',
                           superintendente=superintendente,unidade = unidade, staf_1=staff_1,staf_2=staff_2)
                salva_ref.save()
            else:
                print('ja existe')
    else:
        print('Nenhum contrato cadastrado')
