"""
Componente de fitness: COBERTURA DE COMIDAS.

Objetivo: Maximizar la cobertura de comidas planificadas.

Métricas:
- ¿Los productos permiten preparar las comidas planificadas?
- Balance de categorías (proteínas, carbohidratos, vegetales, frutas)
- Diversidad de opciones

Fórmula:
    f_cobertura = (categorias_cubiertas / categorias_necesarias) × 
                  (comidas_posibles / comidas_planificadas)
"""

import numpy as np
import pandas as pd
from typing import Dict, Set


def calcular_fitness_cobertura(
    individuo: Dict,
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict
) -> float:
    """
    Calcula fitness basado en cobertura de comidas.
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma con genes
    catalogo : pd.DataFrame
        Catálogo con categorías
    config : dict
        Configuración
    entrada_usuario : dict
        Datos del usuario (comidas planificadas)
        
    Returns:
    --------
    float
        Fitness de cobertura en [0, 1]
        1.0 = cubre todas las comidas planificadas
    """
    
    comidas_planificadas = entrada_usuario['comidas_planificadas']
    
    # 1. Identificar categorías presentes en el individuo
    categorias_presentes = identificar_categorias_presentes(individuo, catalogo)
    
    # 2. Verificar balance nutricional por categoría
    balance = verificar_balance_categorias(categorias_presentes)
    
    # 3. Estimar número de comidas que pueden prepararse
    comidas_posibles = estimar_comidas_posibles(
        categorias_presentes,
        comidas_planificadas
    )
    
    # 4. Calcular fitness
    # Componente 1: Balance de categorías (40%)
    fitness_balance = balance['score']
    
    # Componente 2: Cobertura de comidas (60%)
    ratio_cobertura = min(1.0, comidas_posibles / comidas_planificadas)
    
    fitness = 0.4 * fitness_balance + 0.6 * ratio_cobertura
    
    # Guardar en metadata
    individuo['metadata']['cobertura'] = {
        'categorias_presentes': list(categorias_presentes),
        'balance': balance,
        'comidas_posibles': comidas_posibles,
        'comidas_planificadas': comidas_planificadas,
        'ratio_cobertura': ratio_cobertura
    }
    
    return min(1.0, max(0.0, fitness))


def identificar_categorias_presentes(
    individuo: Dict,
    catalogo: pd.DataFrame
) -> Set[str]:
    """
    Identifica qué categorías de alimentos están presentes en el individuo.
    
    Returns:
    --------
    set
        Conjunto de categorías presentes
    """
    
    categorias = set()
    
    for gen in individuo['genes']:
        id_producto = gen['id_producto']
        producto = catalogo[catalogo['id'] == id_producto].iloc[0]
        categorias.add(producto['categoria'])
    
    return categorias


def verificar_balance_categorias(categorias_presentes: Set[str]) -> Dict:
    """
    Verifica el balance de categorías alimenticias.
    
    Categorías esenciales para una dieta balanceada:
    - Proteínas (carnes, huevos, legumbres)
    - Carbohidratos (granos, pan, pasta)
    - Lácteos
    - Frutas
    - Verduras
    - Aceites/grasas saludables
    
    Returns:
    --------
    dict
        {'score': float, 'categorias_faltantes': list, 'categorias_cubiertas': list}
    """
    
    # Mapeo de categorías del catálogo a grupos nutricionales
    grupos_nutricionales = {
        'proteinas': ['Proteínas', 'Granos y Legumbres'],
        'carbohidratos': ['Granos y Legumbres', 'Panadería'],
        'lacteos': ['Lácteos'],
        'frutas': ['Frutas'],
        'verduras': ['Verduras'],
        'grasas': ['Aceites y Condimentos']
    }
    
    grupos_cubiertos = []
    grupos_faltantes = []
    
    for grupo, categorias_grupo in grupos_nutricionales.items():
        # ¿El individuo tiene al menos una categoría de este grupo?
        if any(cat in categorias_presentes for cat in categorias_grupo):
            grupos_cubiertos.append(grupo)
        else:
            grupos_faltantes.append(grupo)
    
    # Score = proporción de grupos cubiertos
    total_grupos = len(grupos_nutricionales)
    score = len(grupos_cubiertos) / total_grupos
    
    return {
        'score': score,
        'grupos_cubiertos': grupos_cubiertos,
        'grupos_faltantes': grupos_faltantes
    }


def estimar_comidas_posibles(
    categorias_presentes: Set[str],
    comidas_planificadas: int
) -> int:
    """
    Estima cuántas comidas pueden prepararse con los productos disponibles.
    
    Heurística simple:
    - Cada comida requiere al menos 2-3 categorías diferentes
    - Si hay buena diversidad, se pueden preparar más comidas
    
    Parameters:
    -----------
    categorias_presentes : set
        Categorías de alimentos disponibles
    comidas_planificadas : int
        Número de comidas a cubrir
        
    Returns:
    --------
    int
        Número estimado de comidas posibles
    """
    
    num_categorias = len(categorias_presentes)
    
    # Heurística basada en diversidad
    if num_categorias >= 8:
        # Excelente diversidad: puede cubrir todas las comidas
        comidas_posibles = comidas_planificadas
    elif num_categorias >= 6:
        # Buena diversidad: 80-100% de comidas
        comidas_posibles = int(comidas_planificadas * 0.9)
    elif num_categorias >= 4:
        # Diversidad moderada: 60-80% de comidas
        comidas_posibles = int(comidas_planificadas * 0.7)
    elif num_categorias >= 2:
        # Baja diversidad: 40-60% de comidas
        comidas_posibles = int(comidas_planificadas * 0.5)
    else:
        # Muy baja diversidad: <40% de comidas
        comidas_posibles = int(comidas_planificadas * 0.3)
    
    return max(1, comidas_posibles)
