"""
Evaluador de población: calcula fitness de todos los individuos.

Funciones principales:
- evaluar_poblacion: evalúa todos los individuos de una población
- evaluar_individuo: evalúa un solo individuo
"""

import pandas as pd
from typing import Dict, List
import sys
sys.path.append('..')

from fitness.init import calcular_fitness_total


def evaluar_poblacion(
    poblacion: List[Dict],
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict,
    requerimientos: pd.DataFrame,
    verbose: bool = False
) -> List[Dict]:
    """
    Evalúa todos los individuos de una población.
    
    Proceso:
    1. Calcular fitness de cada individuo
    2. Ordenar por fitness (descendente: mayor fitness primero)
    3. Asignar ranking
    4. Retornar población evaluada y ordenada
    
    Parameters:
    -----------
    poblacion : list
        Lista de individuos (cromosomas)
    catalogo : pd.DataFrame
        Catálogo de productos
    config : dict
        Configuración del AG
    entrada_usuario : dict
        Datos de entrada del usuario
    requerimientos : pd.DataFrame
        Tabla de requerimientos nutricionales
    verbose : bool
        Si True, imprime progreso
        
    Returns:
    --------
    list
        Población evaluada y ordenada por fitness (mejor primero)
    """
    
    n_individuos = len(poblacion)
    
    if verbose:
        print(f"\n📊 Evaluando población de {n_individuos} individuos...")
    
    # Evaluar cada individuo
    for i, individuo in enumerate(poblacion):
        # Calcular fitness
        evaluar_individuo(
            individuo=individuo,
            catalogo=catalogo,
            config=config,
            entrada_usuario=entrada_usuario,
            requerimientos=requerimientos
        )
        
        # Progreso
        if verbose and (i + 1) % 20 == 0:
            print(f"  Evaluados {i + 1}/{n_individuos} individuos...")
    
    # Ordenar población por fitness (descendente)
    poblacion_ordenada = sorted(
        poblacion,
        key=lambda ind: ind['metadata']['fitness'],
        reverse=True  # Mayor fitness primero
    )
    
    # Asignar ranking
    for rank, individuo in enumerate(poblacion_ordenada, 1):
        individuo['metadata']['ranking'] = rank
    
    if verbose:
        print(f"✅ Población evaluada y ordenada")
        print(f"\n📈 Estadísticas de fitness:")
        print_estadisticas_fitness(poblacion_ordenada)
    
    return poblacion_ordenada


def evaluar_individuo(
    individuo: Dict,
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict,
    requerimientos: pd.DataFrame
) -> float:
    """
    Evalúa un solo individuo (calcula su fitness).
    
    Esta función es wrapper de calcular_fitness_total que además
    actualiza el metadata del individuo.
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma a evaluar
    catalogo : pd.DataFrame
        Catálogo de productos
    config : dict
        Configuración
    entrada_usuario : dict
        Datos de usuario
    requerimientos : pd.DataFrame
        Requerimientos nutricionales
        
    Returns:
    --------
    float
        Fitness del individuo
    """
    
    # Calcular fitness total
    fitness = calcular_fitness_total(
        individuo=individuo,
        catalogo=catalogo,
        config=config,
        entrada_usuario=entrada_usuario,
        requerimientos=requerimientos
    )
    
    # Ya se guarda en metadata dentro de calcular_fitness_total,
    # pero lo retornamos por conveniencia
    return fitness


def print_estadisticas_fitness(poblacion: List[Dict]) -> None:
    """
    Imprime estadísticas de fitness de la población.
    
    Parameters:
    -----------
    poblacion : list
        Población evaluada
    """
    
    import numpy as np
    
    fitness_values = [ind['metadata']['fitness'] for ind in poblacion]
    
    print(f"  - Mejor fitness:    {max(fitness_values):.4f}")
    print(f"  - Peor fitness:     {min(fitness_values):.4f}")
    print(f"  - Fitness promedio: {np.mean(fitness_values):.4f}")
    print(f"  - Desv. estándar:   {np.std(fitness_values):.4f}")
    
    # Fitness del mejor individuo por componente
    mejor_individuo = poblacion[0]  # Ya está ordenado
    componentes = mejor_individuo['metadata']['fitness_componentes']
    
    print(f"\n  Componentes del mejor individuo:")
    print(f"    - Costo:        {componentes['costo']:.4f}")
    print(f"    - Nutrición:    {componentes['nutricion']:.4f}")
    print(f"    - Desperdicio:  {componentes['desperdicio']:.4f}")
    print(f"    - Cobertura:    {componentes['cobertura']:.4f}")
    print(f"    - Satisfacción: {componentes['satisfaccion']:.4f}")


def obtener_mejor_individuo(poblacion: List[Dict]) -> Dict:
    """
    Obtiene el mejor individuo de la población.
    
    IMPORTANTE: La población debe estar ordenada primero.
    
    Parameters:
    -----------
    poblacion : list
        Población (idealmente ordenada)
        
    Returns:
    --------
    dict
        Mejor individuo
    """
    
    # Si no está ordenada, ordenar por fitness
    mejor = max(poblacion, key=lambda ind: ind['metadata']['fitness'])
    return mejor


def obtener_peor_individuo(poblacion: List[Dict]) -> Dict:
    """
    Obtiene el peor individuo de la población.
    
    Parameters:
    -----------
    poblacion : list
        Población
        
    Returns:
    --------
    dict
        Peor individuo
    """
    
    peor = min(poblacion, key=lambda ind: ind['metadata']['fitness'])
    return peor


def obtener_estadisticas_generacion(poblacion: List[Dict]) -> Dict:
    """
    Obtiene estadísticas completas de una generación.
    
    Parameters:
    -----------
    poblacion : list
        Población evaluada
        
    Returns:
    --------
    dict
        Diccionario con estadísticas
    """
    
    import numpy as np
    
    fitness_values = [ind['metadata']['fitness'] for ind in poblacion]
    
    # Obtener componentes de fitness del mejor individuo
    mejor = obtener_mejor_individuo(poblacion)
    componentes_mejor = mejor['metadata']['fitness_componentes']
    
    estadisticas = {
        'fitness': {
            'mejor': float(max(fitness_values)),
            'peor': float(min(fitness_values)),
            'promedio': float(np.mean(fitness_values)),
            'mediana': float(np.median(fitness_values)),
            'desviacion': float(np.std(fitness_values))
        },
        'componentes_mejor': componentes_mejor,
        'costo_mejor': mejor['metadata'].get('costo_total', 0),
        'violaciones': {
            'individuos_con_violaciones': sum(
                1 for ind in poblacion 
                if len(ind['metadata']['violaciones']) > 0
            ),
            'total_violaciones': sum(
                len(ind['metadata']['violaciones']) 
                for ind in poblacion
            )
        }
    }
    
    return estadisticas