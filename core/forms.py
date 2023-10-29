from django import forms
from django.contrib.auth.models import User
from .models import Profile,tb_dados_contrato,unidades



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

class Dados_ContratoForm(forms.ModelForm):
    required_css_class = 'required'
    unidade = forms.ModelChoiceField(
        label = 'Unidade',
        queryset=unidades.objects.all()
    )
    class Meta:
        model = tb_dados_contrato
        fields = ('r_m','unidade','numemro_contrato','nome_contratada','administrador','superintendente','data_inicio','data_fim',
                  'staff_1','staff_2')
    def __int__(self,unidade,*args, **kwargs):
        super().__init__(*args, **kwargs)
        unidades = unidade.objects.values_list('sigla_unidade')
        self.fields['unidade'].queryset = unidades['sigla_unidade']
        for field_name, field in self.fields.items():
            field.attrs['class'] = 'form-control'
