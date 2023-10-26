
import pandas as pd
import plotly.express as px
import smtplib
from datetime import datetime
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

from django.http import HttpResponse
from django.shortcuts import render

from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile
from django.conf import settings


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


        return render(request, 'core/index.html')




@login_required
def cadastrarForm(request):


        return render(request, 'core/informar_indice.html')

@login_required
def mostra_ocorrencia(request):

        return render(request, 'core/processar.html')


@login_required
def mostra_tabela(request):

        return render(request, 'core/visualizar_indices.html')
@login_required
def visualizar_imagem(request,pk):

    return render(request, 'core/visualizar_imagem.html')

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




