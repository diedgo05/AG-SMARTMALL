"""
Validador de restricciones duras del problema.

Restricciones duras (OBLIGATORIAS):
1. Presupuesto no puede exceder máximo
2. No contener productos con alérgenos prohibidos
3. (Opcional) Contener productos esenciales mínimos

Si un individuo viola restricciones duras, debe ser reparado o penalizado severamente.
"""

import pandas as pd
from typing import Dict, List, Tuple


def validar_restricciones_duras(
    individuo: Dict,
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict
) -> Tuple[bool, List[Dict]]:
    """
    Valida que un individuo cumpla todas las restricciones duras.
    
    Restricciones verificadas:
    1. Presupuesto <= presupuesto_max (con buffer de tolerancia)
    2. No contiene alérgenos prohibidos
    3. (Futuro) Contiene productos esenciales
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma a validar
    catalogo : pd.DataFrame
        Catálogo de productos
    config : dict
        Configuración (restricciones)
    entrada_usuario : dict
        Datos del usuario (presupuesto, alérgenos)
        
    Returns:
    --------
    tuple
        (es_valido: bool, violaciones: list)
        - es_valido: True si cumple todas las restricciones
        - violaciones: Lista de diccionarios con info de violaciones
    """
    
    violaciones = []
    
    # RESTRICCIÓN 1: Presupuesto
    violacion_presupuesto = validar_presupuesto(
        individuo,
        catalogo,
        config,
        entrada_usuario
    )
    if violacion_presupuesto:
        violaciones.append(violacion_presupuesto)
    
    # RESTRICCIÓN 2: Alérgenos
    violaciones_alergenos = validar_alergenos(
        individuo,
        catalogo,
        entrada_usuario
    )
    if violaciones_alergenos:
        violaciones.extend(violaciones_alergenos)
    
    # RESTRICCIÓN 3: Productos esenciales (opcional, menos estricta)
    # Por ahora no la implementamos como restricción dura
    
    # Determinar si es válido
    es_valido = len(violaciones) == 0
    
    # Actualizar metadata del individuo
    individuo['metadata']['es_valido'] = es_valido
    
    return es_valido, violaciones


def validar_presupuesto(
    individuo: Dict,
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict
) -> Dict | None:
    """
    Valida que el costo no exceda el presupuesto máximo.
    
    Se permite un buffer pequeño (5%) para tolerancia durante evolución.
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma
    catalogo : pd.DataFrame
        Catálogo
    config : dict
        Configuración
    entrada_usuario : dict
        Datos del usuario
        
    Returns:
    --------
    dict | None
        Información de violación si existe, None si cumple
    """
    
    presupuesto_max = entrada_usuario['presupuesto']
    buffer = config['restricciones'].get('presupuesto_buffer', 1.05)
    presupuesto_permitido = presupuesto_max * buffer
    
    # Costo total (ya calculado en fitness)
    costo_total = individuo['metadata'].get('costo_total')
    
    if costo_total is None:
        # Si no está calculado, calcularlo ahora
        from fitness.fitness_costo import calcular_costo_total
        costo_total = calcular_costo_total(individuo, catalogo)
        individuo['metadata']['costo_total'] = costo_total
    
    if costo_total > presupuesto_permitido:
        return {
            'tipo': 'exceso_presupuesto',
            'severidad': 'alta',
            'detalle': f'Costo ${costo_total:.2f} excede presupuesto permitido ${presupuesto_permitido:.2f}',
            'costo_total': costo_total,
            'presupuesto_max': presupuesto_max,
            'exceso': costo_total - presupuesto_max
        }
    
    return None


def validar_alergenos(
    individuo: Dict,
    catalogo: pd.DataFrame,
    entrada_usuario: Dict
) -> List[Dict]:
    """
    Valida que ningún producto contenga alérgenos prohibidos.
    
    Esta es una restricción CRÍTICA de seguridad.
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma
    catalogo : pd.DataFrame
        Catálogo
    entrada_usuario : dict
        Datos del usuario
        
    Returns:
    --------
    list
        Lista de violaciones (puede estar vacía)
    """
    
    alergenos_prohibidos = entrada_usuario.get('alergenos_prohibidos', [])
    
    if not alergenos_prohibidos:
        return []  # No hay restricciones de alérgenos
    
    violaciones = []
    
    for gen in individuo['genes']:
        id_producto = gen['id_producto']
        producto = catalogo[catalogo['id'] == id_producto].iloc[0]
        
        alergenos_producto_str = producto['alergenos']
        
        # Si el producto tiene alérgenos
        if pd.notna(alergenos_producto_str) and alergenos_producto_str != '':
            alergenos_producto = [a.strip() for a in alergenos_producto_str.split(',')]
            
            # Verificar si contiene algún alérgeno prohibido
            alergenos_encontrados = [
                a for a in alergenos_producto 
                if a in alergenos_prohibidos
            ]
            
            if alergenos_encontrados:
                violaciones.append({
                    'tipo': 'alergeno_presente',
                    'severidad': 'critica',
                    'detalle': f"Producto '{producto['nombre']}' contiene alérgenos prohibidos: {', '.join(alergenos_encontrados)}",
                    'producto_id': id_producto,
                    'producto_nombre': producto['nombre'],
                    'alergenos': alergenos_encontrados
                })
    
    return violaciones


def es_individuo_valido(individuo: Dict) -> bool:
    """
    Verifica si un individuo es válido (sin restricciones violadas).
    
    Asume que ya se llamó validar_restricciones_duras previamente.
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma
        
    Returns:
    --------
    bool
        True si es válido
    """
    
    return individuo['metadata'].get('es_valido', True)


def contar_violaciones_poblacion(poblacion: List[Dict]) -> Dict:
    """
    Cuenta el número de violaciones en toda la población.
    
    Parameters:
    -----------
    poblacion : list
        Población de individuos
        
    Returns:
    --------
    dict
        Estadísticas de violaciones
    """
    
    total_individuos = len(poblacion)
    individuos_validos = sum(1 for ind in poblacion if es_individuo_valido(ind))
    individuos_invalidos = total_individuos - individuos_validos
    
    # Contar por tipo de violación
    tipos_violaciones = {}
    
    for individuo in poblacion:
        for violacion in individuo['metadata'].get('violaciones', []):
            tipo = violacion['tipo']
            tipos_violaciones[tipo] = tipos_violaciones.get(tipo, 0) + 1
    
    return {
        'total_individuos': total_individuos,
        'individuos_validos': individuos_validos,
        'individuos_invalidos': individuos_invalidos,
        'porcentaje_validos': (individuos_validos / total_individuos * 100) if total_individuos > 0 else 0,
        'violaciones_por_tipo': tipos_violaciones
    }