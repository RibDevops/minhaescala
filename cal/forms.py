from django import forms
from .models import Plantao, Solicitacao, Enfermeiro, Hospital, Setor, TipoPlantao
from datetime import datetime

class PlantaoForm(forms.ModelForm):
    class Meta:
        model = Plantao
        fields = ['enfermeiro', 'tipo_plantao', 'data', 'hora_inicio', 'hora_fim', 'setor', 'hospital', 'observacoes']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        if user and hasattr(user, 'perfil'):
            if user.perfil.tipo_usuario == 'ESCALANTE':
                enf = getattr(user.perfil, 'enfermeiro', None)
                if enf:
                    self.fields['enfermeiro'].queryset = Enfermeiro.objects.filter(setores__in=enf.setores.all())
                    self.fields['setor'].queryset = enf.setores.all()
                    self.fields['hospital'].queryset = Hospital.objects.filter(id__in=enf.hospitais.all())

class SolicitacaoForm(forms.ModelForm):
    class Meta:
        model = Solicitacao
        fields = ['tipo', 'data_inicio', 'data_fim', 'motivo', 'plantao_origem', 'enfermeiro_destino']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        if user and hasattr(user, 'perfil') and hasattr(user.perfil, 'enfermeiro'):
            self.fields['plantao_origem'].queryset = Plantao.objects.filter(
                enfermeiro=user.perfil.enfermeiro,
                data__gte=datetime.today()
            )
