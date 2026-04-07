"""
Generador de población inicial para el Algoritmo Genético.
"""

import numpy as np
import pandas as pd
from typing import Dict, List
from .generador_individuo import generar_individuo_aleatorio


def generar_poblacion_inicial(
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict,
    seed: int = None
) -> List[Dict]:
    """
    Genera población inicial de individuos (listas de compras).
    
    Parameters:
    -----------
    catalogo : pd.DataFrame
        Catálogo de productos
    config : dict
        Configuración del AG
    entrada_usuario : dict
        Datos de entrada del usuario
    seed : int, optional
        Semilla para reproducibilidad
        
    Returns:
    --------
    list
        Lista de individuos (cromosomas)
        
    Proceso:
    --------
    1. Generar N individuos aleatorios (N = tamaño población)
    2. Asegurar diversidad (no dos individuos idénticos)
    3. Retornar población
    """
    
    if seed is not None:
        np.random.seed(seed)
    
    tamaño_poblacion = config['poblacion']['tamaño']
    poblacion = []
    
    print(f"Generando población inicial de {tamaño_poblacion} individuos...")
    
    for i in range(tamaño_poblacion):
        # Generar individuo con semilla diferente para cada uno
        individuo = generar_individuo_aleatorio(
            catalogo=catalogo,
            config=config,
            entrada_usuario=entrada_usuario,
            seed=seed + i if seed is not None else None
        )
        
        # Marcar generación 0
        individuo['metadata']['generacion'] = 0
        
        poblacion.append(individuo)
        
        # Progreso
        if (i + 1) % 20 == 0:
            print(f"  Generados {i + 1}/{tamaño_poblacion} individuos...")
    
    print(f"✅ Población inicial generada: {len(poblacion)} individuos")
    
    # Verificar diversidad
    verificar_diversidad_poblacion(poblacion)
    
    return poblacion


def verificar_diversidad_poblacion(poblacion: List[Dict]) -> None:
    """
    Verifica que los individuos sean diversos (no todos iguales).
    
    Imprime estadísticas de diversidad.
    """
    
    n_individuos = len(poblacion)
    
    # Verificar cuántos individuos tienen exactamente los mismos productos
    productos_por_individuo = []
    
    for individuo in poblacion:
        ids_productos = sorted([gen['id_producto'] for gen in individuo['genes']])
        productos_por_individuo.append(tuple(ids_productos))
    
    # Contar individuos únicos
    individuos_unicos = len(set(productos_por_individuo))
    
    print(f"\n📊 Diversidad de población:")
    print(f"  - Total individuos: {n_individuos}")
    print(f"  - Combinaciones únicas de productos: {individuos_unicos}")
    print(f"  - Diversidad: {(individuos_unicos/n_individuos)*100:.1f}%")
    
    if individuos_unicos < n_individuos * 0.8:
        print("  ⚠️  ADVERTENCIA: Baja diversidad en población inicial")