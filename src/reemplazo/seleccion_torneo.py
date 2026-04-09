"""
Selección por torneo.

Mecanismo:
1. Seleccionar k individuos aleatorios de la población
2. El individuo con mejor fitness gana el torneo
3. El ganador es seleccionado como padre

Ventajas:
- Simple y eficiente
- Presión selectiva ajustable (tamaño k)
- No requiere ordenamiento completo
- Funciona bien en la mayoría de problemas

Recomendación: k=5 (equilibrio entre diversidad y presión selectiva)
"""

import numpy as np
from typing import Dict, List


def seleccionar_por_torneo(
    poblacion: List[Dict],
    k: int = 5
) -> Dict:
    """
    Selecciona un individuo mediante torneo.
    
    Proceso:
    1. Seleccionar k individuos aleatorios
    2. Retornar el de mayor fitness
    
    Parameters:
    -----------
    poblacion : list
        Población de individuos (deben tener fitness calculado)
    k : int
        Tamaño del torneo (default: 5)
        - k pequeño (2-3): menor presión selectiva, más diversidad
        - k grande (7-10): mayor presión selectiva, convergencia rápida
        
    Returns:
    --------
    dict
        Individuo ganador del torneo
    """
    
    # Validación
    if k > len(poblacion):
        k = len(poblacion)
    
    # Seleccionar k individuos aleatorios
    indices_competidores = np.random.choice(
        len(poblacion),
        size=k,
        replace=False  # Sin repetición
    )
    
    competidores = [poblacion[i] for i in indices_competidores]
    
    # Encontrar el mejor (mayor fitness)
    ganador = max(competidores, key=lambda ind: ind['metadata']['fitness'])
    
    return ganador


def seleccionar_padres_torneo(
    poblacion: List[Dict],
    n_padres: int,
    k: int = 5
) -> List[Dict]:
    """
    Selecciona múltiples padres mediante torneos.
    
    Parameters:
    -----------
    poblacion : list
        Población de individuos
    n_padres : int
        Número de padres a seleccionar
    k : int
        Tamaño del torneo
        
    Returns:
    --------
    list
        Lista de padres seleccionados
    """
    
    padres = []
    
    for _ in range(n_padres):
        padre = seleccionar_por_torneo(poblacion, k)
        padres.append(padre)
    
    return padres


def seleccionar_parejas_torneo(
    poblacion: List[Dict],
    n_parejas: int,
    k: int = 5
) -> List[tuple]:
    """
    Selecciona parejas de padres para cruza mediante torneos.
    
    Cada pareja se forma con dos torneos independientes.
    
    Parameters:
    -----------
    poblacion : list
        Población de individuos
    n_parejas : int
        Número de parejas a formar
    k : int
        Tamaño del torneo
        
    Returns:
    --------
    list
        Lista de tuplas (padre1, padre2)
    """
    
    parejas = []
    
    for _ in range(n_parejas):
        padre1 = seleccionar_por_torneo(poblacion, k)
        padre2 = seleccionar_por_torneo(poblacion, k)
        
        parejas.append((padre1, padre2))
    
    return parejas