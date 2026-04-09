"""
Operador de cruza de dos puntos.

Proceso:
1. Seleccionar dos puntos de corte aleatorios en el cromosoma
2. Intercambiar el segmento entre los dos puntos
3. Hijo1 = [Padre1_seg1] + [Padre2_seg2] + [Padre1_seg3]
4. Hijo2 = [Padre2_seg1] + [Padre1_seg2] + [Padre2_seg3]
5. Manejar productos duplicados

Ventajas:
- Preserva bloques de genes que funcionan bien juntos
- Mejor que un punto para problemas complejos
- Balance entre exploración y explotación
"""

import numpy as np
from typing import Dict, Tuple
import copy


def cruzar_dos_puntos(
    padre1: Dict,
    padre2: Dict,
    probabilidad_cruza: float = 0.8
) -> Tuple[Dict, Dict]:
    """
    Realiza cruza de dos puntos entre dos padres.
    
    Parameters:
    -----------
    padre1 : dict
        Primer padre (cromosoma)
    padre2 : dict
        Segundo padre (cromosoma)
    probabilidad_cruza : float
        Probabilidad de que ocurra la cruza (default: 0.8)
        Si no ocurre, los hijos son copias de los padres
        
    Returns:
    --------
    tuple
        (hijo1, hijo2) - Dos nuevos individuos
        
    Ejemplo:
    --------
    Padre1: [A B C D E F G H I J K L M N O P Q R S T]
    Padre2: [a b c d e f g h i j k l m n o p q r s t]
    
    Puntos de corte: posición 5 y 15
    
    Hijo1: [A B C D E | f g h i j k l m n o | P Q R S T]
    Hijo2: [a b c d e | F G H I J K L M N O | p q r s t]
    """
    
    # Decidir si realizar cruza o retornar copias
    if np.random.random() > probabilidad_cruza:
        # No realizar cruza: retornar copias de padres
        return copiar_individuo(padre1), copiar_individuo(padre2)
    
    # Longitud del cromosoma (fija: 20 genes)
    n_genes = len(padre1['genes'])
    
    # Seleccionar dos puntos de corte aleatorios
    punto1, punto2 = seleccionar_puntos_corte(n_genes)
    
    # Crear hijos mediante cruza
    genes_hijo1 = np.concatenate([
        padre1['genes'][:punto1],      # Segmento 1 de padre1
        padre2['genes'][punto1:punto2], # Segmento 2 de padre2
        padre1['genes'][punto2:]        # Segmento 3 de padre1
    ])
    
    genes_hijo2 = np.concatenate([
        padre2['genes'][:punto1],      # Segmento 1 de padre2
        padre1['genes'][punto1:punto2], # Segmento 2 de padre1
        padre2['genes'][punto2:]        # Segmento 3 de padre2
    ])
    
    # Crear estructuras de hijos
    hijo1 = crear_individuo_desde_genes(genes_hijo1, padre1, padre2)
    hijo2 = crear_individuo_desde_genes(genes_hijo2, padre2, padre1)
    
    # Manejar productos duplicados (si el mismo producto aparece 2+ veces)
    hijo1 = manejar_duplicados(hijo1)
    hijo2 = manejar_duplicados(hijo2)
    
    return hijo1, hijo2


def seleccionar_puntos_corte(n_genes: int) -> Tuple[int, int]:
    """
    Selecciona dos puntos de corte aleatorios.
    
    Asegura que:
    - punto1 < punto2
    - Los segmentos no sean demasiado pequeños (mínimo 2 genes por segmento)
    
    Parameters:
    -----------
    n_genes : int
        Número de genes en el cromosoma
        
    Returns:
    --------
    tuple
        (punto1, punto2) donde punto1 < punto2
    """
    
    # Asegurar segmentos mínimos de 2 genes
    min_segmento = 2
    
    # Punto1 entre [min_segmento, n_genes - 2*min_segmento]
    punto1 = np.random.randint(min_segmento, n_genes - 2*min_segmento)
    
    # Punto2 entre [punto1 + min_segmento, n_genes - min_segmento]
    punto2 = np.random.randint(punto1 + min_segmento, n_genes - min_segmento + 1)
    
    return punto1, punto2


def crear_individuo_desde_genes(
    genes: np.ndarray,
    padre1: Dict,
    padre2: Dict
) -> Dict:
    """
    Crea un individuo completo a partir de un array de genes.
    
    Parameters:
    -----------
    genes : np.ndarray
        Array de genes (productos)
    padre1 : dict
        Primer padre (para heredar generación)
    padre2 : dict
        Segundo padre
        
    Returns:
    --------
    dict
        Nuevo individuo
    """
    
    # Determinar generación (máximo de los padres + 1)
    generacion_padre1 = padre1['metadata'].get('generacion', 0)
    generacion_padre2 = padre2['metadata'].get('generacion', 0)
    nueva_generacion = max(generacion_padre1, generacion_padre2) + 1
    
    hijo = {
        'genes': genes,
        'metadata': {
            'fitness': None,
            'fitness_componentes': {},
            'es_valido': True,
            'generacion': nueva_generacion,
            'violaciones': [],
            'costo_total': None,
            'origen': 'cruza'
        }
    }
    
    return hijo


def manejar_duplicados(individuo: Dict) -> Dict:
    """
    Maneja productos duplicados en el cromosoma.
    
    Estrategia:
    1. Identificar productos que aparecen más de una vez (mismo id_producto)
    2. Para duplicados:
       - Mantener el primero
       - Consolidar cantidades si es razonable
       - O reemplazar duplicados por productos únicos
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma potencialmente con duplicados
        
    Returns:
    --------
    dict
        Cromosoma sin duplicados (exactamente 20 genes únicos)
    """
    
    genes = individuo['genes']
    
    # Identificar productos únicos
    productos_vistos = {}  # {id_producto: [índices donde aparece]}
    
    for idx, gen in enumerate(genes):
        id_prod = gen['id_producto']
        if id_prod not in productos_vistos:
            productos_vistos[id_prod] = []
        productos_vistos[id_prod].append(idx)
    
    # Encontrar duplicados
    productos_duplicados = {
        id_prod: indices 
        for id_prod, indices in productos_vistos.items() 
        if len(indices) > 1
    }
    
    if not productos_duplicados:
        return individuo  # No hay duplicados
    
    # Estrategia: consolidar cantidades del duplicado en la primera ocurrencia
    # y marcar las demás para reemplazo
    indices_a_reemplazar = []
    
    for id_prod, indices in productos_duplicados.items():
        # Mantener primera ocurrencia, consolidar cantidades
        idx_principal = indices[0]
        cantidad_total = sum(genes[idx]['cantidad'] for idx in indices)
        
        # Actualizar cantidad en primera ocurrencia (con límite razonable)
        genes[idx_principal]['cantidad'] = min(cantidad_total, 10.0)
        
        # Marcar las demás para reemplazo
        indices_a_reemplazar.extend(indices[1:])
    
    # Reemplazar duplicados por genes únicos (sin implementar pool completo,
    # simplemente modificamos ligeramente para hacerlos "únicos")
    # En una implementación completa, buscaríamos productos del catálogo
    # Por ahora, simplemente incrementamos el id_producto ligeramente
    for idx in indices_a_reemplazar:
        # Estrategia simple: cambiar a un producto "cercano" incrementando ID
        genes[idx]['id_producto'] += np.random.randint(1, 10)
        # Nota: Esto es una simplificación. En producción, buscaríamos
        # en el catálogo productos no utilizados de la misma categoría
    
    individuo['genes'] = genes
    
    return individuo


def copiar_individuo(individuo: Dict) -> Dict:
    """
    Crea una copia profunda de un individuo.
    
    Importante: Usar deepcopy para evitar referencias compartidas.
    
    Parameters:
    -----------
    individuo : dict
        Individuo a copiar
        
    Returns:
    --------
    dict
        Copia del individuo
    """
    
    return copy.deepcopy(individuo)