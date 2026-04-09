"""
Mutación: Cambio de marca.

Operación:
- Selecciona un gen aleatorio
- Cambia la marca: genérica ↔ media ↔ premium

Útil para:
- Explorar trade-off costo vs. calidad
- Ajustar presupuesto manteniendo productos
"""

import numpy as np
from typing import Dict


def mutar_cambio_marca(
    individuo: Dict,
    probabilidad: float = 0.1
) -> Dict:
    """
    Muta un individuo cambiando la marca de un producto.
    
    Estrategia:
    1. Para cada gen, con cierta probabilidad:
       - Cambiar a una marca diferente (genérica/media/premium)
       - Preferiblemente a marca adyacente (genérica→media, media→premium)
    
    Marcas disponibles:
    - 'generica': Precio más bajo
    - 'media': Precio intermedio
    - 'premium': Precio más alto, mayor calidad
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma a mutar
    probabilidad : float
        Probabilidad de mutar cada gen
        
    Returns:
    --------
    dict
        Individuo mutado
    """
    
    import copy
    individuo_mutado = copy.deepcopy(individuo)
    
    marcas = ['generica', 'media', 'premium']
    
    for idx, gen in enumerate(individuo_mutado['genes']):
        if np.random.random() < probabilidad:
            # Mutar marca de este gen
            
            marca_actual = gen['marca']
            
            # Estrategia 1 (70%): Cambiar a marca adyacente
            # Estrategia 2 (30%): Cambiar a cualquier otra marca
            
            if np.random.random() < 0.7:
                # Cambio adyacente
                nueva_marca = cambiar_marca_adyacente(marca_actual, marcas)
            else:
                # Cambio aleatorio
                nueva_marca = cambiar_marca_aleatoria(marca_actual, marcas)
            
            # Actualizar gen
            individuo_mutado['genes'][idx]['marca'] = nueva_marca
    
    # Actualizar metadata
    individuo_mutado['metadata']['fue_mutado'] = True
    individuo_mutado['metadata']['tipo_mutacion'] = 'cambio_marca'
    
    return individuo_mutado


def cambiar_marca_adyacente(marca_actual: str, marcas: list) -> str:
    """
    Cambia a una marca adyacente en la jerarquía.
    
    genérica ↔ media ↔ premium
    
    Parameters:
    -----------
    marca_actual : str
        Marca actual
    marcas : list
        Lista de marcas disponibles
        
    Returns:
    --------
    str
        Nueva marca
    """
    
    idx_actual = marcas.index(marca_actual)
    
    # Determinar dirección (subir o bajar)
    if idx_actual == 0:
        # Genérica → solo puede subir a media
        return marcas[1]
    elif idx_actual == 2:
        # Premium → solo puede bajar a media
        return marcas[1]
    else:
        # Media → puede subir o bajar
        direccion = np.random.choice([-1, 1])
        return marcas[idx_actual + direccion]


def cambiar_marca_aleatoria(marca_actual: str, marcas: list) -> str:
    """
    Cambia a cualquier marca diferente de la actual.
    
    Parameters:
    -----------
    marca_actual : str
        Marca actual
    marcas : list
        Lista de marcas disponibles
        
    Returns:
    --------
    str
        Nueva marca
    """
    
    opciones = [m for m in marcas if m != marca_actual]
    return np.random.choice(opciones)