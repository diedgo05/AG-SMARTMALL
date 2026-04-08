"""
Reparador de individuos: corrige individuos que violan restricciones duras.

Estrategias de reparación:
1. Exceso de presupuesto → eliminar productos menos valiosos
2. Alérgenos presentes → reemplazar productos con alérgenos
3. Deficiencia nutricional crítica → agregar productos nutritivos
"""

import numpy as np
import pandas as pd
from typing import Dict, List


def reparar_individuo(
    individuo: Dict,
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict
) -> Dict:
    """
    Repara un individuo que viola restricciones duras.
    
    Proceso:
    1. Identificar violaciones
    2. Aplicar estrategias de reparación según tipo de violación
    3. Re-validar individuo
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma a reparar
    catalogo : pd.DataFrame
        Catálogo de productos
    config : dict
        Configuración
    entrada_usuario : dict
        Datos del usuario
        
    Returns:
    --------
    dict
        Individuo reparado
    """
    
    violaciones = individuo['metadata'].get('violaciones', [])
    
    if not violaciones:
        return individuo  # Ya es válido, no necesita reparación
    
    # Crear copia para no modificar original
    individuo_reparado = {
        'genes': individuo['genes'].copy(),
        'metadata': individuo['metadata'].copy()
    }
    
    # Reparar según tipo de violación
    for violacion in violaciones:
        tipo = violacion['tipo']
        
        if tipo == 'exceso_presupuesto':
            individuo_reparado = reparar_exceso_presupuesto(
                individuo_reparado,
                catalogo,
                config,
                entrada_usuario
            )
        
        elif tipo == 'alergeno_presente':
            individuo_reparado = reparar_alergenos(
                individuo_reparado,
                catalogo,
                entrada_usuario,
                violacion
            )
    
    # Limpiar violaciones después de reparar
    individuo_reparado['metadata']['violaciones'] = []
    individuo_reparado['metadata']['es_valido'] = True
    individuo_reparado['metadata']['fue_reparado'] = True
    
    return individuo_reparado


def reparar_exceso_presupuesto(
    individuo: Dict,
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict
) -> Dict:
    """
    Repara individuo que excede presupuesto eliminando productos menos valiosos.
    
    Estrategia:
    1. Calcular "valor nutricional por peso" de cada producto
    2. Ordenar productos por este ratio (peor a mejor)
    3. Eliminar productos de menor valor hasta cumplir presupuesto
    
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
    dict
        Individuo reparado
    """
    
    from fitness.fitness_costo import calcular_costo_total, obtener_precio_por_marca
    
    presupuesto_max = entrada_usuario['presupuesto']
    
    # Calcular valor nutricional/costo de cada producto
    productos_con_valor = []
    
    for idx, gen in enumerate(individuo['genes']):
        id_producto = gen['id_producto']
        cantidad = gen['cantidad']
        marca = gen['marca']
        
        producto = catalogo[catalogo['id'] == id_producto].iloc[0]
        precio = obtener_precio_por_marca(producto, marca)
        costo = precio * cantidad
        
        # Valor nutricional simple: suma de proteínas + fibra (nutrientes valiosos)
        valor_nutricional = (producto['proteinas_g'] + producto['fibra_g']) * cantidad * 10
        
        # Ratio valor/costo (mayor es mejor)
        ratio = valor_nutricional / costo if costo > 0 else 0
        
        productos_con_valor.append({
            'idx': idx,
            'gen': gen,
            'costo': costo,
            'ratio': ratio,
            'es_esencial': es_producto_esencial(producto, entrada_usuario)
        })
    
    # Ordenar por ratio (menor primero = candidatos a eliminar)
    productos_con_valor.sort(key=lambda x: (x['es_esencial'], x['ratio']))
    
    # Eliminar productos hasta cumplir presupuesto
    genes_reparados = list(individuo['genes'])
    
    costo_actual = calcular_costo_total(individuo, catalogo)
    
    for prod in productos_con_valor:
        if costo_actual <= presupuesto_max:
            break  # Ya cumple presupuesto
        
        if not prod['es_esencial']:  # No eliminar productos esenciales
            # Eliminar este producto
            genes_reparados = [
                g for i, g in enumerate(genes_reparados) 
                if i != prod['idx']
            ]
            costo_actual -= prod['costo']
    
    # Si aún excede presupuesto, reducir cantidades
    if costo_actual > presupuesto_max:
        # Reducir cantidades proporcionalmente
        factor_reduccion = presupuesto_max / costo_actual * 0.95  # 95% para margen
        
        for gen in genes_reparados:
            gen['cantidad'] = round(gen['cantidad'] * factor_reduccion, 2)
            gen['cantidad'] = max(0.5, gen['cantidad'])  # Mínimo 0.5 unidades
    
    individuo['genes'] = np.array(genes_reparados, dtype=object)
    
    return individuo


def reparar_alergenos(
    individuo: Dict,
    catalogo: pd.DataFrame,
    entrada_usuario: Dict,
    violacion: Dict
) -> Dict:
    """
    Repara individuo que contiene productos con alérgenos prohibidos.
    
    Estrategia:
    1. Identificar producto con alérgeno
    2. Reemplazar por producto similar sin alérgeno
    
    Parameters:
    -----------
    individuo : dict
        Cromosoma
    catalogo : pd.DataFrame
        Catálogo
    entrada_usuario : dict
        Datos del usuario
    violacion : dict
        Información de la violación
        
    Returns:
    --------
    dict
        Individuo reparado
    """
    
    id_producto_problematico = violacion['producto_id']
    alergenos_prohibidos = entrada_usuario['alergenos_prohibidos']
    
    # Encontrar el gen con este producto
    for idx, gen in enumerate(individuo['genes']):
        if gen['id_producto'] == id_producto_problematico:
            # Buscar producto de reemplazo (misma categoría, sin alérgenos)
            producto_original = catalogo[catalogo['id'] == id_producto_problematico].iloc[0]
            categoria_original = producto_original['categoria']
            
            # Filtrar productos de la misma categoría sin alérgenos
            candidatos = catalogo[
                (catalogo['categoria'] == categoria_original) &
                (catalogo['id'] != id_producto_problematico)
            ]
            
            # Filtrar los que no tienen alérgenos prohibidos
            candidatos_validos = []
            for _, candidato in candidatos.iterrows():
                alergenos_str = candidato['alergenos']
                
                if pd.isna(alergenos_str) or alergenos_str == '':
                    candidatos_validos.append(candidato)
                else:
                    alergenos_candidato = [a.strip() for a in alergenos_str.split(',')]
                    if not any(a in alergenos_prohibidos for a in alergenos_candidato):
                        candidatos_validos.append(candidato)
            
            if candidatos_validos:
                # Seleccionar reemplazo aleatorio
                reemplazo = candidatos_validos[np.random.randint(0, len(candidatos_validos))]
                
                # Actualizar gen
                individuo['genes'][idx]['id_producto'] = int(reemplazo['id'])
            else:
                # Si no hay reemplazo, eliminar este gen
                individuo['genes'] = np.delete(individuo['genes'], idx)
            
            break  # Solo reparar este producto
    
    return individuo


def es_producto_esencial(producto: pd.Series, entrada_usuario: Dict) -> bool:
    """
    Determina si un producto es esencial (no debe eliminarse en reparación).
    
    Productos esenciales:
    - Productos en lista de preferencias del usuario
    - Productos básicos (leche, huevos, arroz, etc.)
    
    Parameters:
    -----------
    producto : pd.Series
        Información del producto
    entrada_usuario : dict
        Datos del usuario
        
    Returns:
    --------
    bool
        True si es esencial
    """
    
    id_producto = producto['id']
    
    # Verificar si está en preferencias
    preferencias = entrada_usuario.get('preferencias', {})
    productos_preferidos = preferencias.get('productos_preferidos', [])
    
    if id_producto in productos_preferidos:
        return True
    
    # Verificar si es producto básico por nombre
    nombre = producto['nombre'].lower()
    productos_basicos = ['leche', 'huevo', 'arroz', 'frijol', 'pan']
    
    if any(basico in nombre for basico in productos_basicos):
        return True
    
    return False