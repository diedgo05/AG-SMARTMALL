"""
Cargador de datos y archivos de configuración.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict


def cargar_catalogo(ruta: str = 'data/catalogo_productos.csv') -> pd.DataFrame:
    """
    Carga catálogo de productos desde CSV.
    
    Parameters:
    -----------
    ruta : str
        Ruta al archivo CSV
        
    Returns:
    --------
    pd.DataFrame
        Catálogo de productos
    """
    
    ruta_path = Path(ruta)
    
    if not ruta_path.exists():
        raise FileNotFoundError(
            f"Catálogo no encontrado: {ruta}\n"
            f"Ejecuta primero: python scripts/generar_catalogo_productos.py"
        )
    
    catalogo = pd.read_csv(ruta)
    
    print(f"✅ Catálogo cargado: {len(catalogo)} productos")
    
    return catalogo


def cargar_configuracion(ruta: str = 'data/config_ag.json') -> Dict:
    """
    Carga configuración del AG desde JSON.
    
    Parameters:
    -----------
    ruta : str
        Ruta al archivo JSON
        
    Returns:
    --------
    dict
        Configuración del AG
    """
    
    ruta_path = Path(ruta)
    
    if not ruta_path.exists():
        raise FileNotFoundError(f"Configuración no encontrada: {ruta}")
    
    with open(ruta, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print(f"✅ Configuración cargada")
    print(f"  - Población: {config['poblacion']['tamaño']} individuos")
    print(f"  - Genes por individuo: {config['poblacion']['genes_fijos']}")
    print(f"  - Generaciones máximas: {config['generaciones']['max_generaciones']}")
    
    return config


def cargar_requerimientos_nutricionales(
    ruta: str = 'data/requerimientos_nutricionales.csv'
) -> pd.DataFrame:
    """
    Carga tabla de requerimientos nutricionales.
    
    Parameters:
    -----------
    ruta : str
        Ruta al archivo CSV
        
    Returns:
    --------
    pd.DataFrame
        Tabla de requerimientos
    """
    
    ruta_path = Path(ruta)
    
    if not ruta_path.exists():
        raise FileNotFoundError(
            f"Requerimientos no encontrados: {ruta}\n"
            f"Ejecuta: python scripts/generar_requerimientos_nutricionales.py"
        )
    
    reqs = pd.read_csv(ruta)
    
    print(f"✅ Requerimientos nutricionales cargados: {len(reqs)} grupos")
    
    return reqs