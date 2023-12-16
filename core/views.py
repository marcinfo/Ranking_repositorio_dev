import pandas as pd
import logging
from rolepermissions.roles import assign_role
#import locale
import smtplib
from datetime import datetime,date,timedelta
from dateutil.relativedelta import relativedelta
from decouple import config
from django.core.mail import EmailMultiAlternatives
from django.template.loader import  render_to_string
from django.utils.html import strip_tags
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm,Cadastrar_ContratoForm,\
    informar_indicador_MForm,informar_indicador_RForm
from .models import Profile,tb_log_email,tb_referencia_contrato,tb_dados_contrato,tb_modalidade_metropolitana,\
    tb_modalidade_interior,tb_premio_excel
from django.conf import settings
from rolepermissions.decorators import has_role_decorator,has_permission_decorator

#locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
data_log = datetime.now()
data_log=data_log.strftime("%H:%M:%S %d-%m-%Y")
mensagem_concorrencia = 'sem concorrentes para esta posição'
logger =logging.getLogger('django')

def verifica_validade_contrato():
    valida_contrato = tb_dados_contrato.objects.\
    values_list('numemro_contrato','administrador','unidade', 'superintendente','data_inicio','data_fim').\
    filter(Q(Q(ativo = True) & Q(data_fim__lte = date.today())))
    for valida in valida_contrato:
        tb_dados_contrato.objects.update(ativo = 'Não')
        print(valida_contrato)
    return "Tarefa executada"
def gerar_mes_referencia():
    verifica_validade_contrato()
    data=date.today() - relativedelta(months=1)
    mes_ano_format=data.strftime("%m/%Y")
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
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated '\
                                        'successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(
                user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            assign_role(new_user, 'nao_liberado')
            # Create the user profile
            Profile.objects.create(user=new_user)
            return render(request,
                          'core/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'core/register.html',
                  {'user_form': user_form})
@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html', {'section': 'dashboard'})
@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(
                                    instance=request.user.profile,
                                    data=request.POST,
                                    files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request,
                  'core/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})

@login_required
def index(request):
    gerar_mes_referencia()
    horario =datetime.now()
    horario = int(horario.strftime("%H"))
    if (horario >= 0) and (horario <12):
        saudacao = 'Bom dia'
    elif (horario >= 12) and (horario <18):
        saudacao = 'Boa tarde'
    else:
        saudacao = 'Boa noite'


    context={
        'saudacao':saudacao,
    }

    return render(request, 'core/index.html',context)
@has_permission_decorator('contrato')
def cadastrar_contrato(request):

    if request.method == "GET":
        form=Cadastrar_ContratoForm()
        context={
            'form': form
        }
        return render(request, 'core/cadastrar_contrato.html',context=context)
    else:
        form = Cadastrar_ContratoForm(request.POST, request.FILES)
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.cadastrado_por = request.user
            contrato.staff_1 = request.user
            cadastro = form.save()
            messages.success(request, 'Contrato Cadastrado com Sucesso! Para cadastrar outro continue.')
            form = Cadastrar_ContratoForm()
        context = {
            'form':form
        }
        return render(request, 'core/cadastrar_contrato.html',context=context)
@has_permission_decorator('contrato')
def indicadores_M(request):

    mes_ano_ref = tb_referencia_contrato.objects.all().order_by('-id').filter(status='ABERTO').first()

    if request.method == "GET":
        form=informar_indicador_MForm()
        context={
            'form': form
        }
        return render(request, 'core/indicadores_M.html',context=context)
    else:
        form = informar_indicador_MForm(request.POST, request.FILES)
        if form.is_valid():
            indicadorM = form.save(commit=False)
            indicadorM.inserido_por = request.user
            indicadorM.mes_ano_referencia = mes_ano_ref
            indicadorM.entrega_cadastro = (indicadorM.total_cadastro_entregue/indicadorM.total_redes)*100
            indicadorM.seg_capacitacao=(indicadorM.quantidade_acidentes/indicadorM.quantidade_colaboradores)*100

            contrato_autorizado = tb_dados_contrato.objects.values('numemro_contrato').\
                filter((Q(Q(numemro_contrato=indicadorM.contrato)) & (Q(staff_1=request.user) | Q(staff_2=request.user)))).first()
            contrato_autorizado=str(contrato_autorizado)

            if indicadorM.contrato in contrato_autorizado :
                indicadorM = form.save()
                messages.success(request, f'Indicador do Contrato {indicadorM.contrato} foi cadastrado com Sucesso!')
                form = informar_indicador_MForm()
                tb_referencia_contrato.objects.filter(Q(Q(contrato=indicadorM.contrato) &
                                        Q(mes_ano_referencia=indicadorM.mes_ano_referencia))).\
                    update(status='INFORMADO')

                print(indicadorM.contrato)
            else:
                pass
                messages.error(request,f'Você não tem permissão para informar indicadores '
                                       f'para o contrato {indicadorM.contrato}! Verifique o número do CONTRATO ou'
                                       f' revise o CADASTRO. ')
        else:
            pass
            messages.warning(request,'Verifique o preenchimento!')
        context = {

            'form':form
        }
        return render(request, 'core/indicadores_M.html',context=context)
@has_permission_decorator('contrato')
def indicadores_R(request):

        return render(request, 'core/indicadores_R.html')
@has_permission_decorator('contrato','melhores')
def contratos_pendentes(request):
    cont_pendentes = tb_dados_contrato.objects.filter(numemro_contrato__in =tb_referencia_contrato.
                                                      objects.values_list('contrato').filter(status='ABERTO'))
    context ={'cont_pendentes':cont_pendentes,

              }
    return render(request, 'core/contratos_pendentes.html',context)
@has_permission_decorator('administrar')
def sistema(request):
    return render(request, 'core/sistema.html')
@has_permission_decorator('contrato')
def menu_indices(request):

    return render(request, 'core/menu_indices.html')
@has_permission_decorator('contrato')
def menu_contratos(request):
    return render(request, 'core/menu_contratos.html')
def handle404(request,exception):
    return render(request, 'core/erro_404.html')
def handler500(request, *args, **argv):
    return render(request, 'core/erro_500.html', status=500)
def handler400(request, exception):
    return render(request, 'core/erro_400.html',status=400)
def handler401(request, exception):
    return render(request, 'core/erro_401.html',status=401)
def handler402(request, exception):
    return render(request, 'core/erro_402.html',status=402)
def handler403(request, exception):
    error_message = messages.add_message(request, messages.ERROR, "Sem Permissão de Acesso!")
    errors = {'errors': error_message}
    return render(request, 'core/erro_403.html',status=403)
def handler404(request, exception):
    return render(request, 'core/erro_404.html',status=404)
def enviar_email_backend():
    print('Criando lista de emails')
    email_usuario = list(User.objects.values_list('first_name','email', flat=True).filter(is_active=True))
    nome_usuario = email_usuario ['first_name']
    print(email_usuario)
    print('enviando email')
    html_content = render_to_string('core/enviar_email_backend.html',{'nome':'Monitor de pragas'})
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives('Ocorrência Cadastrada',text_content,
                                   settings.EMAIL_HOST_USER,['ARLETA!!!'],email_usuario)
    email.attach_alternative(html_content, "text/html")
    email.send()
    print('enviado')
    return HttpResponse('Email enviado com sucesso!')

def enviar_email():

    inicio_envio_email = datetime.now()

    email_usuario = User.objects.values('first_name','email').filter(is_active=True)

    host = config('EMAIL_HOST')
    port = config('EMAIL_PORT')
    login = config('EMAIL_HOST_USER')
    senha = config('EMAIL_HOST_PASSWORD')
    server = smtplib.SMTP(host, port)

    server.ehlo()
    server.starttls()

    server.login(login, senha)
    total_email = email_usuario.count()
    conta_email = 0
    for email_cad in email_usuario:

        enviado = email_cad['email']
        nome = email_cad['first_name']
        corpo = f"<b color='#1C1C1C'>Olá, {nome}. <br>Uma nova ocorrência de PRAGA foi cadastrada, para mais informações acesse \
          o sistema de <a href='https://monitordepragasonline.onrender.com/'>Monitor de Pragas</a> online.</br></b>"

        email_msg =MIMEMultipart()
        email_msg['From'] = login
        email_msg['To'] = 'marcelosantos170@gmail.com'
        email_msg['Cco'] = enviado

        email_msg['Subject'] = "MONITOR DE PRAGAS on-line - TCC530 - Turma 002 - Univesp"
        email_msg.attach(MIMEText(corpo, 'html'))
        server.sendmail(email_msg['From'], email_msg['Cco'], email_msg.as_string())
        email = email_msg['Cco']
        conta_email = conta_email + 1
        print(f'{conta_email}-{email}')
    server.quit()
    if total_email == conta_email:
        status = 'OK - Todos os emails foram enviados.'
    elif total_email > conta_email:
        status = 'ERRO - Nem todos os emails foram enviados.'
    elif conta_email == 0:
        status = 'Falha - Nenhum email foi enviado.'


    fim_envio_email = datetime.now()
    tempo_envio_email = fim_envio_email - inicio_envio_email
    tempo_envio_email =str(tempo_envio_email)[0:7]
    inicio_envio_email = inicio_envio_email.strftime("%H:%M:%S %d/%m/%Y")
    fim_envio_email = fim_envio_email.strftime("%H:%M:%S %d/%m/%Y")
    log = tb_log_email.objects.create(inicio_envio = inicio_envio_email,fim_envio = fim_envio_email,
                                      total_enderecos= total_email, total_de_envio = conta_email,
                                      tempo_envio = tempo_envio_email, status_tarefa = status)
    log.save()

    print(f'inicio do envio em {inicio_envio_email}')
    print(f'{conta_email} enviados')
    print(f'{total_email} endereços selecionados')
    print(f'envio finalizado em {fim_envio_email}')
    print(f'Tempo de envio {tempo_envio_email}')

@has_permission_decorator('contrato')
def visualizar_contratos(request):

    cont_contratos = tb_dados_contrato.objects.values('id','r_m','numemro_contrato','ativo','unidade','superintendente',
        'administrador','nome_contratada','data_inicio','data_fim').\
    filter(Q(Q(staff_1=request.user) | Q(staff_2=request.user)))

    context ={'cont_contratos':cont_contratos,
              }
    return render(request, 'core/visualizar_contratos.html',context)
@has_permission_decorator('administrar')
def processar_indicadores(request):
    #pagina em branco apenas botões no html SIM ou NÃO
    return render(request, 'core/processar_indicadores.html')

def iniciar_processamento(request):
    messages.info(request,f'{data_log}  validando contratos')
    valida_contrato = tb_dados_contrato.objects.\
    values_list('numemro_contrato','administrador','unidade', 'superintendente','data_inicio','data_fim').\
    filter(Q(Q(ativo = 'SIM') & Q(data_fim__lt = date.today())))
    for valida in valida_contrato:
        tb_dados_contrato.objects.update(ativo = 'False')
        print(valida_contrato)
    messages.info(request,f'{data_log} Validação Finalizada')

    messages.info(request,f'{data_log} gerando calendario referência')
    data=date.today() - relativedelta(months=1)
    mes_ano_format=data.strftime("%B/%Y")
    messages.info(request,f'{data_log} verificando se já existe calendario')
    lista_contratos = tb_dados_contrato.objects.\
        values_list('numemro_contrato','administrador','unidade', 'superintendente','staff_1','staff_1').\
        filter(Q(Q(ativo = 'SIM') & Q(data_fim__gte = date.today()) & Q(data_inicio__lte = date.today())))
    if lista_contratos.count != 0:

        for cont in lista_contratos:
            messages.info(request,f'{data_log} verificando contrato {cont[0]}')
            ref=mes_ano_format
            num_contra=cont[0]
            admin=cont[1]
            unidade=cont[2]
            superintendente=cont[3]
            staff_1=cont[4]
            staff_2=cont[5]
            print(staff_1)
            verificar_referencia = tb_referencia_contrato.objects.all().\
                filter(mes_ano_referencia=ref,contrato=num_contra)
            if verificar_referencia.count() == 0:
                messages.info(request,f'{data_log} criando para o contrato {cont[0]}')
                salva_ref = tb_referencia_contrato.objects.\
                    create(mes_ano_referencia=ref,contrato=num_contra,administrador=admin,status='ABERTO',
                           superintendente=superintendente,unidade = unidade, staf_1=staff_1,staf_2=staff_2)
                salva_ref.save()

                messages.info(request,f'{data_log} criando calendario para o contrato {num_contra}')
            else:
                messages.info(request,f'{data_log} calendario já existe para o contrato {num_contra}')
    else:
        messages.info(request,f'{data_log} Falha ao gerar calendario, nao existe contrato ativo cadastrado')

    messages.info(request,f'{data_log} Fim do processamento')
    return render(request, 'core/iniciar_processamento.html')
@has_permission_decorator('contrato')
def status_contrato(request):
    lista_contrato_usuario = tb_dados_contrato.objects.values_list('numemro_contrato')\
        .filter(Q(Q(staff_1 = request.user)|Q(staff_2 = request.user)))

    cont_contratos = tb_referencia_contrato.objects.values('id','mes_ano_referencia','contrato','unidade','status',
                                                           'administrador','data_inicio','data_fim').\
        filter(contrato__in =lista_contrato_usuario,status = "ABERTO")

    context ={'cont_contratos':cont_contratos,
              }
    return render(request, 'core/status_contrato.html',context)
def melhores_interior_idg(request):
    referencia = tb_premio_excel.objects.values('mes_ref').filter(setor ='INTERIOR').order_by('-mes_ref').distinct()
    busca=request.POST.get('mes_ref')
    ref = tb_premio_excel.objects.values_list('mes_ref').order_by('-mes_ref').first()
    if (request.method=="POST") & (request.POST.get('mes_ref') != ''):

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'INDICE DE DESEMPENHO GLOBAL (IDG)') & Q(mes_ref= busca)& Q(setor= 'INTERIOR')))

        ref = request.POST.get('mes_ref')
    else:

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'INDICE DE DESEMPENHO GLOBAL (IDG)') & Q(mes_ref__in= ref) & Q(setor= 'INTERIOR')))

    context ={'cont_contratos':cont_contratos,
              'referencia':referencia,

              }
    return render(request, 'core/melhores_interior_idg.html',context)
def melhores_interior_arsesp(request):
    referencia = tb_premio_excel.objects.values('mes_ref').filter(setor ='INTERIOR').order_by('-mes_ref').distinct()
    busca=request.POST.get('mes_ref')
    ref = tb_premio_excel.objects.values_list('mes_ref').order_by('-mes_ref').first()
    if (request.method=="POST") & (request.POST.get('mes_ref') != ''):

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'SERVIÇOS ATENDIDOS NO PRAZO ARSESP') & Q(mes_ref= busca)& Q(setor= 'INTERIOR')))

        ref = request.POST.get('mes_ref')
    else:

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'SERVIÇOS ATENDIDOS NO PRAZO ARSESP') & Q(mes_ref__in= ref) & Q(setor= 'INTERIOR')))

    context ={'cont_contratos':cont_contratos,
              'referencia':referencia,

              }
    return render(request, 'core/melhores_interior_arsesp.html',context)
@has_permission_decorator('melhores')
def melhores_interior_seguranca(request):
    referencia = tb_premio_excel.objects.values('mes_ref').filter(setor ='INTERIOR').order_by('-mes_ref').distinct()
    busca=request.POST.get('mes_ref')
    ref = tb_premio_excel.objects.values_list('mes_ref').order_by('-mes_ref').first()
    if (request.method=="POST") & (request.POST.get('mes_ref') != ''):

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'SEGURANÇA') & Q(mes_ref= busca)& Q(setor= 'INTERIOR')))

        ref = request.POST.get('mes_ref')
    else:

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'SEGURANÇA') & Q(mes_ref__in= ref) & Q(setor= 'INTERIOR')))

    context ={'cont_contratos':cont_contratos,
              'referencia':referencia,

              }
    return render(request, 'core/melhores_interior_seguranca.html',context)
@has_permission_decorator('melhores')
def melhores_interior_cadastro(request):
    referencia = tb_premio_excel.objects.values('mes_ref').filter(setor ='INTERIOR').order_by('-mes_ref').distinct()
    busca=request.POST.get('mes_ref')
    ref = tb_premio_excel.objects.values_list('mes_ref').order_by('-mes_ref').first()
    if (request.method=="POST") & (request.POST.get('mes_ref') != ''):

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'ENTREGA DO CADASTRO E IMOBILIZAÇÃO') & Q(mes_ref= busca)& Q(setor= 'INTERIOR')))

        ref = request.POST.get('mes_ref')
    else:

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'ENTREGA DO CADASTRO E IMOBILIZAÇÃO') & Q(mes_ref__in= ref) & Q(setor= 'INTERIOR')))

    context ={'cont_contratos':cont_contratos,
              'referencia':referencia,

              }
    return render(request, 'core/melhores_interior_cadastro.html',context)
def contatos(request):

    return render(request, 'core/contatos.html')
@has_permission_decorator('contrato','melhores')
def informacoes_contrato(request,pk):
    contrato = tb_dados_contrato.objects.select_related('numemro_contrato').filter( id=pk).\
        values('id','ativo','numemro_contrato','superintendente','administrador','r_m','cadastrado_por','unidade',
               'nome_contratada','inserido','data_inicio','data_fim','staff_1','staff_2')

    context = {
        'contrato': contrato }
    return render(request, 'core/informacoes_contrato.html', context)

@has_permission_decorator('melhores')
def melhores(request):
    referencia = tb_premio_excel.objects.values('mes_ref').filter(setor ='CAPITAL',ativo='SIM').order_by('-mes_ref').distinct()
    ref = str(pd.DataFrame(referencia))
    if len(referencia) > 0:
        busca=request.POST.get('mes_ref')
        tabela = tb_premio_excel.objects.values('fornecedor','colocacao','modalidade','mes_ref').filter(setor ='CAPITAL',ativo='SIM')

        if (request.method=="POST") & (request.POST.get('mes_ref') != '') :

            tabela = tb_premio_excel.objects.values('fornecedor','colocacao','modalidade','mes_ref').\
                filter(mes_ref =busca,setor ='CAPITAL',ativo='SIM')

            ref = request.POST.get('mes_ref')

        else:
            ref = tb_premio_excel.objects.values_list('mes_ref').filter(setor ='CAPITAL',ativo='SIM').order_by('-mes_ref').first()
            ref=pd.DataFrame(ref).to_string(header=False,index=False)
            tabela = tb_premio_excel.objects.values('fornecedor','colocacao','modalidade','mes_ref').\
                filter(mes_ref =ref,setor ='CAPITAL',ativo='SIM')
        indicadores = pd.DataFrame(tabela)
        isap = indicadores[['fornecedor','colocacao','modalidade','mes_ref']].query('modalidade=="SERVIÇOS ATENDIDOS NO PRAZO (ISAP)"')
        idg = indicadores[['fornecedor','colocacao','modalidade','mes_ref']].query('modalidade=="INDICE DE DESEMPENHO GLOBAL (IDG)"')
        ida = indicadores[['fornecedor','colocacao','modalidade','mes_ref']].query('modalidade=="INDICE DE DESEMPENHO NA ÁGUA (IDA)"')
        ide = indicadores[['fornecedor','colocacao','modalidade','mes_ref']].query('modalidade=="INDICE DE DESEMPENHO NA ESGOTO(IDE)"')
        idr = indicadores[['fornecedor','colocacao','modalidade','mes_ref']].query('modalidade=="INDICE DE DESEMPENHO REPOSIÇÃO (IDR)"')
        cad_imob= indicadores[['fornecedor','colocacao','modalidade','mes_ref']].query('modalidade=="ENTREGA DO CADASTRO E IMOBILIZAÇÃO"')
        seg= indicadores[['fornecedor','colocacao','modalidade','mes_ref']].query('modalidade=="SEGURANÇA"')

        comgas= indicadores[['fornecedor','colocacao','modalidade','mes_ref']].query('modalidade=="SINISTROS OPERACIONAIS (COMGAS)"')
        capacita= indicadores[['fornecedor','colocacao','modalidade','mes_ref']].query('modalidade=="CAPACITAÇÃO DE EMPREGADOS"')

        primeiro_idr = idr.query('colocacao ==1')
        if primeiro_idr.empty == True:
            primeiro_idr='Sem concorrente'
        else:
            primeiro_idr= primeiro_idr[['fornecedor']].to_string(header=False,index=False)
        segundo_idr = idr.query('colocacao ==2')
        if segundo_idr.empty == True:
            segundo_idr=mensagem_concorrencia
        else:
            segundo_idr= segundo_idr[['fornecedor']].to_string(header=False,index=False)
        terceiro_idr = idr.query('colocacao ==3')
        if terceiro_idr.empty == True:
            terceiro_idr=mensagem_concorrencia
        else:
            terceiro_idr= terceiro_idr[['fornecedor']].to_string(header=False,index=False)
        primeiro_isap = isap.query('colocacao ==1')
        if primeiro_isap.empty == True:
            primeiro_isap=mensagem_concorrencia
        else:
            primeiro_isap= primeiro_isap[['fornecedor']].to_string(header=False,index=False)
        segundo_isap = isap.query('colocacao ==2')
        if segundo_isap.empty == True:
            segundo_isap=mensagem_concorrencia
        else:
            segundo_isap= segundo_isap[['fornecedor']].to_string(header=False,index=False)
        terceiro_isap = isap.query('colocacao ==3')
        if terceiro_isap.empty == True:
            terceiro_isap=mensagem_concorrencia
        else:
            terceiro_isap= terceiro_isap[['fornecedor']].to_string(header=False,index=False)

        primeiro_idg = idg.query('colocacao ==1')
        if primeiro_idg.empty == True:
            primeiro_idg=mensagem_concorrencia

        else:
            primeiro_idg= primeiro_idg[['fornecedor']].to_string(header=False,index=False)
        segundo_idg = idg.query('colocacao ==2')
        if segundo_idg.empty == True:
            segundo_idg=mensagem_concorrencia
        else:
            segundo_idg= segundo_idg[['fornecedor']].to_string(header=False,index=False)
        terceiro_idg = idg.query('colocacao ==3')
        if terceiro_idg.empty == True:
            terceiro_idg=mensagem_concorrencia
        else:
            terceiro_idg= terceiro_idg[['fornecedor']].to_string(header=False,index=False)
        primeiro_ida = ida.query('colocacao ==1')
        if primeiro_ida.empty == True:
            primeiro_ida=mensagem_concorrencia
        else:
            primeiro_ida= primeiro_ida[['fornecedor']].to_string(header=False,index=False)
        segundo_ida = ida.query('colocacao ==2')
        if segundo_ida.empty == True:
            segundo_ida=mensagem_concorrencia
        else:
            segundo_ida= segundo_ida[['fornecedor']].to_string(header=False,index=False)
        terceiro_ida = ida.query('colocacao ==3')
        if terceiro_ida.empty == True:
            terceiro_ida=mensagem_concorrencia
        else:
            terceiro_ida= terceiro_ida[['fornecedor']].to_string(header=False,index=False)
        primeiro_ide = ide.query('colocacao ==1')
        if primeiro_ide.empty == True:
            primeiro_ide=mensagem_concorrencia
        else:
            primeiro_ide= primeiro_ide[['fornecedor']].to_string(header=False,index=False)
        segundo_ide = ide.query('colocacao ==2')
        if segundo_ide.empty == True:
            segundo_ide=mensagem_concorrencia
        else:
            segundo_ide= segundo_ide[['fornecedor']].to_string(header=False,index=False)
        terceiro_ide = ide.query('colocacao ==3')
        if terceiro_ide.empty == True:
            terceiro_ide=mensagem_concorrencia
        else:
            terceiro_ide= terceiro_ide[['fornecedor']].to_string(header=False,index=False)
        primeiro_cad_imob = cad_imob.query('colocacao ==1')
        if primeiro_cad_imob.empty == True:
            primeiro_cad_imob=mensagem_concorrencia
        else:
            primeiro_cad_imob= primeiro_cad_imob[['fornecedor']].to_string(header=False,index=False)
        segundo_cad_imob = cad_imob.query('colocacao ==2')
        if segundo_cad_imob.empty == True:
            segundo_cad_imob=mensagem_concorrencia

        else:
            segundo_cad_imob= segundo_cad_imob[['fornecedor']].to_string(header=False,index=False)
        terceiro_cad_imob = cad_imob.query('colocacao ==3')
        if terceiro_cad_imob.empty == True:
            terceiro_cad_imob=mensagem_concorrencia

        else:
            terceiro_cad_imob= terceiro_cad_imob[['fornecedor']].to_string(header=False,index=False)

        primeiro_seg = seg.query('colocacao ==1')
        if primeiro_seg.empty == True:
            primeiro_seg=mensagem_concorrencia

        else:
            primeiro_seg= primeiro_seg[['fornecedor']].to_string(header=False,index=False)
        segundo_seg = seg.query('colocacao ==2')
        if segundo_seg.empty == True:
            segundo_seg=mensagem_concorrencia

        else:
            segundo_seg= segundo_seg[['fornecedor']].to_string(header=False,index=False)
        terceiro_seg = seg.query('colocacao ==3')
        if terceiro_seg.empty == True:
            terceiro_seg=mensagem_concorrencia

        else:
            terceiro_seg= terceiro_seg[['fornecedor']].to_string(header=False,index=False)

        primeiro_comgas = comgas.query('colocacao ==1')
        if primeiro_comgas.empty == True:
            primeiro_comgas=mensagem_concorrencia

        else:
            primeiro_comgas= primeiro_comgas[['fornecedor']].to_string(header=False,index=False)
        segundo_comgas = comgas.query('colocacao ==2')
        if segundo_comgas.empty == True:
            segundo_comgas=mensagem_concorrencia

        else:
            segundo_comgas= segundo_comgas[['fornecedor']].to_string(header=False,index=False)
        terceiro_comgas = comgas.query('colocacao ==3')
        if terceiro_comgas.empty == True:
            terceiro_comgas=mensagem_concorrencia

        else:
            terceiro_comgas= terceiro_comgas[['fornecedor']].to_string(header=False,index=False)
        primeiro_capacita = capacita.query('colocacao ==1')
        if primeiro_capacita.empty == True:
            primeiro_capacita=mensagem_concorrencia

        else:
            primeiro_capacita= primeiro_capacita[['fornecedor']].to_string(header=False,index=False)
        segundo_capacita = capacita.query('colocacao ==2')
        if segundo_capacita.empty == True:
            segundo_capacita=mensagem_concorrencia

        else:
            segundo_capacita= segundo_capacita[['fornecedor']].to_string(header=False,index=False)
        terceiro_capacita = capacita.query('colocacao ==3')
        if terceiro_capacita.empty == True:
            terceiro_capacita=mensagem_concorrencia
        else:
            terceiro_capacita= terceiro_capacita[['fornecedor']].to_string(header=False,index=False)
        context ={'referencia':referencia,'ref':ref,
            'primeiro_idg':primeiro_idg,
                'segundo_idg':segundo_idg,
                'terceiro_idg':terceiro_idg,
                'primeiro_isap':primeiro_isap,
                'segundo_isap':segundo_isap,
                'terceiro_isap':terceiro_isap,
                'primeiro_ida':primeiro_ida,
                'segundo_ida':segundo_ida,
                'terceiro_ida':terceiro_ida,
                'primeiro_ide':primeiro_ide,
                'segundo_ide':segundo_ide,
                'terceiro_ide':terceiro_ide,
                'primeiro_idr':primeiro_idr,
                'segundo_idr':segundo_idr,
                'terceiro_idr':terceiro_idr,
                'primeiro_cad_imob':primeiro_cad_imob,
                'segundo_cad_imob':segundo_cad_imob,
                'terceiro_cad_imob':terceiro_cad_imob,
                'primeiro_seg':primeiro_seg,
                'segundo_seg':segundo_seg,
                'terceiro_seg':terceiro_seg,
                'primeiro_comgas':primeiro_comgas,
                'segundo_comgas':segundo_comgas,
                'terceiro_comgas':terceiro_comgas,
                'primeiro_capacita':primeiro_capacita,
                'segundo_capacita':segundo_capacita,
                'terceiro_capacita':terceiro_capacita,
                  }
        return render(request, 'core/melhores.html',context)
    messages.error(request,'O Banco de Dados não tem Dados para o processamento!')
    return render(request, 'core/melhores.html')
@has_permission_decorator('melhores')
def melhores_interior(request):
    referencia = tb_premio_excel.objects.values('mes_ref').filter(setor ='INTERIOR',ativo='SIM').order_by('-mes_ref').distinct()
    ref = str(pd.DataFrame(referencia))
    if len(referencia) > 0:
        busca=request.POST.get('mes_ref')
        tabela = tb_premio_excel.objects.values('fornecedor','colocacao','modalidade','mes_ref').filter(setor ='INTERIOR',ativo='SIM')

        if (request.method=="POST") & (request.POST.get('mes_ref') != ''):

            tabela = tb_premio_excel.objects.values('fornecedor','colocacao','modalidade','mes_ref').\
                filter(mes_ref =busca,setor ='INTERIOR',ativo='SIM')

            ref = request.POST.get('mes_ref')

        else:
            ref = tb_premio_excel.objects.values_list('mes_ref').filter(setor ='INTERIOR',ativo='SIM').order_by('-mes_ref').first()
            ref=pd.DataFrame(ref).to_string(header=False,index=False)
            tabela = tb_premio_excel.objects.values('fornecedor','colocacao','modalidade','mes_ref').\
                filter(mes_ref =ref,setor ='INTERIOR',ativo='SIM')

        indicadores = pd.DataFrame(tabela)
        arsesp = indicadores[['fornecedor','colocacao','modalidade','mes_ref']].query('modalidade=="SERVIÇOS ATENDIDOS NO PRAZO ARSESP"')
        idg = indicadores[['fornecedor','colocacao','modalidade','mes_ref']].query('modalidade=="INDICE DE DESEMPENHO GLOBAL (IDG)"')
        cadastro = indicadores[['fornecedor','colocacao','modalidade','mes_ref']].query('modalidade=="ENTREGA DO CADASTRO E IMOBILIZAÇÃO"')

        seguranca = indicadores[['fornecedor','colocacao','modalidade','mes_ref']].query('modalidade=="SEGURANÇA"')

        primeiro_arsesp = arsesp.query('colocacao ==1')
        if primeiro_arsesp.empty == True:
            primeiro_arsesp=mensagem_concorrencia
        else:
            primeiro_arsesp= primeiro_arsesp[['fornecedor']].to_string(header=False,index=False)

        segundo_arsesp = arsesp.query('colocacao ==2')
        if segundo_arsesp.empty == True:
            segundo_arsesp=mensagem_concorrencia
        else:
            segundo_arsesp= segundo_arsesp[['fornecedor']].to_string(header=False,index=False)

        terceiro_arsesp = arsesp.query('colocacao ==3')
        if terceiro_arsesp.empty == True:
            terceiro_arsesp=mensagem_concorrencia
        else:
            terceiro_arsesp= terceiro_arsesp[['fornecedor']].to_string(header=False,index=False)

        primeiro_cadastro = cadastro.query('colocacao ==1')
        if primeiro_cadastro.empty == True:
            primeiro_cadastro=mensagem_concorrencia
        else:
            primeiro_cadastro= primeiro_cadastro[['fornecedor']].to_string(header=False,index=False)
        segundo_cadastro = cadastro.query('colocacao ==2')
        if segundo_cadastro.empty == True:
            segundo_cadastro=mensagem_concorrencia
        else:
            segundo_cadastro= segundo_cadastro[['fornecedor']].to_string(header=False,index=False)

        terceiro_cadastro = cadastro.query('colocacao ==3')
        if terceiro_cadastro.empty == True:
            terceiro_cadastro=mensagem_concorrencia
        else:
            terceiro_cadastro= terceiro_cadastro[['fornecedor']].to_string(header=False,index=False)

        primeiro_idg = idg.query('colocacao ==1')
        if primeiro_idg.empty == True:
            primeiro_idg=mensagem_concorrencia
        else:
            primeiro_idg= primeiro_idg[['fornecedor']].to_string(header=False,index=False)

        segundo_idg = idg.query('colocacao ==2')
        if segundo_idg.empty == True:
            segundo_idg=mensagem_concorrencia
        else:
            segundo_idg= segundo_idg[['fornecedor']].to_string(header=False,index=False)
        terceiro_idg = idg.query('colocacao ==3')
        if terceiro_idg.empty == True:
            terceiro_idg=mensagem_concorrencia
        else:
            terceiro_idg= terceiro_idg[['fornecedor']].to_string(header=False,index=False)

        primeiro_seguranca = seguranca.query('colocacao ==1')
        segundo_seguranca = seguranca.query('colocacao ==2')
        terceiro_seguranca = seguranca.query('colocacao ==3')

        context ={'referencia':referencia,'ref':ref,
            'primeiro_idg':primeiro_idg,
                'segundo_idg':segundo_idg,
                'terceiro_idg':terceiro_idg,
                'primeiro_arsesp':primeiro_arsesp,
                'segundo_arsesp':segundo_arsesp,
                'terceiro_arsesp':terceiro_arsesp,
                'primeiro_cadastro':primeiro_cadastro,
                'segundo_cadastro':segundo_cadastro,
                'terceiro_cadastro':terceiro_cadastro,
                'primeiro_seguranca':primeiro_seguranca[['fornecedor']].to_string(header=False,index=False),
                'segundo_seguranca':segundo_seguranca[['fornecedor']].to_string(header=False,index=False),
                'terceiro_seguranca':terceiro_seguranca[['fornecedor']].to_string(header=False,index=False),
                  }

        return render(request, 'core/melhores_interior.html',context)
    messages.error(request,'O Banco de Dados não tem Dados para o processamento!')
    return render(request, 'core/melhores_interior.html')
@has_permission_decorator('melhores')
def ranking(request):

    return render(request, 'core/ranking.html')
@has_permission_decorator('melhores')
def melhores_idg(request):
    referencia = tb_premio_excel.objects.values('mes_ref').filter(setor ='CAPITAL').order_by('-mes_ref').distinct()
    busca=request.POST.get('mes_ref')
    ref = tb_premio_excel.objects.values_list('mes_ref').order_by('-mes_ref').first()
    if (request.method=="POST") & (request.POST.get('mes_ref') != ''):

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'INDICE DE DESEMPENHO GLOBAL (IDG)') & Q(mes_ref= busca)& Q(setor= 'CAPITAL')))

        ref = request.POST.get('mes_ref')
    else:

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'INDICE DE DESEMPENHO GLOBAL (IDG)') & Q(mes_ref__in= ref) & Q(setor= 'CAPITAL')))

    context ={'cont_contratos':cont_contratos,
              'referencia':referencia,

              }

    return render(request, 'core/melhores_idg.html',context)
@has_permission_decorator('melhores')
def melhores_isap(request):
    referencia = tb_premio_excel.objects.values('mes_ref').order_by('-mes_ref').distinct()
    busca=request.POST.get('mes_ref')
    ref = tb_premio_excel.objects.values_list('mes_ref').order_by('-mes_ref').first()
    if (request.method=="POST") & (request.POST.get('mes_ref') != ''):

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'SERVIÇOS ATENDIDOS NO PRAZO (ISAP)') & Q(mes_ref= busca)& Q(setor= 'CAPITAL')))

        ref = request.POST.get('mes_ref')
    else:

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'SERVIÇOS ATENDIDOS NO PRAZO (ISAP)') & Q(mes_ref__in= ref)& Q(setor= 'CAPITAL')))

    context ={'cont_contratos':cont_contratos,
              'referencia':referencia,

              }
    return render(request, 'core/melhores_isap.html',context)
@has_permission_decorator('melhores')
def melhores_idr(request):
    referencia = tb_premio_excel.objects.values('mes_ref').order_by('-mes_ref').distinct()
    busca=request.POST.get('mes_ref')
    ref = tb_premio_excel.objects.values_list('mes_ref').order_by('-mes_ref').first()
    if (request.method=="POST") & (request.POST.get('mes_ref') != ''):

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'INDICE DE DESEMPENHO REPOSIÇÃO (IDR)') & Q(mes_ref= busca)& Q(setor= 'CAPITAL')))

        ref = request.POST.get('mes_ref')
    else:

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'INDICE DE DESEMPENHO REPOSIÇÃO (IDR)') & Q(mes_ref__in= ref) & Q(setor= 'CAPITAL')))

    context ={'cont_contratos':cont_contratos,
              'referencia':referencia,

              }
    return render(request, 'core/melhores_idr.html',context)
@has_permission_decorator('melhores')
def melhores_ida(request):
    referencia = tb_premio_excel.objects.values('mes_ref').order_by('-mes_ref').distinct()
    busca=request.POST.get('mes_ref')
    ref = tb_premio_excel.objects.values_list('mes_ref').order_by('-mes_ref').first()
    if (request.method=="POST") & (request.POST.get('mes_ref') != ''):

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'INDICE DE DESEMPENHO NA ÁGUA (IDA)') & Q(mes_ref= busca) & Q(setor= 'CAPITAL')))

        ref = request.POST.get('mes_ref')
    else:

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'INDICE DE DESEMPENHO NA ÁGUA (IDA)') & Q(mes_ref__in= ref) & Q(setor= 'CAPITAL')))

    context ={'cont_contratos':cont_contratos,
              'referencia':referencia,

              }
    return render(request, 'core/melhores_ida.html',context)
@has_permission_decorator('melhores')
def melhores_ide(request):
    referencia = tb_premio_excel.objects.values('mes_ref').order_by('-mes_ref').distinct()
    busca=request.POST.get('mes_ref')
    ref = tb_premio_excel.objects.values_list('mes_ref').order_by('-mes_ref').first()
    if (request.method=="POST") & (request.POST.get('mes_ref') != ''):

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'INDICE DE DESEMPENHO NA ESGOTO(IDE)') & Q(mes_ref= busca) & Q(setor= 'CAPITAL')))
        ref = request.POST.get('mes_ref')
    else:
        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'INDICE DE DESEMPENHO NA ESGOTO(IDE)') & Q(mes_ref__in= ref) & Q(setor= 'CAPITAL')))

    context ={'cont_contratos':cont_contratos,
              'referencia':referencia,

              }
    return render(request, 'core/melhores_ide.html',context)
@has_permission_decorator('melhores')
def melhores_capacitacao(request):
    referencia = tb_premio_excel.objects.values('mes_ref').order_by('-mes_ref').distinct()
    busca=request.POST.get('mes_ref')
    ref = tb_premio_excel.objects.values_list('mes_ref').order_by('-mes_ref').first()
    if (request.method=="POST") & (request.POST.get('mes_ref') != ''):

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'CAPACITAÇÃO DE EMPREGADOS') & Q(mes_ref= busca) & Q(setor= 'CAPITAL')))

        ref = request.POST.get('mes_ref')
    else:

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'CAPACITAÇÃO DE EMPREGADOS') & Q(mes_ref__in= ref) & Q(setor= 'CAPITAL')))

    context ={'cont_contratos':cont_contratos,
              'referencia':referencia,

              }
    return render(request, 'core/melhores_capacitacao.html',context)
@has_permission_decorator('melhores')
def melhores_comgas(request):
    referencia = tb_premio_excel.objects.values('mes_ref').order_by('-mes_ref').distinct()
    busca=request.POST.get('mes_ref')
    ref = tb_premio_excel.objects.values_list('mes_ref').order_by('-mes_ref').first()
    if (request.method=="POST") & (request.POST.get('mes_ref') != ''):

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'SINISTROS OPERACIONAIS (COMGAS)') & Q(mes_ref= busca) & Q(setor= 'CAPITAL')))

        ref = request.POST.get('mes_ref')
    else:
        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'SINISTROS OPERACIONAIS (COMGAS)') & Q(mes_ref__in= ref) & Q(setor= 'CAPITAL')))
    context ={'cont_contratos':cont_contratos,
              'referencia':referencia,
              }
    return render(request, 'core/melhores_comgas.html',context)
@has_permission_decorator('melhores')
def melhores_seguranca(request):
    referencia = tb_premio_excel.objects.values('mes_ref').order_by('-mes_ref').distinct()
    busca=request.POST.get('mes_ref')
    ref = tb_premio_excel.objects.values_list('mes_ref').order_by('-mes_ref').first()
    if (request.method=="POST") & (request.POST.get('mes_ref') != ''):

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'SEGURANÇA') & Q(mes_ref= busca) & Q(setor= 'CAPITAL')))

        ref = request.POST.get('mes_ref')
    else:
        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'SEGURANÇA') & Q(mes_ref__in= ref) & Q(setor= 'CAPITAL')))
    context ={'cont_contratos':cont_contratos,
              'referencia':referencia,
              }
    return render(request, 'core/melhores_seguranca.html',context)
@has_permission_decorator('melhores')
def melhores_cadastro(request):
    referencia = tb_premio_excel.objects.values('mes_ref').order_by('-mes_ref').distinct()
    busca=request.POST.get('mes_ref')
    ref = tb_premio_excel.objects.values_list('mes_ref').order_by('-mes_ref').first()
    if (request.method=="POST") & (request.POST.get('mes_ref') != ''):

        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'ENTREGA DO CADASTRO E IMOBILIZAÇÃO') & Q(mes_ref= busca) & Q(setor= 'CAPITAL')))

        ref = request.POST.get('mes_ref')
    else:
        cont_contratos = tb_premio_excel.objects.values('colocacao','contrato','fornecedor','gestores','mes_ref','indicador',
                                                        'indicador','casas_decimais','original','OS_fotos','serv_2_min').\
            filter(Q(Q(modalidade = 'ENTREGA DO CADASTRO E IMOBILIZAÇÃO') & Q(mes_ref__in= ref) & Q(setor= 'CAPITAL')))
    context ={'cont_contratos':cont_contratos,
              'referencia':referencia,
              }
    return render(request, 'core/melhores_cadastro.html',context)

