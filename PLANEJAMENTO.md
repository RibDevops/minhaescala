# Planejamento: Saldo de Horas Semanais

## Objetivo

Mostrar o saldo de horas de cada enfermeiro na semana atual e na próxima, com base nos plantões registrados.
A semana começa no **domingo**.

Exemplo:
- Carga semanal: 20h
- Horas feitas esta semana: 28h
- Saldo desta semana: **+8h** (fez a mais)
- Carga da próxima semana: 20h - 8h = **12h** (deve fazer a menos)

---

## Regra de negócio

```
saldo_semana = horas_realizadas - carga_horaria_semanal

# Saldo positivo → fez horas a mais → próxima semana desconta
# Saldo negativo → fez horas a menos → próxima semana acrescenta

carga_proxima_semana = carga_horaria_semanal - saldo_semana
```

O saldo acumula semana a semana (não zera a cada mês).
Somente plantões com `tipo.tipo_base.contabiliza = True` entram no cálculo.

---

## O que existe hoje

- `Matricula.carga_horaria_semanal` → carga de referência do profissional
- `EventoEscala` → plantões registrados com data e tipo (que tem `horas`)
- `ControleSemanal` → modelo já existe mas não é populado automaticamente (usado pela importação de Excel)
- `EventoEscala.carga_ultimos_7_dias()` → já calcula horas nos últimos 7 dias (janela deslizante, não semana calendário)

---

## O que precisa ser feito

### 1. Função utilitária de cálculo de saldo

Criar em `cal/utils_saldo.py` (ou dentro de `cal/utils.py`):

```python
def semana_atual(referencia=None):
    """Retorna (domingo_inicio, sabado_fim) da semana que contém 'referencia'."""

def horas_semana(profissional, inicio, fim):
    """Soma horas dos EventoEscala contabilizáveis do profissional no período."""

def saldo_semana(profissional, inicio, fim):
    """Retorna horas_semana - carga_horaria_semanal. Positivo = fez a mais."""

def carga_proxima_semana(profissional, inicio_semana_atual):
    """Retorna carga_horaria_semanal - saldo_semana_atual."""
```

### 2. Colunas na lista de profissionais (`/escala-mensal/`)

Na view `escala_mes_view` (`cal/views/escala_mes_views.py`), adicionar ao contexto de cada profissional:

```python
{
    'profissional': ...,
    'dias': ...,
    'semanas_totais': ...,
    'total_mes': ...,
    # NOVO:
    'saldo_semana_atual': +8,    # ex: fez 8h a mais
    'carga_proxima_semana': 12,  # ex: deve fazer 12h na próxima
}
```

### 3. Template `escala/escala_mes.html`

Adicionar duas colunas na tabela de profissionais:

| Profissional | ... dias ... | Total mês | **Esta semana** | **Próxima semana** |
|---|---|---|---|---|
| João | ... | 80h | +8h | 12h |
| Maria | ... | 60h | -4h | 24h |

- Saldo positivo → badge verde (`+Xh`)
- Saldo negativo → badge vermelho (`-Xh`)
- Saldo zero → badge cinza (`0h`)
- Próxima semana → número simples em cinza

### 4. Definição de "semana atual" na escala mensal

A escala mensal exibe um mês inteiro. A coluna "esta semana" deve mostrar
a semana do calendário que contém **hoje**, não o mês exibido.

Se o mês exibido não contém a semana atual, mostrar `—` nas colunas de saldo.

---

## Arquivos a modificar

| Arquivo | O que muda |
|---|---|
| `cal/utils_saldo.py` | Criar — funções de cálculo de saldo |
| `cal/views/escala_mes_views.py` | Adicionar saldo ao contexto de cada profissional |
| `templates/escala/escala_mes.html` | Adicionar duas colunas na tabela |

---

## Pontos de atenção

- **Semana começa no domingo** (weekday 6 no Python, que usa seg=0). Usar `isoweekday()` ou ajustar manualmente.
- **Somente plantões contabilizáveis** (`tipo.tipo_base.contabiliza = True`). TPDs e folgas não entram.
- **Plantões privados do enfermeiro** (criados pelo próprio enfermeiro) — decidir se entram no cálculo ou não. Sugestão: entram, pois representam horas reais trabalhadas.
- O modelo `ControleSemanal` existe mas não é usado aqui — o cálculo será feito dinamicamente via `EventoEscala`, sem depender de `ControleSemanal`.
- Não criar migration — nenhum campo novo no banco.
