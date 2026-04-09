"""
Operador de cruza de un punto.

Proceso:
1. Seleccionar un punto de corte aleatorio
2. Intercambiar segmentos después del punto
3. Hijo1 = [Padre1_antes] + [Padre2_después]
4. Hijo2 = [Padre2_antes] + [Padre1_después]

Más simple que dos puntos, pero puede ser menos efectiva.
"""

import numpy as np
from typing import Dict, Tuple
import copy


def cruzar_un_punto(
    padre1: Dict,
    padre2: Dict,
    probabilidad_cruza: float = 0.8
) -> Tuple[Dict, Dict]:
    """
    Realiza cruza de un punto entre dos padres.
    
    Parameters:
    -----------
    padre1 : dict
        Primer padre
    padre2 : dict
        Segundo padre
    probabilidad_cruza : float
        Probabilidad de cruza
        
    Returns:
    --------
    tuple
        (hijo1, hijo2)
        
    Ejemplo:
    --------
    Padre1: [A B C D E F G H I J K L M N O P Q R S T]
    Padre2: [a b c d e f g h i j k l m n o p q r s t]
    
    Punto de corte: posición 10
    
    Hijo1: [A B C D E F G H I J | k l m n o p q r s t]
    Hijo2: [a b c d e f g h i j | K L M N O P Q R S T]
    """
    
    # Decidir si realizar cruza
    if np.random.random() > probabilidad_cruza:
        return copy.deepcopy(padre1), copy.deepcopy(padre2)
    
    n_genes = len(padre1['genes'])
    
    # Seleccionar punto de corte (evitar extremos)
    punto_corte = np.random.randint(2, n_genes - 2)
    
    # Crear hijos
    genes_hijo1 = np.concatenate([
        padre1['genes'][:punto_corte],
        padre2['genes'][punto_corte:]
    ])
    
    genes_hijo2 = np.concatenate([
        padre2['genes'][:punto_corte],
        padre1['genes'][punto_corte:]
    ])
    
    # Crear individuos
    hijo1 = {
        'genes': genes_hijo1,
        'metadata': {
            'fitness': None,
            'fitness_componentes': {},
            'es_valido': True,
            'generacion': max(
                padre1['metadata'].get('generacion', 0),
                padre2['metadata'].get('generacion', 0)
            ) + 1,
            'violaciones': [],
            'costo_total': None,
            'origen': 'cruza_un_punto'
        }
    }
    
    hijo2 = {
        'genes': genes_hijo2,
        'metadata': {
            'fitness': None,
            'fitness_componentes': {},
            'es_valido': True,
            'generacion': max(
                padre1['metadata'].get('generacion', 0),
                padre2['metadata'].get('generacion', 0)
            ) + 1,
            'violaciones': [],
            'costo_total': None,
            'origen': 'cruza_un_punto'
        }
    }
    
    # Manejar duplicados
    from .cruza_dos_puntos import manejar_duplicados
    hijo1 = manejar_duplicados(hijo1)
    hijo2 = manejar_duplicados(hijo2)
    
    return hijo1, hijo2