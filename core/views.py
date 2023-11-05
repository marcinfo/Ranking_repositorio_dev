
import pandas as pd
import plotly.express as px
import locale
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
    tb_modalidade_interior
from django.conf import settings

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
def verifica_validade_contrato():
        valida_contrato = tb_dados_contrato.objects.\
        values_list('numemro_contrato','administrador','unidade', 'superintendente','data_inicio','data_fim').\
        filter(Q(Q(ativo = True) & Q(data_fim__lte = date.today())))
        for valida in valida_contrato:
            tb_dados_contrato.objects.update(ativo = 'False')
            print(valida_contrato)

def gerar_mes_referencia():
    verifica_validade_contrato()
    data=date.today() - relativedelta(months=1)
    mes_ano_format=data.strftime("%B/%Y")
    lista_contratos = tb_dados_contrato.objects.\
        values_list('numemro_contrato','administrador','unidade', 'superintendente','staff_1','staff_1').\
        filter(Q(Q(ativo = True) & Q(data_fim__gte = date.today()) & Q(data_inicio__lte = date.today())))
    if lista_contratos.count != 0:

        for cont in lista_contratos:
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
def atulizar_localizacao():
    pass

def index(request):

    #verifica_validade_contrato()
    gerar_mes_referencia()
    return render(request, 'core/index.html')
@login_required
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

@login_required
def indicadores_M(request):

    mes_ano_ref = tb_referencia_contrato.objects.all().order_by('-id').filter(status='ABERTO').first()
    messages.warning(request, f'ATENÇÃO! Referência {mes_ano_ref}, '
                           f'para Indicadores não utilizados no contrato preencher com 0 (zero). '
                           f'Revise as informações antes de CLICAR/ENTER no botão SALVAR. Após SALVAR NÃO será possivel'
                           f' corrigir.')
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
            messages.warning(request,'Não Autorizado')
        context = {

            'form':form
        }
        return render(request, 'core/indicadores_M.html',context=context)
def indicadores_R(request):
    mes_ano_ref = tb_referencia_contrato.objects.all().order_by('-id').filter(status='ABERTO').first()
    messages.warning(request, f'ATENÇÃO! Referência {mes_ano_ref}, '
                           f'para Indicadores não utilizados no contrato preencher com 0 (zero). '
                           f'Revise as informações antes de CLICAR/ENTER no botão SALVAR. Após SALVAR NÃO será possivel'
                           f' corrigir.')
    if request.method == "GET":
        form=informar_indicador_RForm()
        context={
            'form': form
        }
        return render(request, 'core/indicadores_R.html',context=context)
    else:
        form = informar_indicador_RForm(request.POST, request.FILES)
        if form.is_valid():
            indicadorR = form.save(commit=False)
            indicadorR.inserido_por = request.user
            indicadorR.mes_ano_referencia = mes_ano_ref
            indicadorR.acidente_trabalho = (indicadorR.quantidade_acidentes/indicadorR.quantidade_colaboradores)*100
            contrato_autorizado = tb_dados_contrato.objects.values('numemro_contrato').\
                filter((Q(Q(numemro_contrato=indicadorR.contrato)) & (Q(staff_1=request.user) | Q(staff_2=request.user)))).first()
            contrato_autorizado=str(contrato_autorizado)
            print(contrato_autorizado)
            print(indicadorR.contrato)
            if indicadorR.contrato in contrato_autorizado :
                indicadorR = form.save()
                messages.success(request, f'Indicador do Contrato {indicadorR.contrato} '
                                          f'foi cadastrado com Sucesso!')
                form = informar_indicador_RForm()
                tb_referencia_contrato.objects.filter(Q(Q(contrato=indicadorR.contrato) &
                                        Q(mes_ano_referencia=indicadorR.mes_ano_referencia))).\
                    update(status='INFORMADO',resp_preenchimento=indicadorR.inserido_por)

                print(indicadorR.contrato)
            else:
                pass
                messages.error(request,f'Você não tem permissão para informar indicadores '
                                       f'para o contrato {indicadorR.contrato}! Verifique o número do CONTRATO ou'
                                       f' revise o CADASTRO. ')
        else:
            pass
            messages.error(request,'Verifique o preenchimento!')
        context = {

            'form':form
        }
        return render(request, 'core/indicadores_R.html',context=context)

@login_required
def informar_indice(request):

        return render(request, 'core/indicadores_M.html')

@login_required
def processar(request):
    gerar_mes_referencia()
    return render(request, 'core/processar.html')


@login_required
def menu_indices(request):

    return render(request, 'core/menu_indices.html')
@login_required
def menu_contratos(request):

    return render(request, 'core/menu_contratos.html')

def erro_400(request,exception):
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


def selecionar(self):
    r=tb_referencia_contrato.objects.all()
    return r

