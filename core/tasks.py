from datetime import datetime,date,timedelta
from dateutil.relativedelta import relativedelta
from .models import tb_dados_contrato,tb_referencia_contrato,tb_premio_excel
from django.db.models import Q
from celery import shared_task
from .views import gerar_mes_referencia
import logging
logger =logging.getLogger('django')
data_log = datetime.now()
def verifica_validade_contrato():
    valida_contrato = tb_dados_contrato.objects.\
    values_list('numemro_contrato','administrador','unidade', 'superintendente','data_inicio','data_fim').\
    filter(Q(Q(ativo = True) & Q(data_fim__lte = date.today())))
    for valida in valida_contrato:
        tb_dados_contrato.objects.update(ativo = 'Não')
        print(valida_contrato)
    return "Tarefa executada"
@shared_task
def teste_task3(name='Cria_mes_referencia',rety_backoff=True):
    logger.info('****************************')
    logger.info(' Iniciando tarefa agendada. ')
    logger.info('****************************')
    try:
        try:
            logger.info('Validando contratos!')
            valida_contrato = tb_dados_contrato.objects.\
            values_list('numemro_contrato','administrador','unidade', 'superintendente','data_inicio','data_fim').\
            filter(Q(Q(ativo = True) & Q(data_fim__lte = date.today())))

            if len(valida_contrato) >0:
                logger.info('Atualizando Status!')
                for valida in valida_contrato:
                    print('atualizando status')
                    tb_dados_contrato.objects.update(ativo = 'Não')
            else:
                logger.info('não existem contratos para atualizar status como INATIVO!')
        except:
            logger.error('erro: Não consegui validar os status dos contratos')
        try:
            logger.info("iniciando tarefa para criação da calendario para o mês de referencia")
            data=date.today() - relativedelta(months=1)
            mes_ano_format=data.strftime("%m/%Y")
            logger.info(f'mês de referencia {mes_ano_format}')
            lista_contratos = tb_dados_contrato.objects.\
            values_list('numemro_contrato','administrador','unidade', 'superintendente','staff_1','staff_1').\
            filter(Q(Q(ativo = 'SIM') & Q(data_fim__gte = date.today()) & Q(data_inicio__lte = date.today())))
            if len(lista_contratos) > 0:
                logger.info("criando calendario referencia")
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
                    if len(verificar_referencia) == 0:
                        logger.info(num_contra)
                        salva_ref = tb_referencia_contrato.objects.\
                            create(mes_ano_referencia=ref,contrato=num_contra,administrador=admin,status='ABERTO',
                                   superintendente=superintendente,unidade = unidade, staf_1=staff_1,staf_2=staff_2)
                        salva_ref.save()
                    else:
                        logger.info('Mês referencia já foi criado anteriormente')
            else:
                logger.erro('Nenhum contrato cadastrado, Mês/ref nao criado!')
        except:
            logger.erro('erro ao gerar o calendario')
        logger.info( 'Tarefa agendada finalizada')
    except:
        logger.error( 'Erro ao processar a tarefa,! verifique o status da aplicacao e do Banco de Dados')
    return 'Tarefa finalizada'
