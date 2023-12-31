import requests
from django import forms
from django.contrib.auth.models import User
from .models import Profile,tb_unidades,tb_dados_contrato,tb_modalidade_metropolitana,tb_referencia_contrato,tb_modalidade_interior


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'photo')


class Cadastrar_ContratoForm(forms.ModelForm):
    required_css_class = 'required'
    unidade = forms.ModelChoiceField(
        label = 'Unidade',
        queryset=tb_unidades.objects.all()
        )
    class Meta:
        model = tb_dados_contrato
        fields = ('r_m','unidade','numemro_contrato','nome_contratada','gestor_1','gestor_2','resp_contratada','administrador',
                  'superintendente','data_inicio','data_fim','staff_2')
        widgets = {
            'data_inicio': forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control',
                                                                       'placeholder':'Select a date', 'type':'date'}),
            'data_fim': forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control',
                                                                    'placeholder':'Select a date', 'type':'date'}),
    }

    def __int__(self,unidade,data_inicio,*args, **kwargs):
        super().__init__(*args, **kwargs)
        unidades = tb_unidades.objects.values_list('sigla_unidade')
        self.fields['unidade'].queryset = unidades['sigla_unidade']
        for field_name, field in self.fields.items():
            field.attrs['class'] = 'form-control'

class informar_indicador_MForm(forms.ModelForm):
    contrato = forms.ModelChoiceField(
        label = 'Contrato',
        queryset=tb_dados_contrato.objects.
        filter(r_m='M',numemro_contrato__in =tb_referencia_contrato.objects.values_list('contrato').
               filter(status='ABERTO'))
        )
    class Meta:
        model = tb_modalidade_metropolitana
        fields = ('contrato','idg','isap','ida','ide',
                  'idr','total_redes','total_cadastro_entregue','quantidade_colaboradores',
                  'quantidade_acidentes','justificativa')
    def __int__(self,contrato,*args, **kwargs):
        super().__init__(*args, **kwargs)
        usuario = kwargs['initial']['usuario']
        contratos = tb_referencia_contrato.objects.values_list('contratos').filter(staf_1=usuario)
        self.fields['contrato'].queryset = contrato[0]
        for field_name, field in self.fields.items():
            field.attrs['class'] = 'form-control'
class informar_indicador_RForm(forms.ModelForm):
    contrato = forms.ModelChoiceField(
        label = 'Contrato',
        queryset=tb_dados_contrato.objects.
        filter(r_m='R',numemro_contrato__in =tb_referencia_contrato.objects.values_list('contrato').
               filter(status='ABERTO'))
        )
    class Meta:
        model = tb_modalidade_interior
        fields = ('contrato','idg_interior','servicos_arsesp','total_redes','total_cadastro_entregue',
                  'quantidade_colaboradores','quantidade_acidentes','justificativa')
    def __int__(self,contrato,*args, **kwargs):
        super().__init__(*args, **kwargs)
        usuario = kwargs['initial']['usuario']
        contratos = tb_referencia_contrato.objects.values_list('contratos').filter(staf_1=usuario)
        self.fields['contrato'].queryset = contrato[0]
        for field_name, field in self.fields.items():
            field.attrs['class'] = 'form-control'
