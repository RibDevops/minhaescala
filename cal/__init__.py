# escalas/views/__init__.py
from .hospital_views import *
from .setor_views import *
from .periodo_views import *
from .tipo_evento_views import *
from .especialidade_views import *
from .matricula_views import *

__all__ = [
    # Hospital
    'hospital_list',
    'hospital_create',
    'hospital_detail',
    'hospital_update',
    'hospital_delete',
    
    # Setor
    'setor_list',
    'setor_create',
    'setor_update',
    'setor_delete',
    
    # Periodo
    'periodo_list',
    'periodo_create',
    'periodo_update',
    'periodo_delete',
    
    # TipoEvento
    'tipo_evento_list',
    'tipo_evento_create',
    'tipo_evento_update',
    'tipo_evento_delete',
    
    # Especialidade
    'especialidade_list',
    'especialidade_create',
    'especialidade_update',
    'especialidade_delete',
    
    # Matricula
    'matricula_list',
    'matricula_create',
    'matricula_detail',
    'matricula_update',
    'matricula_delete',
]