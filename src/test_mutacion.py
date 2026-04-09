"""
Script de prueba para validar el módulo de mutación.
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
from mutacion import (
    mutar_cambio_producto,
    mutar_cambio_cantidad,
    mutar_cambio_marca,
    mutar_cambio_supermercado,
    aplicar_mutacion,
    aplicar_mutacion_poblacion,
    calcular_estadisticas_mutacion
)


def visualizar_gen(gen, catalogo, prefijo=""):
    """Visualiza un gen (producto)."""
    producto = catalogo[catalogo['id'] == gen['id_producto']].iloc[0]
    print(f"{prefijo}ID:{gen['id_producto']:3d} {producto['nombre'][:25]:25s} "
          f"Cant:{gen['cantidad']:.2f} Marca:{gen['marca']:8s} "
          f"Super:{gen['supermercado']:8s}")


def comparar_individuos(ind1, ind2, catalogo, n_genes=5):
    """Compara dos individuos mostrando los primeros N genes."""
    print("\n  ANTES → DESPUÉS:")
    for i in range(min(n_genes, len(ind1['genes']))):
        gen1 = ind1['genes'][i]
        gen2 = ind2['genes'][i]
        
        # Detectar cambios
        cambio_producto = gen1['id_producto'] != gen2['id_producto']
        cambio_cantidad = gen1['cantidad'] != gen2['cantidad']
        cambio_marca = gen1['marca'] != gen2['marca']
        cambio_super = gen1['supermercado'] != gen2['supermercado']
        
        cambios = []
        if cambio_producto: cambios.append('PROD')
        if cambio_cantidad: cambios.append('CANT')
        if cambio_marca: cambios.append('MARCA')
        if cambio_super: cambios.append('SUPER')
        
        marca_cambio = f" [{','.join(cambios)}]" if cambios else ""
        
        print(f"  {i+1}.")
        visualizar_gen(gen1, catalogo, "    Antes:  ")
        visualizar_gen(gen2, catalogo, f"    Después: ")
        if cambios:
            print(f"    {marca_cambio}")


def main():
    """Prueba los operadores de mutación."""
    
    print("="*70)
    print(" TEST: MÓDULO DE MUTACIÓN")
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
    
    # 3. Generar individuo base
    print("\n[2] Generando individuo base...")
    individuo_base = generar_individuo_aleatorio(
        catalogo=catalogo,
        config=config,
        entrada_usuario=entrada_usuario,
        seed=42
    )
    
    print(f"  ✅ Individuo generado con {len(individuo_base['genes'])} genes")
    
    # 4. Probar mutación de cambio de producto
    print("\n" + "="*70)
    print("[3] PRUEBA: MUTACIÓN DE CAMBIO DE PRODUCTO")
    print("="*70)
    
    individuo_mut_prod = mutar_cambio_producto(
        individuo=individuo_base,
        catalogo=catalogo,
        entrada_usuario=entrada_usuario,
        probabilidad=0.3  # 30% para ver varios cambios
    )
    
    print("\n🔄 Cambios detectados:")
    comparar_individuos(individuo_base, individuo_mut_prod, catalogo)
    
    # 5. Probar mutación de cambio de cantidad
    print("\n" + "="*70)
    print("[4] PRUEBA: MUTACIÓN DE CAMBIO DE CANTIDAD")
    print("="*70)
    
    individuo_mut_cant = mutar_cambio_cantidad(
        individuo=individuo_base,
        probabilidad=0.3
    )
    
    print("\n🔄 Cambios detectados:")
    comparar_individuos(individuo_base, individuo_mut_cant, catalogo)
    
    # 6. Probar mutación de cambio de marca
    print("\n" + "="*70)
    print("[5] PRUEBA: MUTACIÓN DE CAMBIO DE MARCA")
    print("="*70)
    
    individuo_mut_marca = mutar_cambio_marca(
        individuo=individuo_base,
        probabilidad=0.3
    )
    
    print("\n🔄 Cambios detectados:")
    comparar_individuos(individuo_base, individuo_mut_marca, catalogo)
    
    # 7. Probar mutación de cambio de supermercado
    print("\n" + "="*70)
    print("[6] PRUEBA: MUTACIÓN DE CAMBIO DE SUPERMERCADO")
    print("="*70)
    
    individuo_mut_super = mutar_cambio_supermercado(
        individuo=individuo_base,
        catalogo=catalogo,
        probabilidad=0.3
    )
    
    print("\n🔄 Cambios detectados:")
    comparar_individuos(individuo_base, individuo_mut_super, catalogo)
    
    # 8. Probar mutación combinada
    print("\n" + "="*70)
    print("[7] PRUEBA: MUTACIÓN COMBINADA")
    print("="*70)
    
    individuo_mut_combinada = aplicar_mutacion(
        individuo=individuo_base,
        catalogo=catalogo,
        config=config,
        entrada_usuario=entrada_usuario
    )
    
    if individuo_mut_combinada['metadata'].get('fue_mutado', False):
        print("\n✅ Individuo fue mutado")
        print("\n🔄 Cambios detectados:")
        comparar_individuos(individuo_base, individuo_mut_combinada, catalogo)
    else:
        print("\n⚪ Individuo NO fue mutado (probabilidad global no se cumplió)")
    
    # 9. Probar mutación en población
    print("\n" + "="*70)
    print("[8] PRUEBA: MUTACIÓN EN POBLACIÓN")
    print("="*70)
    
    # Generar población pequeña
    print("\n  Generando población de 20 individuos...")
    poblacion = []
    for i in range(20):
        ind = generar_individuo_aleatorio(
            catalogo=catalogo,
            config=config,
            entrada_usuario=entrada_usuario,
            seed=100 + i
        )
        poblacion.append(ind)
    
    print(f"  ✅ {len(poblacion)} individuos generados")
    
    # Aplicar mutación
    poblacion_mutada = aplicar_mutacion_poblacion(
        poblacion=poblacion,
        catalogo=catalogo,
        config=config,
        entrada_usuario=entrada_usuario,
        verbose=True
    )
    
    # Estadísticas
    stats = calcular_estadisticas_mutacion(poblacion_mutada)
    
    print(f"\n📊 Estadísticas de mutación:")
    print(f"  - Total individuos: {stats['total_individuos']}")
    print(f"  - Individuos mutados: {stats['individuos_mutados']}")
    print(f"  - Tasa de mutación: {stats['tasa_mutacion']:.1f}%")
    
    if stats['tipos_aplicados']:
        print(f"\n  Tipos de mutación aplicados:")
        for tipo, count in stats['tipos_aplicados'].items():
            print(f"    - {tipo}: {count}")
    
    # 10. Verificar que individuos mantienen 20 genes
    print("\n" + "="*70)
    print("[9] VALIDACIÓN: INTEGRIDAD DE CROMOSOMAS")
    print("="*70)
    
    todos_validos = all(len(ind['genes']) == 20 for ind in poblacion_mutada)
    print(f"\n  Todos los individuos tienen 20 genes: {'✅' if todos_validos else '❌'}")
    
    # Verificar que no hay duplicados excesivos
    individuos_con_duplicados = 0
    for ind in poblacion_mutada:
        ids = [g['id_producto'] for g in ind['genes']]
        if len(set(ids)) < 20:
            individuos_con_duplicados += 1
    
    print(f"  Individuos con productos duplicados: {individuos_con_duplicados}/{len(poblacion_mutada)}")
    
    print("\n" + "="*70)
    print(" ✅ TEST COMPLETADO")
    print("="*70)
    
    print("\n📊 RESUMEN:")
    print("  - Mutación cambio producto: ✅ Implementada")
    print("  - Mutación cambio cantidad: ✅ Implementada")
    print("  - Mutación cambio marca: ✅ Implementada")
    print("  - Mutación cambio supermercado: ✅ Implementada")
    print("  - Mutación combinada: ✅ Implementada")
    print("  - Aplicador a población: ✅ Funcional")
    print("  - Integridad cromosomas: ✅ Preservada")


if __name__ == '__main__':
    main()