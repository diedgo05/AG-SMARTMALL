"""
Selección por ruleta (Roulette Wheel Selection).

Mecanismo:
1. Cada individuo tiene probabilidad de selección proporcional a su fitness
2. Individuo con fitness alto → mayor probabilidad
3. Similar a una ruleta donde cada individuo tiene un sector proporcional

Ventajas:
- Todos tienen oportunidad (incluso los peores)
- Presión selectiva natural

Desventajas:
- Puede tener problemas con fitness negativo
- Convergencia prematura si un individuo domina
"""

import numpy as np
from typing import Dict, List


def seleccionar_por_ruleta(
    poblacion: List[Dict]
) -> Dict:
    """
    Selecciona un individuo mediante ruleta.
    
    Proceso:
    1. Calcular fitness total de la población
    2. Calcular probabilidad de cada individuo: p_i = fitness_i / fitness_total
    3. Girar la ruleta (selección aleatoria ponderada)
    
    Parameters:
    -----------
    poblacion : list
        Población de individuos (deben tener fitness calculado)
        
    Returns:
    --------
    dict
        Individuo seleccionado
        
    Nota:
    -----
    Si hay fitness negativos o muy cercanos a cero, se aplica escalamiento
    para garantizar probabilidades válidas.
    """
    
    # Obtener fitness de todos los individuos
    fitness_values = np.array([
        ind['metadata']['fitness'] 
        for ind in poblacion
    ])
    
    # Manejar fitness negativos o muy pequeños
    # Shift para asegurar todos positivos
    min_fitness = np.min(fitness_values)
    
    if min_fitness < 0:
        # Desplazar todos los fitness para que sean positivos
        fitness_values = fitness_values - min_fitness + 1e-6
    elif np.all(fitness_values < 1e-6):
        # Si todos son muy pequeños, asignar probabilidades uniformes
        fitness_values = np.ones(len(poblacion))
    
    # Calcular probabilidades
    fitness_total = np.sum(fitness_values)
    
    if fitness_total == 0:
        # Caso extremo: todos tienen fitness 0
        probabilidades = np.ones(len(poblacion)) / len(poblacion)
    else:
        probabilidades = fitness_values / fitness_total
    
    # Seleccionar individuo según probabilidades
    indice_seleccionado = np.random.choice(
        len(poblacion),
        p=probabilidades
    )
    
    return poblacion[indice_seleccionado]


def seleccionar_padres_ruleta(
    poblacion: List[Dict],
    n_padres: int
) -> List[Dict]:
    """
    Selecciona múltiples padres mediante ruleta.
    
    Parameters:
    -----------
    poblacion : list
        Población de individuos
    n_padres : int
        Número de padres a seleccionar
        
    Returns:
    --------
    list
        Lista de padres seleccionados
    """
    
    padres = []
    
    for _ in range(n_padres):
        padre = seleccionar_por_ruleta(poblacion)
        padres.append(padre)
    
    return padres


def seleccionar_parejas_ruleta(
    poblacion: List[Dict],
    n_parejas: int
) -> List[tuple]:
    """
    Selecciona parejas de padres para cruza mediante ruleta.
    
    Parameters:
    -----------
    poblacion : list
        Población de individuos
    n_parejas : int
        Número de parejas a formar
        
    Returns:
    --------
    list
        Lista de tuplas (padre1, padre2)
    """
    
    parejas = []
    
    for _ in range(n_parejas):
        padre1 = seleccionar_por_ruleta(poblacion)
        padre2 = seleccionar_por_ruleta(poblacion)
        
        parejas.append((padre1, padre2))
    
    return parejas