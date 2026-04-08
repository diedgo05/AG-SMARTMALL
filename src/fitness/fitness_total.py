"""
Integrador de fitness: Combina todos los componentes.

Fitness Total = w1*f_costo + w2*f_nutricion + w3*f_desperdicio + 
                w4*f_cobertura + w5*f_satisfaccion

Donde: w1 + w2 + w3 + w4 + w5 = 1.0
"""

import pandas as pd
from typing import Dict

from .fitness_costo import calcular_fitness_costo
from .fitness_nutricion import calcular_fitness_nutricion
from .fitness_desperdicio import calcular_fitness_desperdicio
from .fitness_cobertura import calcular_fitness_cobertura
from .fitness_satisfaccion import calcular_fitness_satisfaccion


def calcular_fitness_total(
    individuo: Dict,
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict,
    requerimientos: pd.DataFrame
) -> float:
    """
    Calcula el fitness total del individuo combinando todos los componentes.
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma a evaluar
    catalogo : pd.DataFrame
        Catálogo de productos
    config : dict
        Configuración del AG (incluye pesos)
    entrada_usuario : dict
        Datos de entrada del usuario
    requerimientos : pd.DataFrame
        Tabla de requerimientos nutricionales
        
    Returns:
    --------
    float
        Fitness total en [0, 1]
        1.0 = solución óptima en todos los criterios
    """
    
    # Obtener pesos de la configuración
    pesos = config['fitness']['pesos']
    
    w_costo = pesos['costo']
    w_nutricion = pesos['nutricion']
    w_desperdicio = pesos['desperdicio']
    w_cobertura = pesos['cobertura']
    w_satisfaccion = pesos['satisfaccion']
    
    # Calcular cada componente de fitness
    f_costo = calcular_fitness_costo(individuo, catalogo, config, entrada_usuario)
    
    f_nutricion = calcular_fitness_nutricion(
        individuo, catalogo, config, entrada_usuario, requerimientos
    )
    
    f_desperdicio = calcular_fitness_desperdicio(
        individuo, catalogo, config, entrada_usuario
    )
    
    f_cobertura = calcular_fitness_cobertura(
        individuo, catalogo, config, entrada_usuario
    )
    
    f_satisfaccion = calcular_fitness_satisfaccion(
        individuo, catalogo, config, entrada_usuario
    )
    
    # Combinar con pesos
    fitness_total = (
        w_costo * f_costo +
        w_nutricion * f_nutricion +
        w_desperdicio * f_desperdicio +
        w_cobertura * f_cobertura +
        w_satisfaccion * f_satisfaccion
    )
    
    # Guardar componentes en metadata
    individuo['metadata']['fitness'] = fitness_total
    individuo['metadata']['fitness_componentes'] = {
        'costo': round(f_costo, 4),
        'nutricion': round(f_nutricion, 4),
        'desperdicio': round(f_desperdicio, 4),
        'cobertura': round(f_cobertura, 4),
        'satisfaccion': round(f_satisfaccion, 4)
    }
    
    return fitness_total