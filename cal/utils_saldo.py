"""
Utilitários para cálculo de saldo de horas semanais.

Semana começa no domingo e termina no sábado.
Somente plantões com tipo.tipo_base.contabiliza=True entram no cálculo.
"""

from datetime import date, timedelta
from django.db.models import Sum


def inicio_semana(referencia=None):
    """
    Retorna o domingo que inicia a semana da data de referência.
    Python: segunda=0 ... domingo=6
    """
    if referencia is None:
        referencia = date.today()
    # isoweekday: segunda=1 ... domingo=7
    dias_desde_domingo = referencia.isoweekday() % 7  # domingo=0, segunda=1, ...
    return referencia - timedelta(days=dias_desde_domingo)


def fim_semana(referencia=None):
    """Retorna o sábado que encerra a semana da data de referência."""
    return inicio_semana(referencia) + timedelta(days=6)


def horas_no_periodo(profissional, inicio, fim):
    """
    Soma as horas dos EventoEscala contabilizáveis do profissional
    no intervalo [inicio, fim] (inclusive).
    Plantões registrados pelo próprio enfermeiro (privados) não entram.
    """
    from .models import EventoEscala
    eventos = EventoEscala.objects.filter(
        profissional=profissional,
        data__range=(inicio, fim),
        tipo__tipo_base__contabiliza=True,
    ).exclude(
        criado_por__cal_perfil__tipo='ENFERMEIRO'
    ).select_related('tipo')
    return sum(e.tipo.horas for e in eventos)


def saldo_semana(profissional, referencia=None):
    """
    Retorna o saldo de horas da semana que contém 'referencia'.
      > 0 → fez horas a mais
      < 0 → fez horas a menos
      = 0 → exatamente na carga
    """
    inicio = inicio_semana(referencia)
    fim = fim_semana(referencia)
    horas = horas_no_periodo(profissional, inicio, fim)
    return horas - profissional.carga_horaria_semanal


def carga_proxima_semana(profissional, referencia=None):
    """
    Retorna quantas horas o profissional deve fazer na semana seguinte,
    descontando ou acrescendo o saldo da semana atual.

    Nunca retorna valor negativo (se fez horas demais além da carga
    da próxima semana, retorna 0).
    """
    saldo = saldo_semana(profissional, referencia)
    carga_ajustada = profissional.carga_horaria_semanal - saldo
    return max(0, carga_ajustada)


def saldo_info(profissional, mes, ano):
    """
    Retorna um dict com os dados de saldo para exibição na escala mensal.

    Se a semana atual não pertence ao mês/ano exibido, retorna None
    para indicar que as colunas devem mostrar '—'.

    Retorno:
        {
            'saldo': int,           # ex: +8 ou -4
            'carga_proxima': int,   # ex: 12
            'semana_no_mes': bool,  # True se a semana atual está no mês exibido
        }
    """
    hoje = date.today()
    inicio = inicio_semana(hoje)
    fim = fim_semana(hoje)

    # Verifica se algum dia da semana atual pertence ao mês exibido
    semana_no_mes = (
        (inicio.year == ano and inicio.month == mes) or
        (fim.year == ano and fim.month == mes) or
        (inicio <= date(ano, mes, 1) <= fim)
    )

    saldo = saldo_semana(profissional, hoje)
    carga_prox = carga_proxima_semana(profissional, hoje)

    return {
        'saldo': saldo,
        'carga_proxima': carga_prox,
        'semana_no_mes': semana_no_mes,
    }
