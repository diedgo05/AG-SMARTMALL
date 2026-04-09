"""
Elitismo: Preservación de los mejores individuos.

Mecanismo:
1. Identificar los n mejores individuos de la generación actual
2. Garantizar que pasan a la siguiente generación sin modificación
3. Evita perder buenas soluciones por azar

Ventajas:
- Garantiza monotonía: fitness nunca empeora
- Acelera convergencia
- Preserva soluciones de calidad

Recomendación: 5-10% de la población
"""

import numpy as np
from typing import Dict, List
import copy


def obtener_elite(
    poblacion: List[Dict],
    n_elite: int
) -> List[Dict]:
    """
    Obtiene los n mejores individuos de la población.
    
    IMPORTANTE: La población debe estar ordenada por fitness (mayor primero)
    o se ordenará aquí.
    
    Parameters:
    -----------
    poblacion : list
        Población de individuos
    n_elite : int
        Número de individuos elite a obtener
        
    Returns:
    --------
    list
        Lista de n mejores individuos (copias profundas)
    """
    
    # Ordenar por fitness si no está ordenada
    poblacion_ordenada = sorted(
        poblacion,
        key=lambda ind: ind['metadata']['fitness'],
        reverse=True  # Mayor fitness primero
    )
    
    # Tomar los n mejores
    elite = poblacion_ordenada[:n_elite]
    
    # Retornar copias profundas para evitar modificaciones accidentales
    elite_copias = [copy.deepcopy(ind) for ind in elite]
    
    # Marcar como elite en metadata
    for ind in elite_copias:
        ind['metadata']['es_elite'] = True
    
    return elite_copias


def aplicar_poda(
    poblacion_actual: List[Dict],
    poblacion_hijos: List[Dict],
    proporcion_elite: float = 0.1
) -> List[Dict]:
    """
    Aplica elitismo combinando elite de población actual con hijos.
    
    Proceso:
    1. Calcular n_elite = proporcion_elite × tamaño_población
    2. Obtener los n_elite mejores de población_actual
    3. Obtener los mejores hijos para completar la población
    4. Retornar nueva generación = elite + mejores_hijos
    
    Parameters:
    -----------
    poblacion_actual : list
        Generación actual (padres)
    poblacion_hijos : list
        Hijos generados por cruza y mutación
    proporcion_elite : float
        Proporción de elite a preservar (default: 0.1 = 10%)
        
    Returns:
    --------
    list
        Nueva generación con elitismo aplicado
    """
    
    tamaño_poblacion = len(poblacion_actual)
    n_elite = int(tamaño_poblacion * proporcion_elite)
    n_elite = max(1, n_elite)  # Al menos 1 elite
    
    # Obtener elite de población actual
    elite = obtener_elite(poblacion_actual, n_elite)
    
    # Ordenar hijos por fitness
    hijos_ordenados = sorted(
        poblacion_hijos,
        key=lambda ind: ind['metadata']['fitness'],
        reverse=True
    )
    
    # Calcular cuántos hijos necesitamos para completar población
    n_hijos_necesarios = tamaño_poblacion - n_elite
    
    # Tomar los mejores hijos
    mejores_hijos = hijos_ordenados[:n_hijos_necesarios]
    
    # Combinar elite + mejores hijos
    nueva_generacion = elite + mejores_hijos
    
    return nueva_generacion


def calcular_estadisticas_poda(poblacion: List[Dict]) -> Dict:
    """
    Calcula estadísticas sobre individuos elite en la población.
    
    Parameters:
    -----------
    poblacion : list
        Población de individuos
        
    Returns:
    --------
    dict
        Estadísticas de elitismo
    """
    
    individuos_elite = [
        ind for ind in poblacion 
        if ind['metadata'].get('es_elite', False)
    ]
    
    return {
        'total_individuos': len(poblacion),
        'individuos_elite': len(individuos_elite),
        'proporcion_elite': len(individuos_elite) / len(poblacion) if poblacion else 0,
        'fitness_promedio_elite': np.mean([
            ind['metadata']['fitness'] 
            for ind in individuos_elite
        ]) if individuos_elite else 0
    }