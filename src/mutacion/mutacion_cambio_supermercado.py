"""
Mutación: Cambio de supermercado.

Operación:
- Selecciona un gen aleatorio
- Cambia el supermercado donde se compra el producto
- Solo a supermercados donde el producto está disponible

Útil para:
- Optimizar logística de compra
- Explorar combinaciones de tiendas
"""

import numpy as np
import pandas as pd
from typing import Dict


def mutar_cambio_supermercado(
    individuo: Dict,
    catalogo: pd.DataFrame,
    probabilidad: float = 0.1
) -> Dict:
    """
    Muta un individuo cambiando el supermercado de compra.
    
    Estrategia:
    1. Para cada gen, con cierta probabilidad:
       - Obtener supermercados donde está disponible el producto
       - Cambiar a un supermercado diferente (si hay opciones)
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma a mutar
    catalogo : pd.DataFrame
        Catálogo de productos
    probabilidad : float
        Probabilidad de mutar cada gen
        
    Returns:
    --------
    dict
        Individuo mutado
    """
    
    import copy
    individuo_mutado = copy.deepcopy(individuo)
    
    for idx, gen in enumerate(individuo_mutado['genes']):
        if np.random.random() < probabilidad:
            # Mutar supermercado de este gen
            
            id_producto = gen['id_producto']
            supermercado_actual = gen['supermercado']
            
            # Obtener producto del catálogo
            producto = catalogo[catalogo['id'] == id_producto].iloc[0]
            supermercados_disponibles = producto['supermercados'].split(',')
            
            # Si hay más de un supermercado disponible
            if len(supermercados_disponibles) > 1:
                # Cambiar a un supermercado diferente
                opciones = [s for s in supermercados_disponibles if s != supermercado_actual]
                
                if opciones:
                    nuevo_supermercado = np.random.choice(opciones)
                    individuo_mutado['genes'][idx]['supermercado'] = nuevo_supermercado
    
    # Actualizar metadata
    individuo_mutado['metadata']['fue_mutado'] = True
    individuo_mutado['metadata']['tipo_mutacion'] = 'cambio_supermercado'
    
    return individuo_mutado