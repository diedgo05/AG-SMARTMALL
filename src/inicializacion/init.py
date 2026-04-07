"""
Módulo de inicialización del Algoritmo Genético.
Responsable de generar población inicial de individuos válidos.
"""

from .individuo import generar_individuo_aleatorio
from .poblacion import generar_poblacion_inicial

__all__ = [
    'generar_individuo_aleatorio',
    'generar_poblacion_inicial'
]