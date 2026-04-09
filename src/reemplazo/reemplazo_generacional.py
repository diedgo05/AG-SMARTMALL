"""
Reemplazo generacional: Coordina el proceso de crear una nueva generación.

Proceso completo:
1. Seleccionar padres (torneo o ruleta)
2. Aplicar cruza
3. Aplicar mutación
4. Evaluar hijos
5. Aplicar elitismo
6. Retornar nueva generación
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Callable

def _resolver_imports_para_ejecucion_directa() -> None:
    """
    Permite ejecutar este archivo con `python ruta/al/archivo.py`.

    Cuando se ejecuta directo, Python no conoce el "paquete padre" y los imports
    relativos (from .modulo import ...) fallan. Aquí agregamos `src/` al sys.path
    para habilitar imports absolutos `reemplazo.*` como fallback.
    """

    import os
    import sys

    # .../AG-SMARTMALL/src/reemplazo/reemplazo_generacional.py -> .../AG-SMARTMALL/src
    this_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(this_dir)

    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)


try:
    # Modo paquete (recomendado): python -m reemplazo.reemplazo_generacional
    from .seleccion_torneo import seleccionar_parejas_torneo
    from .seleccion_ruleta import seleccionar_parejas_ruleta
    from .poda import aplicar_poda
except ImportError:  # pragma: no cover
    # Modo ejecución directa: python src/reemplazo/reemplazo_generacional.py
    _resolver_imports_para_ejecucion_directa()
    from reemplazo.seleccion_torneo import seleccionar_parejas_torneo
    from reemplazo.seleccion_ruleta import seleccionar_parejas_ruleta
    from reemplazo.poda import aplicar_poda


def generar_nueva_generacion(
    poblacion_actual: List[Dict],
    catalogo: pd.DataFrame,
    config: Dict,
    entrada_usuario: Dict,
    requerimientos: pd.DataFrame,
    operador_cruza: Callable,
    operador_mutacion: Callable,
    evaluador: Callable,
    metodo_seleccion: str = 'torneo',
    verbose: bool = False
) -> List[Dict]:
    """
    Genera una nueva generación completa aplicando operadores genéticos.
    
    Pipeline completo:
    ┌─────────────────┐
    │ Población Actual│
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ SELECCIÓN       │ (Torneo/Ruleta)
    │ Elegir padres   │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ CRUZA           │
    │ Generar hijos   │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ MUTACIÓN        │
    │ Introducir      │
    │ variabilidad    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ EVALUACIÓN      │
    │ Calcular fitness│
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ PODA            │
    │ Preservar       │
    │ mejores         │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Nueva Generación│
    └─────────────────┘
    
    Parameters:
    -----------
    poblacion_actual : list
        Generación actual (ya evaluada)
    catalogo : pd.DataFrame
        Catálogo de productos
    config : dict
        Configuración del AG
    entrada_usuario : dict
        Datos del usuario
    requerimientos : pd.DataFrame
        Requerimientos nutricionales
    operador_cruza : callable
        Función de cruza a aplicar
    operador_mutacion : callable
        Función de mutación a aplicar
    evaluador : callable
        Función para evaluar población
    metodo_seleccion : str
        'torneo' o 'ruleta'
    verbose : bool
        Si True, imprime progreso
        
    Returns:
    --------
    list
        Nueva generación
    """
    
    tamaño_poblacion = len(poblacion_actual)
    
    if verbose:
        print(f"\n🔄 Generando nueva generación...")
    
    # PASO 1: SELECCIÓN DE PADRES
    if verbose:
        print(f"  [1] Seleccionando padres ({metodo_seleccion})...")
    
    # Necesitamos tantas parejas como para generar población completa
    n_parejas = tamaño_poblacion // 2
    
    if metodo_seleccion == 'torneo':
        k = config['operadores']['seleccion']['tamaño_torneo']
        parejas = seleccionar_parejas_torneo(poblacion_actual, n_parejas, k)
    elif metodo_seleccion == 'ruleta':
        parejas = seleccionar_parejas_ruleta(poblacion_actual, n_parejas)
    else:
        raise ValueError(f"Método de selección '{metodo_seleccion}' no reconocido")
    
    if verbose:
        print(f"      ✅ {len(parejas)} parejas seleccionadas")
    
    # PASO 2: CRUZA
    if verbose:
        print(f"  [2] Aplicando cruza...")
    
    hijos = []
    for padre1, padre2 in parejas:
        hijo1, hijo2 = operador_cruza(padre1, padre2)
        hijos.extend([hijo1, hijo2])
    
    # Ajustar si tenemos más hijos de los necesarios (población impar)
    hijos = hijos[:tamaño_poblacion]
    
    if verbose:
        print(f"      ✅ {len(hijos)} hijos generados")
    
    # PASO 3: MUTACIÓN
    if verbose:
        print(f"  [3] Aplicando mutación...")
    
    hijos_mutados = []
    for hijo in hijos:
        hijo_mutado = operador_mutacion(hijo)
        hijos_mutados.append(hijo_mutado)
    
    n_mutados = sum(1 for h in hijos_mutados if h['metadata'].get('fue_mutado', False))
    
    if verbose:
        print(f"      ✅ {n_mutados}/{len(hijos_mutados)} individuos mutados")
    
    # PASO 4: EVALUACIÓN
    if verbose:
        print(f"  [4] Evaluando hijos...")
    
    hijos_evaluados = evaluador(
        poblacion=hijos_mutados,
        catalogo=catalogo,
        config=config,
        entrada_usuario=entrada_usuario,
        requerimientos=requerimientos,
        verbose=False
    )
    
    if verbose:
        fitness_promedio_hijos = np.mean([
            h['metadata']['fitness'] 
            for h in hijos_evaluados
        ])
        print(f"      ✅ Fitness promedio hijos: {fitness_promedio_hijos:.4f}")
    
    # PASO 5: PODA
    if verbose:
        print(f"  [5] Aplicando poda...")
    
    proporcion_elite = config['operadores']['elitismo']['proporcion']
    
    nueva_generacion = aplicar_poda(
        poblacion_actual=poblacion_actual,
        poblacion_hijos=hijos_evaluados,
        proporcion_elite=proporcion_elite
    )
    
    n_elite = int(tamaño_poblacion * proporcion_elite)
    
    if verbose:
        print(f"      ✅ {n_elite} individuos elite preservados")
    
    # Actualizar número de generación
    for ind in nueva_generacion:
        if not ind['metadata'].get('es_elite', False):
            # Solo incrementar generación si no es elite (elite mantiene su generación)
            gen_actual = ind['metadata'].get('generacion', 0)
            ind['metadata']['generacion'] = gen_actual
    
    if verbose:
        mejor_fitness = max(ind['metadata']['fitness'] for ind in nueva_generacion)
        print(f"\n  ✅ Nueva generación creada")
        print(f"     Mejor fitness: {mejor_fitness:.4f}")
    
    return nueva_generacion


def reemplazar_poblacion(
    poblacion_actual: List[Dict],
    nueva_generacion: List[Dict]
) -> List[Dict]:
    """
    Reemplaza la población actual con la nueva generación.
    
    Esta función es un wrapper simple que retorna la nueva generación,
    pero puede extenderse para implementar estrategias más complejas
    (ej. reemplazo parcial, steady-state, etc.)
    
    Parameters:
    -----------
    poblacion_actual : list
        Generación actual
    nueva_generacion : list
        Nueva generación
        
    Returns:
    --------
    list
        Nueva población (en este caso, nueva_generacion completa)
    """
    
    # Reemplazo generacional completo
    return nueva_generacion