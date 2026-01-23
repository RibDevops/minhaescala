from django import forms
from django.contrib.auth.models import User
from .models import EventoEscala, Matricula, TipoEvento, Periodo, Especialidade, PerfilUsuario, Tipo
from core.models import Hospital, Setor

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['user', 'tipo']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
        }

class PeriodoForm(forms.ModelForm):
    class Meta:
        model = Periodo
        fields = ['nome', 'sigla']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'sigla': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EspecialidadeForm(forms.ModelForm):
    class Meta:
        model = Especialidade
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("As senhas não coincidem.")
        return cleaned_data

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff']

class UsuarioUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UsuarioPasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

class PlantaoForm(forms.ModelForm):
    class Meta:
        model = EventoEscala
        fields = ['data', 'profissional', 'tipo', 'hospital', 'setor', 'observacao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        if user:
            perfil = getattr(user, 'cal_perfil', None)
            if not user.is_staff and perfil:
                if hasattr(user, 'matricula') and user.matricula:
                    matricula = user.matricula
                    self.fields['hospital'].queryset = Hospital.objects.filter(id=matricula.hospital.id)
                    self.fields['setor'].queryset = Setor.objects.filter(id=matricula.setor.id)
                    self.initial['hospital'] = matricula.hospital
                    self.initial['setor'] = matricula.setor
                    if perfil.tipo == 'ENFERMEIRO':
                        self.fields['profissional'].queryset = Matricula.objects.filter(id=matricula.id)
                        self.initial['profissional'] = matricula
                    elif perfil.tipo == 'ESCALANTE':
                        self.fields['profissional'].queryset = Matricula.objects.filter(
                            hospital=matricula.hospital,
                            setor=matricula.setor,
                            ativo=True
                        )
                else:
                    self.fields['profissional'].queryset = Matricula.objects.none()
                    self.fields['hospital'].queryset = Hospital.objects.none()
                    self.fields['setor'].queryset = Setor.objects.none()

class HospitalForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = ['nome', 'sigla']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'sigla': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ['nome', 'hospital']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital': forms.Select(attrs={'class': 'form-control'}),
        }

class TipoForm(forms.ModelForm):
    class Meta:
        model = Tipo
        fields = ['tipo', 'tipo_descricao', 'contabiliza']
        widgets = {
            'tipo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'contabiliza': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TipoEventoForm(forms.ModelForm):
    class Meta:
        model = TipoEvento
        fields = ['tipo_base', 'codigo', 'descricao', 'horas', 'cor']
        widgets = {
            'tipo_base': forms.Select(attrs={'class': 'form-select'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'horas': forms.NumberInput(attrs={'class': 'form-control'}),
            'cor': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color', 'style': 'width: 100%; height: 38px;'}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class MatriculaSimplificadaForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Nome de Usuário (Login)", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    first_name = forms.CharField(max_length=150, label="Primeiro Nome", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, label="Último Nome", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    tipo_perfil = forms.ChoiceField(choices=PerfilUsuario.TIPO_USUARIO_CHOICES, label="Tipo de Perfil (Acesso)", initial='ENFERMEIRO', widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = Matricula
        fields = ['matricula', 'nome_exibicao', 'coren', 'hospital', 'setor', 'especialidade', 'carga_horaria_semanal', 'ativo']
        widgets = {
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_exibicao': forms.TextInput(attrs={'class': 'form-control'}),
            'coren': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital': forms.Select(attrs={'class': 'form-control'}),
            'setor': forms.Select(attrs={'class': 'form-control'}),
            'especialidade': forms.Select(attrs={'class': 'form-control'}),
            'carga_horaria_semanal': forms.NumberInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username
