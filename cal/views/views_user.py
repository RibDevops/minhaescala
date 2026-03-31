from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm, SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from django import forms
from ..models import Matricula


# ── Formulários inline ───────────────────────────────────────────────────────

class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']
        labels = {
            'username': 'Login',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'is_staff': 'Administrador',
            'is_active': 'Ativo',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AdicionarUsuarioForm(UserCreationForm):
    first_name = forms.CharField(label='Nome', required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name  = forms.CharField(label='Sobrenome', required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    email      = forms.EmailField(label='E-mail', required=False,
                                  widget=forms.EmailInput(attrs={'class': 'form-control'}))
    is_staff   = forms.BooleanField(label='Administrador', required=False,
                                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['username'].label = 'Login'


# ── Home ─────────────────────────────────────────────────────────────────────

def home(request):
    if not request.user.is_authenticated:
        return render(request, 'home.html')

    from datetime import date, timedelta
    from django.db.models import Q
    from ..models import EventoEscala
    from ..permissions import is_admin, is_escalante, is_enfermeiro

    hoje = date.today()
    matricula = None
    try:
        matricula = Matricula.objects.filter(user=request.user, ativo=True).first()
    except Exception:
        pass

    plantoes_hoje = []
    proximos = []
    # Flag para controlar o que o template pode mostrar
    pode_editar = not is_enfermeiro(request.user)
    # Flag para indicar se a visão é de setor (ENFERMEIRO vê a escala completa)
    visao_setor = is_enfermeiro(request.user)

    if matricula:
        fim = hoje + timedelta(days=30)
        amanha = hoje + timedelta(days=1)
        base_qs = (
            EventoEscala.objects
            .select_related('tipo', 'hospital', 'setor', 'profissional')
            .order_by('data', 'profissional__nome_exibicao')
        )

        user = request.user

        # "Plantão Hoje" é SEMPRE pessoal — mostra se o usuário logado tem plantão hoje
        plantoes_hoje = list(
            base_qs.filter(profissional=matricula, data=hoje)
        )

        if is_admin(user):
            proximos_qs = base_qs.filter(data__gte=amanha, data__lte=fim)

        elif is_escalante(user):
            # Escalante: "Próximos Plantões" na Home = apenas os PRÓPRIOS plantões
            # (A escala completa do setor fica no Calendário e na Lista)
            proximos_qs = base_qs.filter(
                profissional=matricula,
                data__gte=amanha,
                data__lte=fim,
            )

        elif is_enfermeiro(user):
            # Enfermeiro: "Próximos Plantões" = escala COMPLETA do setor (alinhado com Calendário)
            # Apenas plantões oficiais (não criados por ENFERMEIROs) + os próprios
            oficiais = Q(
                hospital=matricula.hospital,
                setor=matricula.setor,
                data__gte=amanha,
                data__lte=fim,
            ) & ~Q(criado_por__cal_perfil__tipo='ENFERMEIRO')
            proprios = Q(profissional=matricula, data__gte=amanha, data__lte=fim)
            proximos_qs = base_qs.filter(oficiais | proprios).distinct()

        else:
            proximos_qs = base_qs.filter(profissional=matricula, data__gte=amanha, data__lte=fim)

        proximos = list(proximos_qs[:20])

    return render(request, 'home.html', {
        'hoje': hoje,
        'matricula': matricula,
        'plantoes_hoje': plantoes_hoje,
        'proximos': proximos[:20],
        'pode_editar': pode_editar,
        'visao_setor': visao_setor,
    })


# ── Auth ─────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            return redirect('cal:home')
        messages.error(request, 'Usuário ou senha inválidos')
    return render(request, 'cal/login.html')

def logout_view(request):
    logout(request)
    return redirect('cal:login')

def register_view(request):
    return render(request, 'cal/register.html')


# ── Perfil do próprio usuário ─────────────────────────────────────────────────

@login_required
def perfil_usuario(request):
    if request.method == 'POST':
        if 'perfil_submit' in request.POST:
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name  = request.POST.get('last_name', '')
            request.user.email      = request.POST.get('email', '')
            request.user.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('cal:perfil')
        elif 'password_submit' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('cal:perfil')

    password_form = PasswordChangeForm(request.user)
    matricula = getattr(request.user, 'matricula', None)
    return render(request, 'cal/perfil.html', {
        'password_form': password_form,
        'matricula': matricula
    })


# ── Gestão de usuários (staff only) ──────────────────────────────────────────

def _requer_staff(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('cal:home')
    return None


def listar_usuarios(request):
    guard = _requer_staff(request)
    if guard:
        return guard
    usuarios = User.objects.all().select_related().order_by('username')
    return render(request, 'usuarios/listar.html', {'usuarios': usuarios})


def adicionar_usuario(request):
    guard = _requer_staff(request)
    if guard:
        return guard
    if request.method == 'POST':
        form = AdicionarUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = form.cleaned_data.get('is_staff', False)
            user.save()
            messages.success(request, f'Usuário "{user.username}" criado com sucesso!')
            return redirect('cal:listar_usuarios')
    else:
        form = AdicionarUsuarioForm()
    return render(request, 'usuarios/form_usuario.html', {
        'form': form,
        'titulo': 'Novo Usuário',
        'btn_label': 'Criar Usuário',
    })


def editar_usuario(request, pk):
    guard = _requer_staff(request)
    if guard:
        return guard
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuário "{usuario.username}" atualizado!')
            return redirect('cal:listar_usuarios')
    else:
        form = EditarUsuarioForm(instance=usuario)
    return render(request, 'usuarios/form_usuario.html', {
        'form': form,
        'titulo': f'Editar — {usuario.username}',
        'btn_label': 'Salvar Alterações',
        'usuario': usuario,
    })


def resetar_senha(request, pk):
    guard = _requer_staff(request)
    if guard:
        return guard
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = SetPasswordForm(usuario, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Senha de "{usuario.username}" redefinida!')
            return redirect('cal:listar_usuarios')
    else:
        form = SetPasswordForm(usuario)
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'
    return render(request, 'usuarios/form_usuario.html', {
        'form': form,
        'titulo': f'Redefinir Senha — {usuario.username}',
        'btn_label': 'Salvar Nova Senha',
        'usuario': usuario,
    })


def desativar_usuario(request, pk):
    guard = _requer_staff(request)
    if guard:
        return guard
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, 'Você não pode desativar sua própria conta.')
        return redirect('cal:listar_usuarios')
    usuario.is_active = not usuario.is_active
    usuario.save()
    estado = 'ativado' if usuario.is_active else 'desativado'
    messages.success(request, f'Usuário "{usuario.username}" {estado}.')
    return redirect('cal:listar_usuarios')


def excluir_usuario(request, pk):
    guard = _requer_staff(request)
    if guard:
        return guard
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, 'Você não pode excluir sua própria conta.')
        return redirect('cal:listar_usuarios')
    if request.method == 'POST':
        nome = usuario.username
        usuario.delete()
        messages.success(request, f'Usuário "{nome}" excluído.')
        return redirect('cal:listar_usuarios')
    return render(request, 'usuarios/confirmar_exclusao.html', {'usuario': usuario})
