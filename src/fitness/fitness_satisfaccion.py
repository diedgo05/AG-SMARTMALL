"""
Componente de fitness: SATISFACCIÓN DE PREFERENCIAS.

Objetivo: Maximizar la satisfacción de preferencias familiares.

Factores:
- Productos preferidos presentes
- Productos no deseados ausentes
- Calidad de marcas (genérica vs. premium)

Fórmula:
    f_satisfaccion = (preferencias_cumplidas / total_preferencias) × 
                     (1 - penalizacion_productos_no_deseados)
"""

import numpy as np
import pandas as pd
from typing import Dict, List


def calcular_fitness_satisfaccion(
    individuo: Dict,
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict
) -> float:
    """
    Calcula fitness basado en satisfacción de preferencias.
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma con genes
    catalogo : pd.DataFrame
        Catálogo de productos
    config : dict
        Configuración
    entrada_usuario : dict
        Preferencias del usuario
        
    Returns:
    --------
    float
        Fitness de satisfacción en [0, 1]
        1.0 = todas las preferencias satisfechas
    """
    
    preferencias = entrada_usuario.get('preferencias', {})
    
    productos_preferidos = preferencias.get('productos_preferidos', [])
    productos_evitar = preferencias.get('productos_evitar', [])
    prioridad_organico = preferencias.get('prioridad_organico', False)
    
    # Productos en el individuo
    productos_individuo = [gen['id_producto'] for gen in individuo['genes']]
    marcas_individuo = [gen['marca'] for gen in individuo['genes']]
    
    # COMPONENTE 1: Productos preferidos presentes (60% del peso)
    if productos_preferidos:
        presentes = [p for p in productos_preferidos if p in productos_individuo]
        ratio_preferidos = len(presentes) / len(productos_preferidos)
    else:
        ratio_preferidos = 1.0  # No hay preferencias, satisfacción neutra
    
    # COMPONENTE 2: Productos no deseados ausentes (30% del peso)
    if productos_evitar:
        no_deseados_presentes = [p for p in productos_evitar if p in productos_individuo]
        penalizacion_no_deseados = len(no_deseados_presentes) / len(productos_evitar)
    else:
        penalizacion_no_deseados = 0.0
    
    # COMPONENTE 3: Calidad de marcas (10% del peso)
    # Si prioridad_organico = True, premiar marcas premium
    if prioridad_organico:
        marcas_premium = sum(1 for m in marcas_individuo if m == 'premium')
        ratio_premium = marcas_premium / len(marcas_individuo)
    else:
        # Balance de marcas (ni todas genéricas ni todas premium)
        ratio_premium = 0.5  # Neutro
    
    # Calcular fitness final
    fitness = (
        0.60 * ratio_preferidos +
        0.30 * (1.0 - penalizacion_no_deseados) +
        0.10 * ratio_premium
    )
    
    # Guardar en metadata
    individuo['metadata']['satisfaccion'] = {
        'ratio_preferidos': ratio_preferidos,
        'productos_preferidos_presentes': len([p for p in productos_preferidos if p in productos_individuo]),
        'productos_preferidos_total': len(productos_preferidos),
        'productos_no_deseados_presentes': len([p for p in productos_evitar if p in productos_individuo]),
        'ratio_premium': ratio_premium
    }
    
    return min(1.0, max(0.0, fitness))