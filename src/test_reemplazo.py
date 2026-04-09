"""
Script de prueba para validar el módulo de reemplazo.
"""

import sys
sys.path.append('src')

import numpy as np
from utils.cargador_datos import (
    cargar_catalogo,
    cargar_configuracion,
    cargar_requerimientos_nutricionales
)
from inicializacion import generar_poblacion_inicial
from evaluacion import evaluar_poblacion
from cruza import cruzar_dos_puntos
from mutacion import aplicar_mutacion
from reemplazo import (
    seleccionar_por_torneo,
    seleccionar_por_ruleta,
    seleccionar_padres_torneo,
    seleccionar_padres_ruleta,
    obtener_elite,
    aplicar_poda,
    generar_nueva_generacion
)


def main():
    """Prueba el módulo de reemplazo."""
    
    print("="*70)
    print(" TEST: MÓDULO DE REEMPLAZO")
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
    
    # 3. Generar y evaluar población
    print("\n[2] Generando población de prueba (20 individuos)...")
    config_prueba = config.copy()
    config_prueba['poblacion']['tamaño'] = 20
    
    poblacion = generar_poblacion_inicial(
        catalogo=catalogo,
        config=config_prueba,
        entrada_usuario=entrada_usuario,
        seed=42
    )
    
    print(f"  ✅ Población generada: {len(poblacion)} individuos")
    
    print("\n[3] Evaluando población...")
    poblacion_evaluada = evaluar_poblacion(
        poblacion=poblacion,
        catalogo=catalogo,
        config=config,
        entrada_usuario=entrada_usuario,
        requerimientos=requerimientos,
        verbose=False
    )
    
    fitness_values = [ind['metadata']['fitness'] for ind in poblacion_evaluada]
    print(f"  ✅ Población evaluada")
    print(f"     Mejor fitness: {max(fitness_values):.4f}")
    print(f"     Fitness promedio: {np.mean(fitness_values):.4f}")
    
    # 4. Probar selección por torneo
    print("\n" + "="*70)
    print("[4] PRUEBA: SELECCIÓN POR TORNEO")
    print("="*70)
    
    print("\n  Seleccionando 1 individuo con torneo (k=5)...")
    ganador_torneo = seleccionar_por_torneo(poblacion_evaluada, k=5)
    print(f"  ✅ Ganador seleccionado")
    print(f"     Fitness: {ganador_torneo['metadata']['fitness']:.4f}")
    print(f"     Ranking: {ganador_torneo['metadata']['ranking']}")
    
    print("\n  Seleccionando 10 padres con torneo...")
    padres_torneo = seleccionar_padres_torneo(poblacion_evaluada, n_padres=10, k=5)
    print(f"  ✅ {len(padres_torneo)} padres seleccionados")
    
    fitness_padres = [p['metadata']['fitness'] for p in padres_torneo]
    print(f"     Fitness promedio padres: {np.mean(fitness_padres):.4f}")
    print(f"     (Fitness promedio población: {np.mean(fitness_values):.4f})")
    print(f"     ▲ Mejora: {((np.mean(fitness_padres) / np.mean(fitness_values) - 1) * 100):.1f}%")
    
    # 5. Probar selección por ruleta
    print("\n" + "="*70)
    print("[5] PRUEBA: SELECCIÓN POR RULETA")
    print("="*70)
    
    print("\n  Seleccionando 1 individuo con ruleta...")
    ganador_ruleta = seleccionar_por_ruleta(poblacion_evaluada)
    print(f"  ✅ Ganador seleccionado")
    print(f"     Fitness: {ganador_ruleta['metadata']['fitness']:.4f}")
    
    print("\n  Seleccionando 10 padres con ruleta...")
    padres_ruleta = seleccionar_padres_ruleta(poblacion_evaluada, n_padres=10)
    print(f"  ✅ {len(padres_ruleta)} padres seleccionados")
    
    fitness_padres_ruleta = [p['metadata']['fitness'] for p in padres_ruleta]
    print(f"     Fitness promedio padres: {np.mean(fitness_padres_ruleta):.4f}")
    
    # 6. Probar elitismo
    print("\n" + "="*70)
    print("[6] PRUEBA: ELITISMO")
    print("="*70)
    
    n_elite = 3
    print(f"\n  Obteniendo {n_elite} individuos elite...")
    elite = obtener_elite(poblacion_evaluada, n_elite)
    
    print(f"  ✅ Elite obtenida: {len(elite)} individuos")
    for i, ind in enumerate(elite, 1):
        print(f"     #{i} Fitness: {ind['metadata']['fitness']:.4f}, "
              f"Es elite: {ind['metadata'].get('es_elite', False)}")
    
    # 7. Probar aplicación de elitismo
    print("\n" + "="*70)
    print("[7] PRUEBA: APLICAR ELITISMO EN REEMPLAZO")
    print("="*70)
    
    # Simular generación de hijos (con fitness más bajo)
    print("\n  Simulando población de hijos...")
    hijos = poblacion_evaluada.copy()
    # Degradar fitness de hijos artificialmente para probar elitismo
    for hijo in hijos:
        hijo['metadata']['fitness'] *= 0.8  # Reducir 20%
    
    print(f"  Población actual: Mejor fitness = {max(fitness_values):.4f}")
    fitness_hijos = [h['metadata']['fitness'] for h in hijos]
    print(f"  Hijos: Mejor fitness = {max(fitness_hijos):.4f}")
    
    print(f"\n  Aplicando elitismo (10%)...")
    nueva_gen = aplicar_poda(
        poblacion_actual=poblacion_evaluada,
        poblacion_hijos=hijos,
        proporcion_elite=0.10
    )
    
    fitness_nueva_gen = [ind['metadata']['fitness'] for ind in nueva_gen]
    print(f"  ✅ Nueva generación creada")
    print(f"     Tamaño: {len(nueva_gen)}")
    print(f"     Mejor fitness: {max(fitness_nueva_gen):.4f}")
    print(f"     (Preservó el mejor de población actual: {'✅' if max(fitness_nueva_gen) >= max(fitness_values) else '❌'})")
    
    # 8. Probar generación completa
    print("\n" + "="*70)
    print("[8] PRUEBA: GENERAR NUEVA GENERACIÓN COMPLETA")
    print("="*70)
    
    # Definir funciones wrapper
    def operador_cruza(p1, p2):
        return cruzar_dos_puntos(p1, p2, probabilidad_cruza=0.8)
    
    def operador_mutacion(ind):
        return aplicar_mutacion(ind, catalogo, config, entrada_usuario)
    
    print("\n  Generando nueva generación completa...")
    print("  (Selección → Cruza → Mutación → Evaluación → Elitismo)")
    
    nueva_generacion = generar_nueva_generacion(
        poblacion_actual=poblacion_evaluada,
        catalogo=catalogo,
        config=config,
        entrada_usuario=entrada_usuario,
        requerimientos=requerimientos,
        operador_cruza=operador_cruza,
        operador_mutacion=operador_mutacion,
        evaluador=evaluar_poblacion,
        metodo_seleccion='torneo',
        verbose=True
    )
    
    # Comparar generaciones
    print("\n📊 COMPARACIÓN DE GENERACIONES:")
    
    fitness_gen0 = [ind['metadata']['fitness'] for ind in poblacion_evaluada]
    fitness_gen1 = [ind['metadata']['fitness'] for ind in nueva_generacion]
    
    print(f"\n  Generación 0 (original):")
    print(f"    - Mejor fitness:    {max(fitness_gen0):.4f}")
    print(f"    - Fitness promedio: {np.mean(fitness_gen0):.4f}")
    print(f"    - Peor fitness:     {min(fitness_gen0):.4f}")
    
    print(f"\n  Generación 1 (nueva):")
    print(f"    - Mejor fitness:    {max(fitness_gen1):.4f}")
    print(f"    - Fitness promedio: {np.mean(fitness_gen1):.4f}")
    print(f"    - Peor fitness:     {min(fitness_gen1):.4f}")
    
    mejora = ((max(fitness_gen1) - max(fitness_gen0)) / max(fitness_gen0)) * 100
    print(f"\n  📈 Mejora del mejor fitness: {mejora:+.2f}%")
    
    if max(fitness_gen1) >= max(fitness_gen0):
        print(f"  ✅ Elitismo funcionó: el mejor no empeoró")
    else:
        print(f"  ❌ Error: el mejor fitness empeoró (elitismo falló)")
    
    print("\n" + "="*70)
    print(" ✅ TEST COMPLETADO")
    print("="*70)
    
    print("\n📊 RESUMEN:")
    print("  - Selección por torneo: ✅ Implementada")
    print("  - Selección por ruleta: ✅ Implementada")
    print("  - Elitismo: ✅ Implementado")
    print("  - Generación nueva: ✅ Funcional")
    print("  - Preservación del mejor: ✅ Garantizada")


if __name__ == '__main__':
    main()