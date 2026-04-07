"""
Generador de individuos (cromosomas) para el AG.
Cada individuo representa una lista de compras de exactamente 20 productos.
"""

import numpy as np
import pandas as pd
from typing import Dict, List


def generar_individuo_aleatorio(
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict,
    seed: int = None
) -> Dict:
    """
    Genera un individuo (cromosoma) aleatorio válido.
    
    CROMOSOMA = lista de exactamente 20 productos con sus atributos.
    
    Parameters:
    -----------
    catalogo : pd.DataFrame
        Catálogo completo de productos disponibles
    config : dict
        Configuración del AG (cargada desde config_ag.json)
    entrada_usuario : dict
        Datos de entrada del usuario (presupuesto, familia, restricciones)
    seed : int, optional
        Semilla para reproducibilidad
        
    Returns:
    --------
    dict
        Individuo con estructura:
        {
            'genes': np.array([gen1, gen2, ..., gen20]),
            'metadata': {
                'fitness': None,
                'fitness_componentes': {},
                'es_valido': True,
                'generacion': 0,
                'violaciones': []
            }
        }
    
    Estrategia de generación:
    -------------------------
    1. Filtrar productos prohibidos (alérgenos)
    2. Seleccionar productos esenciales (si los hay)
    3. Completar con productos aleatorios hasta tener 20
    4. Asignar cantidades, marcas y supermercados aleatorios
    5. Verificar restricciones básicas (presupuesto buffer)
    """
    
    if seed is not None:
        np.random.seed(seed)
    
    n_genes = config['poblacion']['genes_fijos']  # 20 productos fijos
    
    # PASO 1: Filtrar catálogo (eliminar productos con alérgenos prohibidos)
    catalogo_valido = filtrar_productos_prohibidos(
        catalogo, 
        entrada_usuario['alergenos_prohibidos']
    )
    
    if len(catalogo_valido) < n_genes:
        raise ValueError(
            f"Catálogo insuficiente: solo {len(catalogo_valido)} productos "
            f"válidos, se necesitan al menos {n_genes}"
        )
    
    # PASO 2: Identificar productos esenciales (si están en inventario o preferencias)
    productos_esenciales_ids = identificar_productos_esenciales(
        catalogo_valido,
        entrada_usuario
    )
    
    # PASO 3: Seleccionar productos para el cromosoma
    productos_seleccionados = seleccionar_productos_para_cromosoma(
        catalogo_valido,
        productos_esenciales_ids,
        n_genes
    )
    
    # PASO 4: Crear genes (asignar cantidad, marca, supermercado)
    genes = []
    
    for id_producto in productos_seleccionados:
        producto_info = catalogo_valido[catalogo_valido['id'] == id_producto].iloc[0]
        
        # Crear gen
        gen = crear_gen_aleatorio(producto_info, entrada_usuario)
        genes.append(gen)
    
    # PASO 5: Crear cromosoma completo
    cromosoma = {
        'genes': np.array(genes, dtype=object),
        'metadata': {
            'fitness': None,
            'fitness_componentes': {
                'costo': None,
                'nutricion': None,
                'desperdicio': None,
                'cobertura': None,
                'satisfaccion': None
            },
            'es_valido': True,
            'generacion': 0,
            'violaciones': [],
            'costo_total': None  # Se calcula en fitness
        }
    }
    
    return cromosoma


def filtrar_productos_prohibidos(
    catalogo: pd.DataFrame, 
    alergenos_prohibidos: List[str]
) -> pd.DataFrame:
    """
    Elimina del catálogo productos que contienen alérgenos prohibidos.
    
    Parameters:
    -----------
    catalogo : pd.DataFrame
        Catálogo completo
    alergenos_prohibidos : list
        Lista de alérgenos que NO deben estar presentes
        
    Returns:
    --------
    pd.DataFrame
        Catálogo filtrado
    """
    
    if not alergenos_prohibidos:
        return catalogo.copy()
    
    def tiene_alergeno_prohibido(alergenos_str):
        """Verifica si un producto tiene algún alérgeno prohibido."""
        if pd.isna(alergenos_str) or alergenos_str == '':
            return False
        
        alergenos_producto = [a.strip() for a in alergenos_str.split(',')]
        
        for alergeno in alergenos_producto:
            if alergeno in alergenos_prohibidos:
                return True
        
        return False
    
    # Filtrar productos
    mascara_validos = ~catalogo['alergenos'].apply(tiene_alergeno_prohibido)
    catalogo_filtrado = catalogo[mascara_validos].copy()
    
    return catalogo_filtrado


def identificar_productos_esenciales(
    catalogo: pd.DataFrame,
    entrada_usuario: Dict
) -> List[int]:
    """
    Identifica productos que DEBEN estar en la lista de compras.
    
    Criterios:
    - Productos preferidos por la familia
    - Productos básicos (leche, huevos, arroz, etc.)
    - Productos para complementar inventario bajo
    
    Parameters:
    -----------
    catalogo : pd.DataFrame
        Catálogo filtrado de productos válidos
    entrada_usuario : dict
        Datos de usuario
        
    Returns:
    --------
    list
        IDs de productos esenciales (máximo 10 para dejar espacio a variabilidad)
    """
    
    esenciales = []
    
    # 1. Productos preferidos del usuario
    if 'preferencias' in entrada_usuario:
        prefs = entrada_usuario['preferencias'].get('productos_preferidos', [])
        # Tomar máximo 5 productos preferidos
        esenciales.extend(prefs[:5])
    
    # 2. Productos básicos universales (si no están en preferencias)
    # Buscar productos por nombre (aproximación simple)
    productos_basicos_nombres = ['leche', 'huevo', 'arroz', 'frijol', 'pan']
    
    for nombre_basico in productos_basicos_nombres:
        if len(esenciales) >= 10:  # Límite de esenciales
            break
        
        # Buscar producto que contenga ese nombre
        mascara = catalogo['nombre'].str.lower().str.contains(nombre_basico, na=False)
        productos_encontrados = catalogo[mascara]
        
        if len(productos_encontrados) > 0:
            # Tomar el más barato (genérica)
            producto_basico = productos_encontrados.iloc[0]['id']
            if producto_basico not in esenciales:
                esenciales.append(producto_basico)
    
    return esenciales[:10]  # Máximo 10 productos esenciales


def seleccionar_productos_para_cromosoma(
    catalogo: pd.DataFrame,
    productos_esenciales: List[int],
    n_genes: int
) -> List[int]:
    """
    Selecciona exactamente n_genes productos para el cromosoma.
    
    Estrategia:
    - Incluir todos los productos esenciales
    - Completar con productos aleatorios del catálogo
    - Asegurar diversidad de categorías
    
    Parameters:
    -----------
    catalogo : pd.DataFrame
        Catálogo filtrado
    productos_esenciales : list
        IDs de productos que deben incluirse
    n_genes : int
        Número total de genes (20)
        
    Returns:
    --------
    list
        Lista de n_genes IDs de productos únicos
    """
    
    seleccionados = productos_esenciales.copy()
    
    # Cuántos productos faltan por seleccionar
    n_faltantes = n_genes - len(seleccionados)
    
    if n_faltantes <= 0:
        # Si hay más esenciales que genes, tomar solo los primeros n_genes
        return seleccionados[:n_genes]
    
    # Productos candidatos (que NO sean esenciales)
    candidatos = catalogo[~catalogo['id'].isin(seleccionados)]
    
    # Estrategia: seleccionar de manera balanceada por categoría
    categorias = catalogo['categoria'].unique()
    productos_por_categoria = n_faltantes // len(categorias) + 1
    
    productos_adicionales = []
    
    for categoria in categorias:
        if len(productos_adicionales) >= n_faltantes:
            break
        
        productos_categoria = candidatos[candidatos['categoria'] == categoria]
        
        if len(productos_categoria) > 0:
            # Seleccionar aleatoriamente de esta categoría
            n_tomar = min(productos_por_categoria, len(productos_categoria))
            ids_seleccionados = np.random.choice(
                productos_categoria['id'].values,
                size=n_tomar,
                replace=False
            )
            productos_adicionales.extend(ids_seleccionados.tolist())
    
    # Combinar esenciales + adicionales
    seleccionados.extend(productos_adicionales[:n_faltantes])
    
    # Si todavía faltan productos (poco probable), rellenar aleatoriamente
    while len(seleccionados) < n_genes:
        candidatos_restantes = candidatos[~candidatos['id'].isin(seleccionados)]
        if len(candidatos_restantes) == 0:
            break
        id_aleatorio = np.random.choice(candidatos_restantes['id'].values)
        seleccionados.append(id_aleatorio)
    
    return seleccionados[:n_genes]


def crear_gen_aleatorio(
    producto_info: pd.Series,
    entrada_usuario: Dict
) -> Dict:
    """
    Crea un gen (producto con atributos) con valores aleatorios.
    
    GEN = {
        'id_producto': int,
        'cantidad': float,
        'marca': str,
        'supermercado': str
    }
    
    Parameters:
    -----------
    producto_info : pd.Series
        Fila del catálogo con información del producto
    entrada_usuario : dict
        Datos de usuario
        
    Returns:
    --------
    dict
        Gen con atributos asignados
    """
    
    # Cantidad aleatoria (0.5 a 5.0 unidades)
    # Cantidad depende del tipo de producto y tamaño de familia
    n_personas = entrada_usuario['num_personas']
    periodo_dias = entrada_usuario['periodo_dias']
    
    # Estimación: familia promedio consume X cantidad por semana
    # Ajuste heurístico simple
    cantidad_base = np.random.uniform(0.5, 3.0)
    factor_familia = 1 + (n_personas - 4) * 0.2  # Ajuste por tamaño
    cantidad = round(cantidad_base * factor_familia, 2)
    
    # Marca aleatoria (distribución: 50% genérica, 30% media, 20% premium)
    marcas = ['generica', 'media', 'premium']
    probabilidades = [0.50, 0.30, 0.20]
    marca = np.random.choice(marcas, p=probabilidades)
    
    # Supermercado aleatorio (de los disponibles para este producto)
    supermercados_disponibles = producto_info['supermercados'].split(',')
    supermercado = np.random.choice(supermercados_disponibles)
    
    gen = {
        'id_producto': int(producto_info['id']),
        'cantidad': cantidad,
        'marca': marca,
        'supermercado': supermercado
    }
    
    return gen