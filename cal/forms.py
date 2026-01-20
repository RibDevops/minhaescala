from django import forms
from django.contrib.auth.models import User
from .models import EventoEscala, Matricula, Hospital, Setor, TipoEvento

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
        fields = ['profissional', 'tipo_evento', 'data', 'setor', 'hospital', 'observacoes']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        if user and hasattr(user, 'perfil'):
            if user.perfil.tipo_usuario == 'ESCALANTE':
                matricula = getattr(user.perfil, 'matricula', None)
                if matricula:
                    self.fields['profissional'].queryset = Matricula.objects.filter(setores__in=matricula.setores.all())
                    self.fields['setor'].queryset = matricula.setores.all()
                    self.fields['hospital'].queryset = Hospital.objects.filter(id__in=matricula.hospitais.all())


# forms.py
from django import forms
from .models import Hospital, Setor, Periodo, TipoEvento, Especialidade, Matricula, PerfilUsuario
from django.contrib.auth.models import User

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

class PeriodoForm(forms.ModelForm):
    class Meta:
        model = Periodo
        fields = ['nome', 'sigla']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'sigla': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TipoEventoForm(forms.ModelForm):
    class Meta:
        model = TipoEvento
        fields = ['nome', 'codigo', 'periodo', 'horas', 'cor', 'contabiliza_carga_horaria']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'periodo': forms.Select(attrs={'class': 'form-control'}),
            'horas': forms.NumberInput(attrs={'class': 'form-control'}),
            'cor': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'contabiliza_carga_horaria': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EspecialidadeForm(forms.ModelForm):
    class Meta:
        model = Especialidade
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
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

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['tipo_usuario']
        widgets = {
            'tipo_usuario': forms.Select(attrs={'class': 'form-control'}),
        }

class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = ['numero', 'nome_exibicao', 'nome_completo', 'carga_horaria_semanal', 'hospitais', 'setores', 'especialidades']
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_exibicao': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'carga_horaria_semanal': forms.NumberInput(attrs={'class': 'form-control'}),
            'hospitais': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'setores': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'especialidades': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        }