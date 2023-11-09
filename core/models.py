
from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django import forms
escolhe_M_R=(

    ("Interior/Litoral","Interior/Litoral"),("M",'Metropolitana'),
)
hora_envio_email=(('0','00'),('1','01'))
escolha_status=(('SIM','SIM'),('NÃO','NÃO'))
class Base(models.Model):
    inserido = models.DateTimeField(verbose_name="Inserido em:", auto_now_add=True, null=True)
    atualizado = models.DateTimeField(verbose_name="Atualizado em:", auto_now=True, null=True)
    ativo = models.CharField('Ativo?', default='SIM',choices=escolha_status,max_length=3 )
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
        class Meta:
            verbose_name = "Tabela Cadastro de Cultura"
            verbose_name_plural = "Tabela de cadastro de Culturas"

class tb_log_email(models.Model):
    inserido = models.DateTimeField(verbose_name="Inserido em:", auto_now_add=True)
    inicio_envio = models.CharField(max_length=35 , verbose_name='Inicio do envio do e-mail')
    fim_envio = models.CharField(max_length=35, verbose_name='Fim do envio do e-mail')
    total_enderecos = models.CharField(max_length=35, verbose_name='Quantidade de endereços selecionados')
    total_de_envio = models.CharField(max_length=35, verbose_name='Quantidade de emails enviados')
    tempo_envio = models.CharField(max_length=9, verbose_name='tempo de execução',null=True,blank=True)
    status_tarefa = models.CharField(max_length=35, verbose_name='Status da tarefa')
    class Meta:
        verbose_name = "Tabela log de emil"
        verbose_name_plural = "Tabela log de emils"
class tb_dados_contrato(Base):
    id = models.AutoField(primary_key=True)
    r_m = models.CharField(max_length= 20,choices=escolhe_M_R,verbose_name="Metropolitana/Interior")
    inserido = models.DateTimeField(verbose_name="Inserido em", auto_now_add=True)
    cadastrado_por = models.CharField(verbose_name="Cadastrado Por",max_length= 100, blank=False, null=False)
    unidade = models.CharField(verbose_name="Inserido em",max_length= 10, blank=False, null=False)
    numemro_contrato = models.CharField(verbose_name="Número do Contrato",max_length= 10, blank=False, null=False, unique=True)
    nome_contratada =  models.CharField(verbose_name="Nome da Contratada",max_length= 100, blank=False, null=False)
    administrador = models.CharField(verbose_name="Responsavel da Contratada",max_length= 100, blank=False, null=False)
    superintendente = models.CharField(verbose_name="Surperintendente",max_length= 100, blank=False, null=False)
    data_inicio = models.DateField(verbose_name="Data de Inicio do Contrato",blank=False, null=False,)
    data_fim = models.DateField(verbose_name="Data de Fim do Contrato",blank=False, null=False)

    staff_1 = models.CharField(max_length= 100, blank=False, null=False)
    staff_2 = models.CharField(max_length= 100, blank=False, null=False,)

    def __str__(self):
        return self.numemro_contrato
    class Meta:
        verbose_name = "Tabela Dados do Contrato"
        verbose_name_plural = "Tabela Dados dos Contratos"
class tb_modalidade_interior(Base):
    id = models.AutoField(primary_key=True)
    mes_ano_referencia = models.CharField(max_length=20)
    inserido_por = models.CharField(max_length= 100, blank=False, null=False)
    contrato = models.CharField(max_length=20)
    idg_interior = models.DecimalField(help_text='Índice de Desempenho Global',max_digits=5,decimal_places=2,
                                       blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    servicos_arsesp = models.DecimalField(help_text='Serviços Atendidos No Prazo ARSESP',max_digits=5,decimal_places=2,
                                   blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    total_redes = models.DecimalField(help_text='Total de Redes executadas.',decimal_places=2,max_digits=7,
                               blank=False,null=False)
    total_cadastro_entregue = models.DecimalField(help_text='Total de CADASTRO entregue.',decimal_places=2,max_digits=7,
                               blank=False,null=False)
    entrega_cadastro = models.DecimalField(help_text='Entrega do Cadastro E Imobilização',max_digits=5,decimal_places=2,
                                   blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    quantidade_colaboradores = models.IntegerField(verbose_name='Quantidade de colaboradores',
                                                   help_text='quantidade de colaboradores no contrato',
                                                   null=False,blank=False)
    quantidade_acidentes = models.IntegerField(help_text='Quantidade de acidentes',verbose_name='Quantidade de acidentes',
                                               null=False,blank=False)
    acidente_trabalho = models.DecimalField(null=False,blank=False,max_digits=5,decimal_places=2,help_text='indicador de acidentes')
    justificativa = models.TextField(max_length=500,blank=True)
    class Meta:
        verbose_name = "Tabela de Indicador Contrato Interior"
        verbose_name_plural = "Tabela de Indicadores Contratos Interior"
class tb_modalidade_metropolitana(Base):
    id = models.AutoField(primary_key=True)
    mes_ano_referencia = models.CharField(max_length=20,editable=False)
    inserido_por = models.CharField(max_length= 100, blank=False, null=False,editable=False)
    contrato = models.CharField(max_length=20)
    idg = models.DecimalField(help_text='INDICE DE DESEMPENHO GLOBAL ',max_digits=5,decimal_places=2,
                                       blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    isap = models.DecimalField(help_text='SERVIÇOS ATENDIDOS NO PRAZO (ISAP)',max_digits=5,decimal_places=2,
                                   blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    ida = models.DecimalField(help_text='INDICE DE DESEMPENHO NA ÁGUA (IDA)',max_digits=5,decimal_places=2,
                                   blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    ide = models.DecimalField(help_text='INDICE DE DESEMPENHO NA ESGOTO(IDE)',max_digits=5,decimal_places=2,
                                   blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    idr = models.DecimalField(help_text='INDICE DE DESEMPENHO REPOSIÇÃO (IDR)',max_digits=5,decimal_places=2,
                               blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    total_redes = models.DecimalField(verbose_name='Metros de rede executadas',help_text='Total de Redes executadas em metros.',decimal_places=2,max_digits=7,
                               blank=False,null=False)
    total_cadastro_entregue = models.DecimalField(help_text='Total de CADASTRO entregue.',decimal_places=2,max_digits=7,
                               blank=False,null=False)

    entrega_cadastro = models.DecimalField(help_text='ENTREGA DO CADASTRO E IMOBILIZAÇÃO',max_digits=5,decimal_places=2,
                               blank=False,null=False)
    quantidade_colaboradores = models.IntegerField(verbose_name='Quantidade de colaboradores',
                                                   help_text='quantidade de colaboradores no contrato',
                                                   null=False,blank=False)
    quantidade_acidentes = models.IntegerField(help_text='Quantidade de acidentes',verbose_name='Quantidade de acidentes',
                                               null=False,blank=False)

    seg_capacitacao = models.DecimalField(verbose_name='SEGURANÇA E CAPACITAÇÃO',max_digits=5,decimal_places=2,
                           blank=True,null=True,validators=[MinValueValidator(0),MaxValueValidator(100)])
    justificativa = models.TextField(max_length=500, verbose_name='Justifique os indicadores informados.',blank=True)
    class Meta:
        verbose_name = "Tabela de Indicador Contrato Metropolitana"
        verbose_name_plural = "Tabela de Indicadores Contratos Metropolitana"

class tb_unidades(Base):
    id = models.AutoField(primary_key=True)
    inserido = models.DateTimeField(verbose_name="Inserido em:", auto_now_add=True)
    inserido_por = models.CharField(max_length= 100, blank=False, null=False)
    num_unidade = models.IntegerField(unique=True)
    sigla_unidade  = models.CharField(max_length= 10,unique=True, blank=False, null=False)
    nome_unidade  = models.CharField(max_length= 100,unique=True, blank=False, null=False)
    superintendente = models.CharField(max_length= 100, blank=False, null=False)
    def __str__(self):
        return self.sigla_unidade
    class Meta:
        verbose_name = "Tabela de Unidade"
        verbose_name_plural = "Tabela de Unidades"

class tb_referencia_contrato(Base):
    id = models.AutoField(primary_key=True)
    resp_preenchimento = models.CharField(max_length= 100, blank=False, null=False)
    mes_ano_referencia = models.CharField(max_length=100, blank=True, null=False)
    unidade = models.CharField(max_length=20, blank=True, null=True)
    contrato = models.CharField(max_length=20, blank=True, null=False)
    administrador = models.CharField(max_length= 100, blank=True, null=True)
    superintendente = models.CharField(max_length= 100, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=False)
    data_hora_preenchimento = models.CharField(max_length=20, blank=True, null=False)
    staf_1 = models.CharField(max_length=20, blank=True, null=False)
    staf_2 = models.CharField(max_length=20, blank=True, null=False)
    data_inicio = models.DateField(blank=True, null=True)
    data_fim = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.mes_ano_referencia
    class Meta:
        verbose_name = "Tabela Mês/Ano Referencia"
        verbose_name_plural = "Tabela Mês/Ano Referencias"
