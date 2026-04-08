"""
Componente de fitness: DESPERDICIO.

Objetivo: Minimizar el desperdicio de alimentos.

Factores considerados:
- Productos perecederos (vida útil < 7 días)
- Cantidad comprada vs. tasa de consumo estimada
- Número de productos perecederos

Fórmula:
    desperdicio_estimado = suma(probabilidad_desperdicio × costo_producto)
    f_desperdicio = 1 - (desperdicio_estimado / costo_total)
"""

import numpy as np
import pandas as pd
from typing import Dict


def calcular_fitness_desperdicio(
    individuo: Dict,
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict
) -> float:
    """
    Calcula fitness basado en desperdicio estimado de alimentos.
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma con genes
    catalogo : pd.DataFrame
        Catálogo con vida útil de productos
    config : dict
        Configuración
    entrada_usuario : dict
        Datos del usuario (periodo, familia)
        
    Returns:
    --------
    float
        Fitness de desperdicio en [0, 1]
        1.0 = desperdicio mínimo (óptimo)
        0.0 = desperdicio muy alto
        
    Lógica:
    -------
    1. Identificar productos perecederos (vida_util < periodo_dias)
    2. Estimar probabilidad de desperdicio por producto
    3. Calcular desperdicio total estimado
    4. Penalizar exceso de productos perecederos
    """
    
    periodo_dias = entrada_usuario['periodo_dias']
    num_personas = entrada_usuario['num_personas']
    max_perecederos = config['restricciones']['max_productos_perecederos']
    
    # Calcular costo total (para normalización)
    costo_total = individuo['metadata'].get('costo_total', 1.0)
    
    desperdicio_total = 0.0
    productos_perecederos = []
    
    for gen in individuo['genes']:
        id_producto = gen['id_producto']
        cantidad = gen['cantidad']
        marca = gen['marca']
        
        # Buscar producto en catálogo
        producto = catalogo[catalogo['id'] == id_producto].iloc[0]
        
        vida_util = producto['vida_util_dias']
        categoria = producto['categoria']
        
        # ¿Es perecedero para este periodo?
        if vida_util < periodo_dias * 1.5:  # Margen de 50%
            productos_perecederos.append(producto['nombre'])
            
            # Estimar probabilidad de desperdicio
            prob_desperdicio = estimar_probabilidad_desperdicio(
                producto=producto,
                cantidad=cantidad,
                vida_util=vida_util,
                periodo_dias=periodo_dias,
                num_personas=num_personas
            )
            
            # Calcular desperdicio monetario esperado
            precio = obtener_precio_producto(producto, marca)
            costo_producto = precio * cantidad
            desperdicio_producto = prob_desperdicio * costo_producto
            
            desperdicio_total += desperdicio_producto
    
    # PENALIZACIÓN 1: Desperdicio monetario
    if costo_total > 0:
        ratio_desperdicio = desperdicio_total / costo_total
    else:
        ratio_desperdicio = 0
    
    fitness = 1.0 - ratio_desperdicio
    
    # PENALIZACIÓN 2: Exceso de productos perecederos
    num_perecederos = len(productos_perecederos)
    
    if num_perecederos > max_perecederos:
        exceso = num_perecederos - max_perecederos
        penalizacion_exceso = exceso * 0.05  # -5% por cada producto extra
        fitness = max(0.0, fitness - penalizacion_exceso)
        
        individuo['metadata']['violaciones'].append({
            'tipo': 'exceso_perecederos',
            'severidad': 'media',
            'detalle': f'{num_perecederos} productos perecederos (máx: {max_perecederos})'
        })
    
    # Guardar información en metadata
    individuo['metadata']['desperdicio'] = {
        'desperdicio_estimado': round(desperdicio_total, 2),
        'ratio_desperdicio': round(ratio_desperdicio, 3),
        'num_perecederos': num_perecederos,
        'productos_perecederos': productos_perecederos[:5]  # Primeros 5
    }
    
    return min(1.0, max(0.0, fitness))


def estimar_probabilidad_desperdicio(
    producto: pd.Series,
    cantidad: float,
    vida_util: int,
    periodo_dias: int,
    num_personas: int
) -> float:
    """
    Estima la probabilidad de que un producto se desperdicie.
    
    Factores:
    - Vida útil vs. periodo de compra
    - Cantidad comprada vs. tamaño de familia
    - Categoría del producto
    
    Parameters:
    -----------
    producto : pd.Series
        Información del producto
    cantidad : float
        Cantidad comprada
    vida_util : int
        Días antes de caducar
    periodo_dias : int
        Periodo de compra (ej. 7 días)
    num_personas : int
        Tamaño de la familia
        
    Returns:
    --------
    float
        Probabilidad de desperdicio [0, 1]
    """
    
    categoria = producto['categoria']
    
    # FACTOR 1: Vida útil relativa
    if vida_util >= periodo_dias * 2:
        factor_vida_util = 0.0  # No perecedero para este periodo
    elif vida_util >= periodo_dias:
        factor_vida_util = 0.2  # Baja probabilidad
    elif vida_util >= periodo_dias * 0.5:
        factor_vida_util = 0.5  # Probabilidad moderada
    else:
        factor_vida_util = 0.8  # Alta probabilidad (caduca muy pronto)
    
    # FACTOR 2: Cantidad vs. tamaño de familia
    # Estimación heurística: familia promedio consume ~0.3 unidades/persona/día
    consumo_estimado = num_personas * periodo_dias * 0.3
    
    if cantidad <= consumo_estimado * 0.8:
        factor_cantidad = 0.0  # Cantidad conservadora
    elif cantidad <= consumo_estimado * 1.2:
        factor_cantidad = 0.1  # Cantidad adecuada
    elif cantidad <= consumo_estimado * 1.5:
        factor_cantidad = 0.3  # Algo excesivo
    else:
        factor_cantidad = 0.6  # Muy excesivo
    
    # FACTOR 3: Categoría (algunas categorías se desperdician más)
    factores_categoria = {
        'Frutas': 0.3,
        'Verduras': 0.3,
        'Lácteos': 0.2,
        'Panadería': 0.2,
        'Proteínas': 0.25,
        'Granos y Legumbres': 0.0,
        'Enlatados': 0.0,
        'Congelados': 0.1,
        'Aceites y Condimentos': 0.0,
        'Bebidas': 0.1,
        'Botanas': 0.05
    }
    
    factor_categoria = factores_categoria.get(categoria, 0.15)
    
    # Combinar factores (promedio ponderado)
    probabilidad = (
        0.4 * factor_vida_util +
        0.4 * factor_cantidad +
        0.2 * factor_categoria
    )
    
    return min(1.0, max(0.0, probabilidad))


def obtener_precio_producto(producto: pd.Series, marca: str) -> float:
    """Obtiene precio del producto según marca."""
    mapa_precios = {
        'generica': 'precio_generica',
        'media': 'precio_media',
        'premium': 'precio_premium'
    }
    
    columna = mapa_precios.get(marca, 'precio_generica')
    return float(producto[columna])