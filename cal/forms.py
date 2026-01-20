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
