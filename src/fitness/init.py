"""
Módulo de cálculo de fitness (aptitud) para el Algoritmo Genético.

Componentes del fitness:
- f1: Costo (minimizar)
- f2: Nutrición (maximizar)
- f3: Desperdicio (minimizar)
- f4: Cobertura de comidas (maximizar)
- f5: Satisfacción de preferencias (maximizar)

Fitness total = w1*f1 + w2*f2 + w3*f3 + w4*f4 + w5*f5
donde w1 + w2 + w3 + w4 + w5 = 1.0
"""

from .fitness_costo import calcular_fitness_costo
from .fitness_nutricion import calcular_fitness_nutricion
from .fitness_desperdicio import calcular_fitness_desperdicio
from .fitness_cobertura import calcular_fitness_cobertura
from .fitness_satisfaccion import calcular_fitness_satisfaccion
from .fitness_total import calcular_fitness_total

__all__ = [
    'calcular_fitness_costo',
    'calcular_fitness_nutricion',
    'calcular_fitness_desperdicio',
    'calcular_fitness_cobertura',
    'calcular_fitness_satisfaccion',
    'calcular_fitness_total'
]