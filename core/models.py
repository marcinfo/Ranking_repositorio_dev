from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

escolhe_M_R=(

    ("I","Interior"),("L",'Litoral'),("M",'Metropolitana'),
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
    r_m = models.CharField(max_length= 1,choices=escolhe_M_R,verbose_name="Diretoria:")
    inserido = models.DateTimeField(verbose_name="Inserido em:", auto_now_add=True)
    cadastrado_por = models.CharField(max_length= 100, blank=False, null=False)
    unidade = models.CharField(max_length= 100, blank=True, null=True)
    numemro_contrato = models.CharField(max_length= 10,verbose_name='Número do Contrato:', unique=True )
    nome_contratada =  models.CharField(max_length= 100, blank=False, null=False)
    administrador = models.CharField(max_length= 100, blank=False, null=False)
    superintendente = models.CharField(max_length= 100, blank=False, null=False)
    data_inicio = models.DateField(blank=False, null=False)
    data_fim = models.DateField(blank=False, null=False)
    staff_1 = models.CharField(max_length= 100, blank=False, null=False)
    staff_2 = models.CharField(max_length= 100, blank=False, null=False)
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
    idg_interior = models.DecimalField(help_text='INDICE DE DESEMPENHO GLOBAL (IDG)',max_digits=4,decimal_places=2,
                                       blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    servicos_arsesp = models.DecimalField(help_text='SERVIÇOS ATENDIDOS NO PRAZO ARSESP',max_digits=4,decimal_places=2,
                                   blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    entrega_cadastro = models.DecimalField(help_text='ENTREGA DO CADASTRO E IMOBILIZAÇÃO',max_digits=4,decimal_places=2,
                                   blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    acidente_trabalho = models.IntegerField(help_text='ACIDENTE DE TRABALHO (Quantidade)',blank=False,null=False,
                                            validators=[MinValueValidator(0),MaxValueValidator(100)])
    justificativa = models.TextField(max_length=500, help_text='Justifique os indicadores informados.',blank=False)
    class Meta:
        verbose_name = "Tabela de Indicador Contrato Interior"
        verbose_name_plural = "Tabela de Indicadores Contratos Interior"

class tb_modalidade_litoral(Base):
    id = models.AutoField(primary_key=True)
    mes_ano_referencia = models.CharField(max_length=20)
    inserido_por = models.CharField(max_length= 100, blank=False, null=False)
    contrato = models.CharField(max_length=20)
    idg_interior = models.DecimalField(help_text='INDICE DE DESEMPENHO GLOBAL (IDG)',max_digits=4,decimal_places=2,
                                       blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    servicos_arsesp = models.DecimalField(help_text='SERVIÇOS ATENDIDOS NO PRAZO ARSESP',max_digits=4,decimal_places=2,
                                   blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    entrega_cadastro = models.DecimalField(help_text='ENTREGA DO CADASTRO E IMOBILIZAÇÃO',max_digits=4,decimal_places=2,
                                   blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    acidente_trabalho = models.IntegerField(help_text='ACIDENTE DE TRABALHO (Quantidade)',blank=False,null=False,
                                            validators=[MinValueValidator(0),MaxValueValidator(100)])
    justificativa = models.TextField(max_length=500, help_text='Justifique os indicadores informados.',blank=False)
    class Meta:
        verbose_name = "Tabela de Indicador Contrato Litoral"
        verbose_name_plural = "Tabela de Indicadores Contratos Litoral"

class tb_modalidade_metropolitana(Base):
    id = models.AutoField(primary_key=True)
    mes_ano_referencia = models.CharField(max_length=20)
    inserido_por = models.CharField(max_length= 100, blank=False, null=False)
    contrato = models.CharField(max_length=20)
    idg = models.DecimalField(help_text='INDICE DE DESEMPENHO GLOBAL (IDG)',max_digits=5,decimal_places=2,
                                       blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    isap = models.DecimalField(help_text='SERVIÇOS ATENDIDOS NO PRAZO (ISAP)',max_digits=5,decimal_places=2,
                                   blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    ida = models.DecimalField(help_text='INDICE DE DESEMPENHO NA ÁGUA (IDA)',max_digits=5,decimal_places=2,
                                   blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    ide = models.DecimalField(help_text='INDICE DE DESEMPENHO NA ESGOTO(IDE)',max_digits=5,decimal_places=2,
                                   blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    idr = models.DecimalField(help_text='INDICE DE DESEMPENHO REPOSIÇÃO (IDR)',max_digits=5,decimal_places=2,
                               blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    entrega_cadastro = models.DecimalField(help_text='ENTREGA DO CADASTRO E IMOBILIZAÇÃO',max_digits=5,decimal_places=2,
                               blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    seg_capacitacao = models.DecimalField(verbose_name='SEGURANÇA E CAPACITAÇÃO',max_digits=5,decimal_places=2,
                           blank=False,null=False,validators=[MinValueValidator(0),MaxValueValidator(100)])
    justificativa = models.TextField(max_length=500, verbose_name='Justifique os indicadores informados.',blank=False)
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
    resp_preenchimento = models.CharField(max_length= 100, blank=True, null=False)
    mes_ano_referencia = models.CharField(max_length=20, blank=True, null=False)
    contrato = models.CharField(max_length=20, blank=True, null=False)
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
