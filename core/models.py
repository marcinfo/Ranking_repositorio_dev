from django.conf import settings
from django.db import models
from stdimage import StdImageField

def crialista():
    global lista_praga, lista_cultura
    lista_praga = TbCadastro_pragas.objects.select_related('nome_comum').values_list('nome_comum', 'nome_comum')
    lista_cultura = TbCadastro_culturas.objects.select_related('cultura').values_list('cultura', 'cultura')
    return
pass

CONTROLE_CHOICE=(
    ("Controlada",'Controlada'),
    ("Fora de Controle","Fora de Controle"),
)
hora_envio_email=(('0','00'),('1','01'))
class Base(models.Model):
    inserido = models.DateTimeField(verbose_name="Inserido em:", auto_now_add=True, null=True)
    atualizado = models.DateTimeField(verbose_name="Atualizado em:", auto_now=True, null=True)
    ativo = models.BooleanField('Ativo?', default=True )
    class Meta:
        abstract = True
class Profile(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='user_id')

    notificacoes = models.BooleanField('Receber Notificações?', default=True)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)
    class Meta:
        verbose_name = "Tabela de Perfil"
        verbose_name_plural = "Tabela de Perfis"
    def __str__(self):
        return f'Profile for user {self.user.username}'

class TbPragas(models.Model):
    id_praga = models.AutoField(primary_key=True)
    cultura = models.CharField(max_length=45, blank=True, null=True)
    especie = models.CharField(max_length=45, blank=True, null=True)
    nome_comum = models.CharField(max_length=45, blank=True, null=True)
    nome_comum2 = models.CharField(max_length=48, blank=True, null=True)
    class Meta:
        verbose_name = "Tabela de Praga"
        verbose_name_plural = "Tabela de Pragas"



class TbCadastro_pragas(models.Model):
    id= models.AutoField(primary_key=True)
    especie = models.CharField(max_length=45, unique=True)
    nome_comum = models.CharField(max_length=45, unique=True)
    class Meta:
        verbose_name = "Tabela Cadastro de Praga"
        verbose_name_plural = "Tabela de cadastro de Pragas"

class TbCadastro_culturas(models.Model):
    id= models.AutoField(primary_key=True)
    cultura = models.CharField(max_length=45, unique=True)
    nome_comum = models.CharField(max_length=45, unique=True)
    class Meta:
        verbose_name = "Tabela Cadastro de Cultura"
        verbose_name_plural = "Tabela de cadastro de Culturas"

#lista_praga = TbCadastro_pragas.objects.select_related('nome_comum').values_list('nome_comum', 'nome_comum')
#lista_cultura = TbCadastro_culturas.objects.select_related('cultura').values_list('cultura', 'cultura')



class Tb_Registros(Base):
    crialista()
    id_ocorrencia = models.AutoField(primary_key=True)
    usuario =  models.CharField(max_length=45,editable=False)
    praga = models.CharField(max_length=40,choices=lista_praga,help_text='Selecione qual o tipo de praga esta contaminando.')
    cultura =  models.CharField(verbose_name='Cultura',max_length=48,choices=lista_cultura,
                                help_text='Qual plantação foi contaminada?')
    status = models.CharField(verbose_name='A Praga Esta Controlada?', max_length=45, choices=CONTROLE_CHOICE,help_text='A praga esta controlada?')
    nome_propriedade = models.CharField(verbose_name='Nome da Propriedade:',max_length=60,
                                        help_text='Nome da propriedade que esta sendo contaminada.',null=True,blank=True)
    prejuizo=models.DecimalField(verbose_name='Total do prejuizo R$',max_digits=20, decimal_places=2,default=0.0,help_text='qual o valor do prejuizo?')
    hectares=models.IntegerField(verbose_name='Quantidade de hectar afetado',default=0,help_text='quantos hectares estão contaminados')
    latitude = models.CharField(max_length=45)
    longitude = models.CharField(max_length=45)
    city = models.CharField(max_length=45,null=True,blank=True)
    state = models.CharField(max_length=45,null=True,blank=True)
    country = models.CharField(max_length=45,null=True,blank=True)
    imagem = StdImageField('Imagem',upload_to='images',null=True,blank=False,
                           variations={'thumbnail': {"width": 300, "height": 400, "crop": True}})
    observacao = models.CharField(max_length=200,verbose_name='Observações',blank=True)
    class Meta:
        verbose_name = "Tabela de Registro"
        verbose_name_plural = "Tabela de Registros"

    def __str__(self):
        return self.usuario



class TbParametros(models.Model):
    id= models.AutoField(primary_key=True)
    ativa_email = models.BooleanField('Enviar email?', default=False)
    hora_envio = models.CharField(max_length=2,choices=hora_envio_email,verbose_name='Horario para envio do e-mail',null=True,blank=True )

    class Meta:
        verbose_name = "Tabela Cadastro de Parametro"
        verbose_name_plural = "Tabela de cadastro de Parametros"


