import folium
import pandas as pd
import plotly.express as px
import smtplib
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
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from geopy import distance
from geopy.geocoders import Nominatim
from .forms import LoginForm, UserRegistrationForm, \
    UserEditForm, ProfileEditForm, RegistrosModelForm
from .models import Profile, Tb_Registros,TbCadastro_culturas,TbCadastro_pragas,TbParametros
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
                    return HttpResponse('Authenticated ' \
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
def index(request):

    registros = Tb_Registros.objects.select_related('usuario').all().filter(ativo=True).values()
    contador =registros.count()
    if contador != 0:
        praga_afetada = Tb_Registros.objects.values('praga').annotate(total=Count('praga')).order_by("-total")
        status_conta = Tb_Registros.objects.values('status').annotate(total=Count('praga')).order_by("-total")
        dados = pd.DataFrame(registros)
        reg_ocorrencias = pd.DataFrame(registros)
        total=reg_ocorrencias['id_ocorrencia'].count()
        total_prejuizo = reg_ocorrencias['prejuizo'].sum()
        total_hectares = reg_ocorrencias['hectares'].sum()
        tipo_praga=reg_ocorrencias.groupby('praga')['praga'].unique().count()
        tipo_cultura = reg_ocorrencias.groupby('cultura')['cultura'].unique().count()
        config={'displayModeBar':False}
        fonte_titulo='Times New Roman'
        largura= 400
        altura=200
        graf_grupo_cultura = px.histogram(registros , x=['praga'],
                      height=altura,width=largura,template='simple_white',color_discrete_sequence=['#66CDAA'])
        graf_grupo_cultura.update_layout(title={'text':'Ocorrências de Pragas.','font':{'size':16}}, title_font_family=fonte_titulo,
                                         title_font_color='darkgrey',title_y=0.9,title_x=0.5)
        graf_grupo_cultura.update_layout(title_font_family='classic-roman',font_color='grey',showlegend=False,
                                         yaxis_title={'text':'ocorrências','font':{'size':12}},
                                         xaxis_title={'text': 'praga', 'font': {'size': 12}})
        chart_graf_grupo_cultura = graf_grupo_cultura.to_html(config = config)

        graf_grupo_praga = px.histogram(registros, x=['cultura'],
                      height=altura,width=largura,template='simple_white',color_discrete_sequence=['#66CDAA'])
        graf_grupo_praga.update_layout(title={'text':'Cultura Atacada.','font':{'size':16}}, title_font_family=fonte_titulo,
                                         title_font_color='darkgrey',title_y=0.9,title_x=0.5)
        graf_grupo_praga.update_layout(title_font_family='classic-roman',font_color='grey',showlegend=False,
                                         yaxis_title={'text':'ocorrências','font':{'size':12}},
                                         xaxis_title={'text': 'cultura', 'font': {'size': 12}})
        chart_graf_grupo_praga = graf_grupo_praga.to_html(config = config)
        graf_grupo_status= px.pie(status_conta, values='total', names='status',height=320,width=320, hole=.6)
        graf_grupo_status.update_layout(title={'text':'Status das Pragas.','font':{'size':16}}, title_font_family=fonte_titulo,
                                         title_font_color='darkgrey',title_y=0.9,title_x=0.5)
        graf_grupo_status.update_layout(title_font_family='classic-roman',font_color='grey',showlegend=True,
                                         yaxis_title={'text':'total','font':{'size':12}},
                                         xaxis_title={'text': 'status', 'font': {'size': 12}})
        chart_graf_grupo_status = graf_grupo_status.to_html(config = config)
        graf_grupo_praga_prejuizo= px.histogram(dados, x=dados['praga'], y=dados['prejuizo'].astype(float),
                      height=altura,width=largura,template='simple_white',color_discrete_sequence=['#66CDAA'])
        graf_grupo_praga_prejuizo.update_layout(title={'text':'Prejuizo por Praga.','font':{'size':16}}, title_font_family=fonte_titulo,
                                         title_font_color='darkgrey',title_y=0.9,title_x=0.5)
        graf_grupo_praga_prejuizo.update_layout(title_font_family='classic-roman',font_color='grey',showlegend=False,
                                         yaxis_title={'text':'R$','font':{'size':12}},
                                         xaxis_title={'text': 'praga', 'font': {'size': 12}})
        chart_graf_grupo_praga_prejuizo = graf_grupo_praga_prejuizo.to_html(config = config)
        graf_grupo_cultura_prejuizo= px.histogram(dados, x=dados['cultura'], y=dados['prejuizo'].astype(float),
                      height=altura,width=largura,template='simple_white',color_discrete_sequence=['#66CDAA'])
        graf_grupo_cultura_prejuizo.update_layout(title={'text':'Prejuizo por Cultura.','font':{'size':16}}, title_font_family=fonte_titulo,
                                         title_font_color='darkgrey',title_y=0.9,title_x=0.5)
        graf_grupo_cultura_prejuizo.update_layout(title_font_family='classic-roman',font_color='grey',showlegend=False,
                                         yaxis_title={'text':'R$','font':{'size':12}},
                                         xaxis_title={'text': 'cultura', 'font': {'size': 12}})
        chart_graf_grupo_cultura_prejuizo = graf_grupo_cultura_prejuizo.to_html(config = config)
        graf_grupo_hectar_prejuizo= px.histogram(registros,  y=['prejuizo'],
                      height=altura,width=largura,template='simple_white',color_discrete_sequence=['Purple'])
        graf_grupo_hectar_prejuizo.update_layout(title={'text':'Prejuizo por hectar.','font':{'size':16}}, title_font_family=fonte_titulo,
                                         title_font_color='darkgrey',title_y=0.9,title_x=0.5)
        graf_grupo_hectar_prejuizo.update_layout(title_font_family='classic-roman',font_color='grey',showlegend=False,
                                         yaxis_title={'text':'R$','font':{'size':12}},
                                         xaxis_title={'text': 'hectares', 'font': {'size': 12}})
        graf_grupo_hectar_prejuizo = graf_grupo_hectar_prejuizo.to_html(config = config)
        context = {
            'total': total, 'total_prejuizo': total_prejuizo, 'tipo_praga': tipo_praga,'total_hectares': total_hectares,
            'praga_afetada':praga_afetada,'tipo_cultura': tipo_cultura,'chart_graf_grupo_cultura':chart_graf_grupo_cultura,
            'chart_graf_grupo_praga':chart_graf_grupo_praga,'chart_graf_grupo_status':chart_graf_grupo_status,
            'chart_graf_grupo_praga_prejuizo':chart_graf_grupo_praga_prejuizo,
            'chart_graf_grupo_cultura_prejuizo':chart_graf_grupo_cultura_prejuizo,
            'graf_grupo_hectar_prejuizo':graf_grupo_hectar_prejuizo,
        }
        return render(request, 'core/index.html',context)
    else:
        print(contador)
        messages.info(request,'Não existem informações para exibir!')
        return render(request, 'core/index.html')





@login_required
def cadastrarForm(request):
    geolocator = Nominatim(user_agent="geoapiExercises")
    if request.method == "GET":
        form=RegistrosModelForm()
        context={
            'form': form
        }
        return render(request, 'core/cadastrar.html',context=context)
    else:
        form = RegistrosModelForm(request.POST, request.FILES)
        if form.is_valid():
            regitro = form.save(commit=False)
            regitro.usuario = request.user

            Latitude = regitro.latitude
            Longitude = regitro.longitude

            location = geolocator.reverse(Latitude + "," + Longitude)
            address = location.raw['address']
            city = address.get('city', '')
            state = address.get('state', '')
            country = address.get('country', '')
            code = address.get('country_code')
            zipcode = address.get('postcode')
            print('City : ', city)
            print('State : ', state)
            print('Country : ', country)
            print('Zip Code : ', zipcode)
            regitro = form.save()

            messages.info(request, 'Ocorrência Cadastrada com Sucesso!')

            form = RegistrosModelForm()
            #enviar_email_backend()
            enviar_email()
        context = {
            'form':form
        }
        #enviar_email()
        return render(request, 'core/cadastrar.html', context=context)

@login_required
def mostra_ocorrencia(request):
    registros = Tb_Registros.objects.all().values()
    contador =registros.count()
    if contador != 0:
        l1 = " -15.793889"
        l2 = " -47.882778"
        lat_get = request.GET.get('lat')
        lon_get = request.GET.get('lon')
        zoom = 4
        loc_usuario = 'centralizado em Brasilia.'
        if (lat_get != None) & (lon_get != None):
            latitude = str(lat_get)
            longitude = str(lon_get)
            l1 = latitude
            l2 = longitude
            zoom = 9
            loc_usuario='Você esta aqui!'
        else:
            l1 = l1
            l2 = l2
        ocorrencias = Tb_Registros.objects.all().values()
        geo_loc_ocorrencias = pd.DataFrame(ocorrencias)
        lista_distancia = []
        for _, dis in geo_loc_ocorrencias.iterrows():
            distan = distance.distance((l1, l2), [float(dis['latitude']), dis['longitude']]).km
            distan = float(distan)
            distan = round(distan,1)
            lista_distancia += [distan]
        geo_loc_ocorrencias['distancia'] = lista_distancia
        geo_loc_ocorrencias = geo_loc_ocorrencias.nsmallest(100, 'distancia')
        geo_loc_ocorrencias['poupup']= ' data '+geo_loc_ocorrencias['inserido'].map(str)+' '+geo_loc_ocorrencias['praga']+ \
                          ' '+geo_loc_ocorrencias['observacao']+ ' distancia=  '+geo_loc_ocorrencias['distancia'].map(str) +'km'

        m = folium.Map(location=[l1, l2], zoom_start=zoom, control_scale=True, width=1090, height=450)
        folium.Marker(location=[float(l1), float(l2)]).add_to(m)
        for _, ocor  in geo_loc_ocorrencias.iterrows():

            folium.Marker(
                location=[ocor['latitude'], ocor['longitude']], popup=ocor['poupup'],
            ).add_to(m)
        folium.Marker(
            location=[l1, l2], popup=loc_usuario, icon=folium.Icon(color='green', icon='ok-circle'), ).add_to(m)
        context = {
            'vacin': 'Veja as ocorrencias mais proximas da sua localização.',
            'm': m._repr_html_()
        }
        return render(request, 'core/mapa.html',context)

    else:

        messages.info(request,'Não existem informações para exibir!')
        return render(request, 'core/mapa.html')


@login_required
def mostra_tabela(request):
    registros = Tb_Registros.objects.all().values()
    contador = registros.count()
    if contador != 0:
        registros = Tb_Registros.objects.select_related('usuario').filter(ativo=True).\
            values('id_ocorrencia','inserido','nome_propriedade','cultura','praga','hectares','prejuizo','status','imagem','observacao')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:

            registros = registros.filter(
                inserido__date__range=[start_date,end_date]
            )
        tabela_paginator = Paginator(registros, 5)
        page_num = request.GET.get('page')
        page = tabela_paginator.get_page((page_num))

        context = {
            'page': page }
        return render(request, 'core/ocorrencias.html', context)
    else:

        messages.info(request,'Não existem informações para exibir!')
        return render(request, 'core/ocorrencias.html')
@login_required
def visualizar_imagem(request,pk):
    registro = Tb_Registros.objects.select_related('usuario').filter(ativo=True, id_ocorrencia=pk).\
        values('id_ocorrencia','inserido','nome_propriedade','cultura','praga','hectares','prejuizo',
               'status','imagem','observacao')
    print(registro)
    context = {
        'registro': registro }
    return render(request, 'core/visualizar_imagem.html',context)

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

def crialista():
    global lista_praga, lista_cultura
    lista_praga = TbCadastro_pragas.objects.select_related('nome_comum').values_list('nome_comum', 'nome_comum')
    lista_cultura = TbCadastro_culturas.objects.select_related('cultura').values_list('cultura', 'cultura')
    return
pass
crialista()

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
    email_usuario = User.objects.values('first_name','email').filter(is_active=True)

    host = config('EMAIL_HOST')
    port = config('EMAIL_PORT')
    login = config('EMAIL_HOST_USER')
    senha = config('EMAIL_HOST_PASSWORD')
    server = smtplib.SMTP(host, port)

    server.ehlo()
    server.starttls()

    server.login(login, senha)
    conta_email = 0
    for email_cad in email_usuario:

        enviado = email_cad['email']
        nome = email_cad['first_name']
        corpo = f"<b color='#1C1C1C'>Olá, {nome}. <br>Uma nova ocorrência de PRAGA foi cadastrada, para mais informações acesse \
          o sistema de <a href='https://monitordepragasonline.onrender.com/'>Monitormento</a> online.</br></b>"

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





