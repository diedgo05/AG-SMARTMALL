"""
Aplicador de operador de cruza.

Facilita la aplicación de cruza a una población completa.
"""

import numpy as np
from typing import Dict, List, Tuple, Callable

from .cruza_dos_puntos import cruzar_dos_puntos
from .cruza_un_punto import cruzar_un_punto
from .cruza_uniforme import cruzar_uniforme


def aplicar_cruza_poblacion(
    padres: List[Dict],
    config: Dict,
    tipo_cruza: str = 'dos_puntos'
) -> List[Dict]:
    """
    Aplica operador de cruza a una lista de padres seleccionados.
    
    Proceso:
    1. Emparejar padres de dos en dos
    2. Aplicar cruza a cada pareja
    3. Generar población de hijos
    
    Parameters:
    -----------
    padres : list
        Lista de individuos seleccionados (debe ser par)
    config : dict
        Configuración del AG
    tipo_cruza : str
        Tipo de cruza: 'dos_puntos', 'un_punto', 'uniforme'
        
    Returns:
    --------
    list
        Lista de hijos generados
    """
    
    # Obtener probabilidad de cruza de configuración
    prob_cruza = config['operadores']['cruza']['probabilidad']
    
    # Seleccionar función de cruza
    operador_cruza = obtener_operador_cruza(tipo_cruza)
    
    # Generar hijos
    hijos = []
    
    # Emparejar padres de dos en dos
    for i in range(0, len(padres) - 1, 2):
        padre1 = padres[i]
        padre2 = padres[i + 1]
        
        # Aplicar cruza
        hijo1, hijo2 = operador_cruza(padre1, padre2, prob_cruza)
        
        hijos.extend([hijo1, hijo2])
    
    # Si quedó un padre sin pareja (número impar), agregarlo como está
    if len(padres) % 2 == 1:
        import copy
        hijos.append(copy.deepcopy(padres[-1]))
    
    return hijos


def obtener_operador_cruza(tipo: str) -> Callable:
    """
    Obtiene la función de cruza según el tipo especificado.
    
    Parameters:
    -----------
    tipo : str
        Tipo de cruza
        
    Returns:
    --------
    callable
        Función de cruza
    """
    
    operadores = {
        'dos_puntos': cruzar_dos_puntos,
        'un_punto': cruzar_un_punto,
        'uniforme': cruzar_uniforme
    }
    
    if tipo not in operadores:
        raise ValueError(
            f"Tipo de cruza '{tipo}' no reconocido. "
            f"Opciones: {list(operadores.keys())}"
        )
    
    return operadores[tipo]


def generar_parejas_aleatorias(poblacion: List[Dict]) -> List[Tuple[Dict, Dict]]:
    """
    Genera parejas aleatorias de individuos para cruza.
    
    Útil para cruza con selección aleatoria de parejas.
    
    Parameters:
    -----------
    poblacion : list
        Población de individuos
        
    Returns:
    --------
    list
        Lista de tuplas (padre1, padre2)
    """
    
    # Mezclar población
    indices = np.random.permutation(len(poblacion))
    poblacion_mezclada = [poblacion[i] for i in indices]
    
    # Crear parejas
    parejas = []
    for i in range(0, len(poblacion_mezclada) - 1, 2):
        parejas.append((poblacion_mezclada[i], poblacion_mezclada[i + 1]))
    
    return parejas