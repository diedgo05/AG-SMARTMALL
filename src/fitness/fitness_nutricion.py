"""
Componente de fitness: NUTRICIÓN.

Objetivo: Maximizar el cumplimiento de requerimientos nutricionales.

Métricas consideradas:
- Calorías totales
- Proteínas (g)
- Carbohidratos (g)
- Grasas (g)
- Fibra (g)

Fórmula:
    Para cada nutriente: cumplimiento = min(aporte / requerimiento, 1.0)
    f_nutricion = promedio(cumplimientos)
    
Penalizaciones:
- Deficiencia crítica (<80% de algún nutriente esencial)
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple


def calcular_fitness_nutricion(
    individuo: Dict,
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict,
    requerimientos: pd.DataFrame
) -> float:
    """
    Calcula fitness basado en cumplimiento nutricional.
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma con genes
    catalogo : pd.DataFrame
        Catálogo con información nutricional
    config : dict
        Configuración (penalizaciones)
    entrada_usuario : dict
        Composición familiar y periodo
    requerimientos : pd.DataFrame
        Tabla de requerimientos nutricionales
        
    Returns:
    --------
    float
        Fitness nutricional en [0, 1]
        1.0 = cumple 100% de todos los requerimientos
    """
    
    # 1. Calcular requerimientos totales de la familia
    requerimientos_totales = calcular_requerimientos_familia(
        entrada_usuario,
        requerimientos
    )
    
    # 2. Calcular aporte nutricional del individuo
    aporte_total = calcular_aporte_nutricional(individuo, catalogo)
    
    # 3. Calcular cumplimiento por nutriente
    cumplimientos = {}
    
    nutrientes = ['calorias', 'proteinas_g', 'carbohidratos_g', 'grasas_g', 'fibra_g']
    
    for nutriente in nutrientes:
        requerido = requerimientos_totales[nutriente]
        aportado = aporte_total[nutriente]
        
        # Cumplimiento = min(aportado / requerido, 1.0)
        # No premiamos exceso (más no es necesariamente mejor)
        cumplimiento = min(aportado / requerido, 1.0) if requerido > 0 else 1.0
        
        cumplimientos[nutriente] = cumplimiento
    
    # 4. Detectar deficiencias críticas
    umbral_critico = config['restricciones']['umbral_nutricion_minimo']  # 0.80
    deficiencias_criticas = []
    
    for nutriente, cumplimiento in cumplimientos.items():
        if cumplimiento < umbral_critico:
            deficiencias_criticas.append({
                'nutriente': nutriente,
                'cumplimiento': cumplimiento,
                'requerido': requerimientos_totales[nutriente],
                'aportado': aporte_total[nutriente]
            })
    
    # 5. Calcular fitness
    # Fitness base = promedio de cumplimientos
    fitness_base = np.mean(list(cumplimientos.values()))
    
    # Penalizar deficiencias críticas
    if deficiencias_criticas:
        penalizacion = len(deficiencias_criticas) * 0.15  # -15% por cada deficiencia
        fitness = max(0.0, fitness_base - penalizacion)
        
        # Registrar violaciones
        for deficiencia in deficiencias_criticas:
            individuo['metadata']['violaciones'].append({
                'tipo': 'deficiencia_nutricional',
                'severidad': 'alta',
                'detalle': f"{deficiencia['nutriente']}: {deficiencia['cumplimiento']*100:.1f}%"
            })
    else:
        fitness = fitness_base
    
    # Guardar detalles en metadata
    individuo['metadata']['nutricion'] = {
        'cumplimientos': cumplimientos,
        'deficiencias_criticas': deficiencias_criticas,
        'aporte_total': aporte_total
    }
    
    return min(1.0, max(0.0, fitness))


def calcular_requerimientos_familia(
    entrada_usuario: Dict,
    requerimientos: pd.DataFrame
) -> Dict:
    """
    Calcula requerimientos nutricionales totales para la familia
    durante el periodo especificado.
    
    Parameters:
    -----------
    entrada_usuario : dict
        Composición familiar y periodo
    requerimientos : pd.DataFrame
        Tabla de requerimientos por grupo demográfico
        
    Returns:
    --------
    dict
        Requerimientos totales: {'calorias': X, 'proteinas_g': Y, ...}
    """
    
    composicion = entrada_usuario['composicion_familia']
    periodo_dias = entrada_usuario['periodo_dias']
    
    totales = {
        'calorias': 0,
        'proteinas_g': 0,
        'carbohidratos_g': 0,
        'grasas_g': 0,
        'fibra_g': 0
    }
    
    for miembro in composicion:
        edad_grupo = miembro['edad_grupo']
        genero = miembro['genero']
        
        # Buscar en tabla de requerimientos
        req = requerimientos[
            (requerimientos['edad_grupo'] == edad_grupo) &
            (requerimientos['genero'] == genero)
        ]
        
        if len(req) == 0:
            # Fallback: usar requerimientos de adulto promedio
            req = requerimientos[
                (requerimientos['edad_grupo'] == 'adulto') &
                (requerimientos['genero'] == 'masculino')
            ]
        
        req = req.iloc[0]
        
        # Sumar requerimientos diarios × periodo
        totales['calorias'] += req['calorias_dia'] * periodo_dias
        totales['proteinas_g'] += req['proteinas_g_dia'] * periodo_dias
        totales['carbohidratos_g'] += req['carbohidratos_g_dia'] * periodo_dias
        totales['grasas_g'] += req['grasas_g_dia'] * periodo_dias
        totales['fibra_g'] += req['fibra_g_dia'] * periodo_dias
    
    return totales


def calcular_aporte_nutricional(individuo: Dict, catalogo: pd.DataFrame) -> Dict:
    """
    Calcula el aporte nutricional total del individuo.
    
    IMPORTANTE: Los valores nutricionales en el catálogo están por 100g/100ml.
    Debemos multiplicar por la cantidad del producto.
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma con genes
    catalogo : pd.DataFrame
        Catálogo con información nutricional
        
    Returns:
    --------
    dict
        Aporte total: {'calorias': X, 'proteinas_g': Y, ...}
    """
    
    aporte = {
        'calorias': 0,
        'proteinas_g': 0,
        'carbohidratos_g': 0,
        'grasas_g': 0,
        'fibra_g': 0
    }
    
    for gen in individuo['genes']:
        id_producto = gen['id_producto']
        cantidad = gen['cantidad']  # En kg, litros, paquetes, etc.
        
        # Buscar producto en catálogo
        producto = catalogo[catalogo['id'] == id_producto].iloc[0]
        
        # Información nutricional por 100g/100ml
        # Convertir cantidad a "unidades de 100g/100ml"
        # Asumimos que 1 unidad (kg, litro) = 10 × 100g/100ml
        factor_conversion = 10  # 1 kg = 10 × 100g
        
        cantidad_normalizada = cantidad * factor_conversion
        
        # Sumar aportes
        aporte['calorias'] += producto['calorias'] * cantidad_normalizada
        aporte['proteinas_g'] += producto['proteinas_g'] * cantidad_normalizada
        aporte['carbohidratos_g'] += producto['carbohidratos_g'] * cantidad_normalizada
        aporte['grasas_g'] += producto['grasas_g'] * cantidad_normalizada
        aporte['fibra_g'] += producto['fibra_g'] * cantidad_normalizada
    
    return aporte