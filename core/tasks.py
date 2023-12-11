from datetime import datetime,date,timedelta
from dateutil.relativedelta import relativedelta
from .models import tb_dados_contrato,tb_referencia_contrato
from django.db.models import Q
from celery import shared_task,Task

@shared_task
def teste_celery3():
    print('teste agendamento tesk celery')
@shared_task
def gerar_mes_referencia():
    print('teste')


