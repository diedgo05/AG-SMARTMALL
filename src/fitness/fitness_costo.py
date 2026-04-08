"""
Componente de fitness: COSTO.

Objetivo: Minimizar el costo total de la lista de compras.

Función:
- Si costo <= presupuesto: fitness alto (cercano a 1)
- Si costo > presupuesto: penalización severa

Fórmula:
    f_costo = 1 - (costo_total / presupuesto_max)  si costo <= presupuesto
    f_costo = penalización_severa                  si costo > presupuesto
"""

import numpy as np
import pandas as pd
from typing import Dict


def calcular_fitness_costo(
    individuo: Dict,
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict
) -> float:
    """
    Calcula fitness basado en el costo total de la lista de compras.
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma con genes (productos)
    catalogo : pd.DataFrame
        Catálogo de productos con precios
    config : dict
        Configuración del AG (penalizaciones)
    entrada_usuario : dict
        Datos del usuario (presupuesto)
        
    Returns:
    --------
    float
        Fitness de costo en rango [0, 1]
        1.0 = costo mínimo (óptimo)
        0.0 = costo máximo o violación severa
        
    Lógica:
    -------
    1. Calcular costo total sumando: precio × cantidad para cada producto
    2. Precio depende de la marca seleccionada (genérica/media/premium)
    3. Si costo <= presupuesto: recompensar uso eficiente
    4. Si costo > presupuesto: penalizar fuertemente (restricción dura)
    """
    
    presupuesto_max = entrada_usuario['presupuesto']
    penalizacion_exceso = config['fitness']['penalizaciones']['exceso_presupuesto']
    
    # Calcular costo total del individuo
    costo_total = calcular_costo_total(individuo, catalogo)
    
    # Guardar en metadata para referencia
    individuo['metadata']['costo_total'] = costo_total
    
    # CASO 1: Costo dentro del presupuesto
    if costo_total <= presupuesto_max:
        # Fitness alto si usa poco presupuesto, pero no penalizar demasiado
        # usar más presupuesto (queremos cubrir necesidades)
        # Normalizar: fitness = 1.0 si usa 80-100% del presupuesto
        
        ratio_uso = costo_total / presupuesto_max
        
        if ratio_uso >= 0.80:
            # Uso óptimo del presupuesto (80-100%)
            fitness = 1.0
        elif ratio_uso >= 0.60:
            # Uso aceptable (60-80%)
            # Interpolación lineal: 0.8 en 60%, 1.0 en 80%
            fitness = 0.8 + (ratio_uso - 0.60) * (0.2 / 0.20)
        else:
            # Uso muy bajo (<60%): puede indicar lista incompleta
            # Fitness moderado
            fitness = 0.5 + ratio_uso * (0.3 / 0.60)
        
        return min(1.0, max(0.0, fitness))
    
    # CASO 2: Costo excede presupuesto (RESTRICCIÓN DURA VIOLADA)
    else:
        exceso = costo_total - presupuesto_max
        exceso_porcentual = exceso / presupuesto_max
        
        # Penalización proporcional al exceso
        # Exceso 5% → penalización moderada
        # Exceso 20%+ → penalización severa
        
        if exceso_porcentual <= 0.05:
            # Tolerancia del 5% (puede ocurrir durante evolución)
            fitness = 0.5
        elif exceso_porcentual <= 0.10:
            # Exceso 5-10%: penalización moderada
            fitness = 0.3
        elif exceso_porcentual <= 0.20:
            # Exceso 10-20%: penalización fuerte
            fitness = 0.1
        else:
            # Exceso >20%: penalización muy severa
            fitness = 0.01
        
        # Marcar violación en metadata
        individuo['metadata']['violaciones'].append({
            'tipo': 'exceso_presupuesto',
            'severidad': 'alta',
            'detalle': f'Costo: ${costo_total:.2f}, Presupuesto: ${presupuesto_max:.2f}'
        })
        
        return fitness


def calcular_costo_total(individuo: Dict, catalogo: pd.DataFrame) -> float:
    """
    Calcula el costo total de todos los productos en el individuo.
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma con genes
    catalogo : pd.DataFrame
        Catálogo con precios
        
    Returns:
    --------
    float
        Costo total en pesos mexicanos
    """
    
    costo_total = 0.0
    
    for gen in individuo['genes']:
        id_producto = gen['id_producto']
        cantidad = gen['cantidad']
        marca = gen['marca']
        
        # Buscar producto en catálogo
        producto = catalogo[catalogo['id'] == id_producto].iloc[0]
        
        # Obtener precio según marca
        precio_unitario = obtener_precio_por_marca(producto, marca)
        
        # Costo de este producto
        costo_producto = precio_unitario * cantidad
        costo_total += costo_producto
    
    return round(costo_total, 2)


def obtener_precio_por_marca(producto: pd.Series, marca: str) -> float:
    """
    Obtiene el precio del producto según la marca seleccionada.
    
    Parameters:
    -----------
    producto : pd.Series
        Fila del catálogo
    marca : str
        'generica', 'media', o 'premium'
        
    Returns:
    --------
    float
        Precio unitario
    """
    
    mapa_precios = {
        'generica': 'precio_generica',
        'media': 'precio_media',
        'premium': 'precio_premium'
    }
    
    columna_precio = mapa_precios.get(marca, 'precio_generica')
    precio = producto[columna_precio]
    
    return float(precio)