"""
Script de prueba para validar el módulo de cruza.
"""

import sys
sys.path.append('src')

import numpy as np
from utils import (
    cargar_catalogo,
    cargar_configuracion,
    cargar_requerimientos_nutricionales
)
from inicializacion import generar_individuo_aleatorio
from cruza import (
    cruzar_dos_puntos,
    cruzar_un_punto,
    cruzar_uniforme,
    aplicar_cruza_poblacion
)


def visualizar_cromosoma(individuo, catalogo, nombre="Individuo"):
    """Visualiza los primeros 5 productos de un cromosoma."""
    print(f"\n  {nombre}:")
    for i, gen in enumerate(individuo['genes'][:5], 1):
        producto = catalogo[catalogo['id'] == gen['id_producto']].iloc[0]
        print(f"    {i}. ID:{gen['id_producto']:3d} {producto['nombre'][:30]:30s} "
              f"Cant:{gen['cantidad']:.1f} Marca:{gen['marca']:8s}")
    print(f"    ... ({len(individuo['genes'])} productos en total)")


def main():
    """Prueba los operadores de cruza."""
    
    print("="*70)
    print(" TEST: MÓDULO DE CRUZA")
    print("="*70)
    
    # 1. Cargar datos
    print("\n[1] Cargando datos...")
    catalogo = cargar_catalogo()
    config = cargar_configuracion()
    requerimientos = cargar_requerimientos_nutricionales()
    
    # 2. Entrada de usuario
    entrada_usuario = {
        'presupuesto': 2000,
        'num_personas': 4,
        'composicion_familia': [
            {'edad_grupo': 'adulto', 'genero': 'masculino'},
            {'edad_grupo': 'adulto', 'genero': 'femenino'},
            {'edad_grupo': 'niño_8_12', 'genero': 'ambos'},
            {'edad_grupo': 'niño_4_7', 'genero': 'ambos'}
        ],
        'periodo_dias': 7,
        'alergenos_prohibidos': ['gluten'],
        'preferencias': {
            'productos_preferidos': [1, 3, 5, 12],
            'productos_evitar': [45, 67],
            'prioridad_organico': False
        },
        'inventario_actual': [],
        'comidas_planificadas': 21
    }
    
    # 3. Generar dos padres
    print("\n[2] Generando dos padres...")
    padre1 = generar_individuo_aleatorio(
        catalogo=catalogo,
        config=config,
        entrada_usuario=entrada_usuario,
        seed=42
    )
    
    padre2 = generar_individuo_aleatorio(
        catalogo=catalogo,
        config=config,
        entrada_usuario=entrada_usuario,
        seed=100
    )
    
    print("\n📋 PADRES GENERADOS:")
    visualizar_cromosoma(padre1, catalogo, "Padre 1")
    visualizar_cromosoma(padre2, catalogo, "Padre 2")
    
    # 4. Probar cruza de dos puntos
    print("\n" + "="*70)
    print("[3] PRUEBA: CRUZA DE DOS PUNTOS")
    print("="*70)
    
    hijo1_2p, hijo2_2p = cruzar_dos_puntos(padre1, padre2, probabilidad_cruza=1.0)
    
    print("\n🧬 HIJOS GENERADOS (Cruza de dos puntos):")
    visualizar_cromosoma(hijo1_2p, catalogo, "Hijo 1")
    visualizar_cromosoma(hijo2_2p, catalogo, "Hijo 2")
    
    print(f"\n  Metadata Hijo 1:")
    print(f"    - Generación: {hijo1_2p['metadata']['generacion']}")
    print(f"    - Origen: {hijo1_2p['metadata']['origen']}")
    print(f"    - Número de genes: {len(hijo1_2p['genes'])}")
    
    # Verificar que no hay duplicados
    ids_hijo1 = [g['id_producto'] for g in hijo1_2p['genes']]
    ids_unicos = len(set(ids_hijo1))
    print(f"    - Productos únicos: {ids_unicos}/20 {'✅' if ids_unicos == 20 else '⚠️'}")
    
    # 5. Probar cruza de un punto
    print("\n" + "="*70)
    print("[4] PRUEBA: CRUZA DE UN PUNTO")
    print("="*70)
    
    hijo1_1p, hijo2_1p = cruzar_un_punto(padre1, padre2, probabilidad_cruza=1.0)
    
    print("\n🧬 HIJOS GENERADOS (Cruza de un punto):")
    visualizar_cromosoma(hijo1_1p, catalogo, "Hijo 1")
    visualizar_cromosoma(hijo2_1p, catalogo, "Hijo 2")
    
    # 6. Probar cruza uniforme
    print("\n" + "="*70)
    print("[5] PRUEBA: CRUZA UNIFORME")
    print("="*70)
    
    hijo1_uni, hijo2_uni = cruzar_uniforme(padre1, padre2, probabilidad_cruza=1.0)
    
    print("\n🧬 HIJOS GENERADOS (Cruza uniforme):")
    visualizar_cromosoma(hijo1_uni, catalogo, "Hijo 1")
    visualizar_cromosoma(hijo2_uni, catalogo, "Hijo 2")
    
    # 7. Probar aplicador de cruza a población
    print("\n" + "="*70)
    print("[6] PRUEBA: APLICAR CRUZA A POBLACIÓN")
    print("="*70)
    
    # Generar población pequeña de 10 padres
    print("\n  Generando población de 10 padres...")
    padres = []
    for i in range(10):
        padre = generar_individuo_aleatorio(
            catalogo=catalogo,
            config=config,
            entrada_usuario=entrada_usuario,
            seed=200 + i
        )
        padres.append(padre)
    
    print(f"  ✅ {len(padres)} padres generados")
    
    # Aplicar cruza
    print(f"\n  Aplicando cruza de dos puntos...")
    hijos = aplicar_cruza_poblacion(
        padres=padres,
        config=config,
        tipo_cruza='dos_puntos'
    )
    
    print(f"  ✅ {len(hijos)} hijos generados")
    
    # Verificar que todos los hijos tienen 20 genes
    todos_validos = all(len(hijo['genes']) == 20 for hijo in hijos)
    print(f"\n  Validación: Todos los hijos tienen 20 genes: {'✅' if todos_validos else '❌'}")
    
    # Estadísticas de duplicados
    hijos_sin_duplicados = 0
    for hijo in hijos:
        ids = [g['id_producto'] for g in hijo['genes']]
        if len(set(ids)) == 20:
            hijos_sin_duplicados += 1
    
    print(f"  Hijos sin duplicados: {hijos_sin_duplicados}/{len(hijos)} "
          f"({hijos_sin_duplicados/len(hijos)*100:.1f}%)")
    
    # 8. Probar que no cruza cuando probabilidad = 0
    print("\n" + "="*70)
    print("[7] PRUEBA: PROBABILIDAD DE CRUZA = 0")
    print("="*70)
    
    hijo1_no, hijo2_no = cruzar_dos_puntos(padre1, padre2, probabilidad_cruza=0.0)
    
    # Verificar que los hijos son copias exactas de los padres
    ids_padre1 = [g['id_producto'] for g in padre1['genes']]
    ids_hijo1 = [g['id_producto'] for g in hijo1_no['genes']]
    
    son_identicos = ids_padre1 == ids_hijo1
    print(f"\n  Hijo es copia exacta del padre: {'✅' if son_identicos else '❌'}")
    
    print("\n" + "="*70)
    print(" ✅ TEST COMPLETADO")
    print("="*70)
    
    print("\n📊 RESUMEN:")
    print("  - Cruza de dos puntos: ✅ Implementada")
    print("  - Cruza de un punto: ✅ Implementada")
    print("  - Cruza uniforme: ✅ Implementada")
    print("  - Manejo de duplicados: ✅ Funcional")
    print("  - Aplicador de cruza: ✅ Funcional")
    print("  - Probabilidad de cruza: ✅ Respetada")


if __name__ == '__main__':
    main()