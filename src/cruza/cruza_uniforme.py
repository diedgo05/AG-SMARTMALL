"""
Operador de cruza uniforme.

Proceso:
1. Para cada gen (posición en el cromosoma):
   - Lanzar moneda (probabilidad 0.5)
   - Si cara: hijo1 hereda de padre1, hijo2 hereda de padre2
   - Si cruz: hijo1 hereda de padre2, hijo2 hereda de padre1

Ventajas:
- Máxima diversidad genética
- Bueno para problemas donde no hay dependencias entre genes adyacentes

Desventajas:
- Puede romper bloques de genes que funcionan bien juntos
"""

import numpy as np
from typing import Dict, Tuple
import copy


def cruzar_uniforme(
    padre1: Dict,
    padre2: Dict,
    probabilidad_cruza: float = 0.8,
    probabilidad_heredar_p1: float = 0.5
) -> Tuple[Dict, Dict]:
    """
    Realiza cruza uniforme entre dos padres.
    
    Parameters:
    -----------
    padre1 : dict
        Primer padre
    padre2 : dict
        Segundo padre
    probabilidad_cruza : float
        Probabilidad de que ocurra cruza
    probabilidad_heredar_p1 : float
        Probabilidad de heredar de padre1 (default: 0.5 = equitativo)
        
    Returns:
    --------
    tuple
        (hijo1, hijo2)
        
    Ejemplo:
    --------
    Padre1: [A B C D E F G H I J K L M N O P Q R S T]
    Padre2: [a b c d e f g h i j k l m n o p q r s t]
    
    Máscara aleatoria: [1 0 1 1 0 0 1 0 1 0 1 1 0 1 0 0 1 1 0 1]
    (1 = heredar de padre1, 0 = heredar de padre2)
    
    Hijo1: [A b C D e f G h I j K L m N o p Q R s T]
    Hijo2: [a B c d E F g H i J k l M n O P q r S t]
    """
    
    # Decidir si realizar cruza
    if np.random.random() > probabilidad_cruza:
        return copy.deepcopy(padre1), copy.deepcopy(padre2)
    
    n_genes = len(padre1['genes'])
    
    # Crear máscara de herencia (True = heredar de padre1)
    mascara = np.random.random(n_genes) < probabilidad_heredar_p1
    
    # Crear genes de hijos
    genes_hijo1 = np.array([
        padre1['genes'][i] if mascara[i] else padre2['genes'][i]
        for i in range(n_genes)
    ], dtype=object)
    
    genes_hijo2 = np.array([
        padre2['genes'][i] if mascara[i] else padre1['genes'][i]
        for i in range(n_genes)
    ], dtype=object)
    
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
            'origen': 'cruza_uniforme'
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
            'origen': 'cruza_uniforme'
        }
    }
    
    # Manejar duplicados
    from .cruza_dos_puntos import manejar_duplicados
    hijo1 = manejar_duplicados(hijo1)
    hijo2 = manejar_duplicados(hijo2)
    
    return hijo1, hijo2