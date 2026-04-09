"""
Aplicador de mutación combinada.

Aplica múltiples tipos de mutación según probabilidades configuradas.
Es el punto de entrada principal para mutar individuos y poblaciones.
"""

import numpy as np
import pandas as pd
from typing import Dict, List
import copy

from .mutacion_cambio_producto import mutar_cambio_producto
from .mutacion_cambio_cantidad import mutar_cambio_cantidad
from .mutacion_cambio_marca import mutar_cambio_marca
from .mutacion_cambio_supermercado import mutar_cambio_supermercado


def aplicar_mutacion(
    individuo: Dict,
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict
) -> Dict:
    """
    Aplica mutación a un individuo según configuración.
    
    Proceso:
    1. Determinar si el individuo será mutado (probabilidad global)
    2. Si se muta, aplicar uno o más tipos de mutación según sus probabilidades
    3. Actualizar metadata
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma a mutar
    catalogo : pd.DataFrame
        Catálogo de productos
    config : dict
        Configuración del AG (probabilidades de mutación)
    entrada_usuario : dict
        Datos del usuario
        
    Returns:
    --------
    dict
        Individuo (mutado o no)
    """
    
    # Obtener configuración de mutación
    config_mutacion = config['operadores']['mutacion']
    prob_mutacion_global = config_mutacion['probabilidad_global']
    prob_por_gen = config_mutacion['probabilidad_por_gen']
    tipos_mutacion = config_mutacion['tipos']
    
    # Decidir si mutar este individuo
    if np.random.random() > prob_mutacion_global:
        return individuo  # No mutar
    
    # El individuo será mutado
    individuo_mutado = copy.deepcopy(individuo)
    
    # Aplicar cada tipo de mutación según su probabilidad
    for tipo_mut in tipos_mutacion:
        tipo = tipo_mut['tipo']
        prob = tipo_mut['probabilidad']
        
        # ¿Aplicar este tipo de mutación?
        if np.random.random() < prob:
            
            if tipo == 'cambio_producto':
                individuo_mutado = mutar_cambio_producto(
                    individuo_mutado,
                    catalogo,
                    entrada_usuario,
                    probabilidad=prob_por_gen
                )
            
            elif tipo == 'cambio_cantidad':
                individuo_mutado = mutar_cambio_cantidad(
                    individuo_mutado,
                    probabilidad=prob_por_gen
                )
            
            elif tipo == 'cambio_marca':
                individuo_mutado = mutar_cambio_marca(
                    individuo_mutado,
                    probabilidad=prob_por_gen
                )
            
            elif tipo == 'cambio_supermercado':
                individuo_mutado = mutar_cambio_supermercado(
                    individuo_mutado,
                    catalogo,
                    probabilidad=prob_por_gen
                )
    
    # Marcar que fue mutado
    if 'mutaciones_aplicadas' not in individuo_mutado['metadata']:
        individuo_mutado['metadata']['mutaciones_aplicadas'] = []
    
    individuo_mutado['metadata']['fue_mutado'] = True
    
    return individuo_mutado


def aplicar_mutacion_poblacion(
    poblacion: List[Dict],
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict,
    verbose: bool = False
) -> List[Dict]:
    """
    Aplica mutación a toda una población.
    
    Parameters:
    -----------
    poblacion : list
        Lista de individuos
    catalogo : pd.DataFrame
        Catálogo de productos
    config : dict
        Configuración
    entrada_usuario : dict
        Datos del usuario
    verbose : bool
        Si True, imprime progreso
        
    Returns:
    --------
    list
        Población con individuos mutados
    """
    
    if verbose:
        print(f"\n🧬 Aplicando mutación a población de {len(poblacion)} individuos...")
    
    poblacion_mutada = []
    n_mutados = 0
    
    for individuo in poblacion:
        individuo_mutado = aplicar_mutacion(
            individuo=individuo,
            catalogo=catalogo,
            config=config,
            entrada_usuario=entrada_usuario
        )
        
        poblacion_mutada.append(individuo_mutado)
        
        if individuo_mutado['metadata'].get('fue_mutado', False):
            n_mutados += 1
    
    if verbose:
        tasa_mutacion = (n_mutados / len(poblacion)) * 100
        print(f"  ✅ Mutación aplicada: {n_mutados}/{len(poblacion)} individuos ({tasa_mutacion:.1f}%)")
    
    return poblacion_mutada


def calcular_estadisticas_mutacion(poblacion: List[Dict]) -> Dict:
    """
    Calcula estadísticas de mutación en la población.
    
    Parameters:
    -----------
    poblacion : list
        Población de individuos
        
    Returns:
    --------
    dict
        Estadísticas de mutación
    """
    
    total_individuos = len(poblacion)
    individuos_mutados = sum(
        1 for ind in poblacion 
        if ind['metadata'].get('fue_mutado', False)
    )
    
    # Contar por tipo de mutación
    tipos_aplicados = {}
    
    for individuo in poblacion:
        tipo_mut = individuo['metadata'].get('tipo_mutacion')
        if tipo_mut:
            tipos_aplicados[tipo_mut] = tipos_aplicados.get(tipo_mut, 0) + 1
    
    return {
        'total_individuos': total_individuos,
        'individuos_mutados': individuos_mutados,
        'tasa_mutacion': (individuos_mutados / total_individuos * 100) if total_individuos > 0 else 0,
        'tipos_aplicados': tipos_aplicados
    }