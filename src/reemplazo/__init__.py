"""
Módulo de selección y reemplazo generacional para el Algoritmo Genético.

Componentes:
- Selección de padres: Determina quiénes se reproducen
- Elitismo: Preserva mejores individuos
- Reemplazo generacional: Crea nueva generación

Estrategias de selección:
- Torneo: k individuos compiten, gana el mejor (recomendado)
- Ruleta: probabilidad proporcional al fitness
"""

from .seleccion_torneo import seleccionar_por_torneo, seleccionar_padres_torneo
from .seleccion_ruleta import seleccionar_por_ruleta, seleccionar_padres_ruleta
from .poda import aplicar_poda, obtener_elite
from .reemplazo_generacional import (
    generar_nueva_generacion,
    reemplazar_poblacion
)

__all__ = [
    'seleccionar_por_torneo',
    'seleccionar_padres_torneo',
    'seleccionar_por_ruleta',
    'seleccionar_padres_ruleta',
    'aplicar_poda',
    'obtener_elite',
    'generar_nueva_generacion',
    'reemplazar_poblacion'
]