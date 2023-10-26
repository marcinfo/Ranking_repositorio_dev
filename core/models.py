from django.conf import settings
from django.db import models
from stdimage import StdImageField



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



