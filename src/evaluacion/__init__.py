"""
Módulo de evaluación del Algoritmo Genético.

Responsabilidades:
- Evaluar poblaciones completas (calcular fitness de cada individuo)
- Validar restricciones duras
- Ordenar población por fitness
- Coordinar reparación de individuos inválidos
"""

from .evaluador import evaluar_poblacion, evaluar_individuo
from .validador import validar_restricciones_duras, es_individuo_valido, contar_violaciones_poblacion

__all__ = [
    'evaluar_poblacion',
    'evaluar_individuo',
    'validar_restricciones_duras',
    'es_individuo_valido',
    'contar_violaciones_poblacion'
]