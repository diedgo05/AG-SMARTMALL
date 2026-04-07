"""
Utilidades y funciones auxiliares.
"""

from .cargador_datos import (
    cargar_catalogo,
    cargar_configuracion,
    cargar_requerimientos_nutricionales
)

__all__ = [
    'cargar_catalogo',
    'cargar_configuracion',
    'cargar_requerimientos_nutricionales'
]