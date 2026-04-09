"""
Mutación: Cambio de cantidad.

Operación:
- Selecciona un gen aleatorio
- Incrementa o decrementa la cantidad en ±1 unidad
- Respeta límites mínimos y máximos razonables

Útil para:
- Ajuste fino de cantidades
- Balancear presupuesto
"""

import numpy as np
from typing import Dict


def mutar_cambio_cantidad(
    individuo: Dict,
    probabilidad: float = 0.1,
    cantidad_min: float = 0.5,
    cantidad_max: float = 10.0,
    incremento_max: float = 2.0
) -> Dict:
    """
    Muta un individuo cambiando la cantidad de un producto.
    
    Estrategia:
    1. Para cada gen, con cierta probabilidad:
       - Generar incremento aleatorio: [-incremento_max, +incremento_max]
       - Aplicar incremento a cantidad actual
       - Limitar a rango [cantidad_min, cantidad_max]
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma a mutar
    probabilidad : float
        Probabilidad de mutar cada gen
    cantidad_min : float
        Cantidad mínima permitida (default: 0.5)
    cantidad_max : float
        Cantidad máxima permitida (default: 10.0)
    incremento_max : float
        Incremento/decremento máximo (default: 2.0)
        
    Returns:
    --------
    dict
        Individuo mutado
    """
    
    import copy
    individuo_mutado = copy.deepcopy(individuo)
    
    for idx, gen in enumerate(individuo_mutado['genes']):
        if np.random.random() < probabilidad:
            # Mutar cantidad de este gen
            
            cantidad_actual = gen['cantidad']
            
            # Generar incremento aleatorio
            incremento = np.random.uniform(-incremento_max, incremento_max)
            
            # Aplicar incremento
            nueva_cantidad = cantidad_actual + incremento
            
            # Limitar a rango válido
            nueva_cantidad = max(cantidad_min, min(cantidad_max, nueva_cantidad))
            
            # Redondear a 2 decimales
            nueva_cantidad = round(nueva_cantidad, 2)
            
            # Actualizar gen
            individuo_mutado['genes'][idx]['cantidad'] = nueva_cantidad
    
    # Actualizar metadata
    individuo_mutado['metadata']['fue_mutado'] = True
    individuo_mutado['metadata']['tipo_mutacion'] = 'cambio_cantidad'
    
    return individuo_mutado