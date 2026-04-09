"""
Mutación: Cambio de producto.

Operación:
- Selecciona un gen aleatorio del cromosoma
- Reemplaza el producto por otro del catálogo
- Preferiblemente de la misma categoría para preservar balance

Útil para:
- Explorar alternativas dentro de la misma categoría
- Reemplazar productos sub-óptimos
"""

import numpy as np
import pandas as pd
from typing import Dict


def mutar_cambio_producto(
    individuo: Dict,
    catalogo: pd.DataFrame,
    entrada_usuario: Dict,
    probabilidad: float = 0.1
) -> Dict:
    """
    Muta un individuo cambiando un producto por otro.
    
    Estrategia:
    1. Seleccionar gen aleatorio a mutar
    2. Obtener categoría del producto actual
    3. Buscar productos candidatos de la misma categoría (sin alérgenos)
    4. Seleccionar producto de reemplazo aleatorio
    5. Reemplazar manteniendo cantidad y marca similar
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma a mutar
    catalogo : pd.DataFrame
        Catálogo de productos
    entrada_usuario : dict
        Datos del usuario (para filtrar alérgenos)
    probabilidad : float
        Probabilidad de mutar cada gen (default: 0.1)
        
    Returns:
    --------
    dict
        Individuo mutado
    """
    
    import copy
    individuo_mutado = copy.deepcopy(individuo)
    
    alergenos_prohibidos = entrada_usuario.get('alergenos_prohibidos', [])
    
    # Determinar qué genes mutar
    for idx, gen in enumerate(individuo_mutado['genes']):
        if np.random.random() < probabilidad:
            # Mutar este gen
            
            # Obtener información del producto actual
            id_actual = gen['id_producto']
            producto_actual = catalogo[catalogo['id'] == id_actual].iloc[0]
            categoria_actual = producto_actual['categoria']
            
            # Buscar candidatos de reemplazo (misma categoría, sin alérgenos)
            candidatos = catalogo[
                (catalogo['categoria'] == categoria_actual) &
                (catalogo['id'] != id_actual)  # No el mismo producto
            ]
            
            # Filtrar alérgenos
            if alergenos_prohibidos:
                candidatos_validos = []
                for _, candidato in candidatos.iterrows():
                    alergenos_str = candidato['alergenos']
                    
                    if pd.isna(alergenos_str) or alergenos_str == '':
                        candidatos_validos.append(candidato)
                    else:
                        alergenos_producto = [a.strip() for a in alergenos_str.split(',')]
                        if not any(a in alergenos_prohibidos for a in alergenos_producto):
                            candidatos_validos.append(candidato)
                
                candidatos = pd.DataFrame(candidatos_validos)
            
            if len(candidatos) > 0:
                # Seleccionar producto de reemplazo aleatorio
                nuevo_producto = candidatos.sample(n=1).iloc[0]
                
                # Actualizar gen
                individuo_mutado['genes'][idx]['id_producto'] = int(nuevo_producto['id'])
                
                # Mantener cantidad original (o ajustar ligeramente)
                # Mantener marca original
                # Actualizar supermercado si el nuevo producto no está disponible
                supermercados_disponibles = nuevo_producto['supermercados'].split(',')
                if gen['supermercado'] not in supermercados_disponibles:
                    individuo_mutado['genes'][idx]['supermercado'] = np.random.choice(
                        supermercados_disponibles
                    )
    
    # Actualizar metadata
    individuo_mutado['metadata']['fue_mutado'] = True
    individuo_mutado['metadata']['tipo_mutacion'] = 'cambio_producto'
    
    return individuo_mutado