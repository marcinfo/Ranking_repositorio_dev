# Generated by Django 4.2.4 on 2023-11-01 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_tb_referencia_contrato_administrador_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tb_referencia_contrato',
            name='unidade',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='tb_referencia_contrato',
            name='mes_ano_referencia',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]