from django import forms
from django.contrib.auth.models import User
from .models import EventoEscala, Matricula, Hospital, Setor, TipoEvento, Periodo, Especialidade, PerfilUsuario

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
        fields = ['data', 'profissional', 'tipo_evento', 'hospital', 'setor', 'cor', 'observacoes']
        widgets = {
            'cor': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'cor':
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        if user and hasattr(user, 'perfil'):
            if user.perfil.tipo_usuario == 'PROFISSIONAL':
                minha_matricula = user.perfil.matriculas.all()
                self.fields['profissional'].queryset = minha_matricula
                self.fields['profissional'].initial = minha_matricula.first()
                self.fields['profissional'].widget.attrs['readonly'] = True
            elif user.perfil.tipo_usuario == 'ESCALANTE':
                matricula = user.perfil.matriculas.first()
                if matricula:
                    self.fields['profissional'].queryset = Matricula.objects.filter(setor=matricula.setor)
                    self.fields['setor'].queryset = Setor.objects.filter(id=matricula.setor.id)
                    self.fields['hospital'].queryset = Hospital.objects.filter(id=matricula.hospital.id)

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
        fields = ['nome', 'tipo_usuario']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_usuario': forms.Select(attrs={'class': 'form-control'}),
        }

class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = ['numero', 'perfil', 'nome_exibicao', 'nome_completo', 'carga_horaria_semanal', 'hospital', 'setor', 'especialidade']
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'perfil': forms.Select(attrs={'class': 'form-control'}),
            'nome_exibicao': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'carga_horaria_semanal': forms.NumberInput(attrs={'class': 'form-control'}),
            'hospital': forms.Select(attrs={'class': 'form-control'}),
            'setor': forms.Select(attrs={'class': 'form-control'}),
            'especialidade': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra para mostrar apenas perfis que são do tipo PROFISSIONAL (agora Enfermeiro)
        self.fields['perfil'].queryset = PerfilUsuario.objects.filter(tipo_usuario='PROFISSIONAL')
