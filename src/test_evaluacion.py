"""
Script de prueba para validar el módulo de evaluación.
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
from evaluacion import (
    evaluar_poblacion,
    validar_restricciones_duras,
    contar_violaciones_poblacion
)
from utils.reparador import reparar_individuo


def main():
    """Prueba el módulo de evaluación."""
    
    print("="*70)
    print(" TEST: MÓDULO DE EVALUACIÓN")
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
    
    # 3. Generar población pequeña para prueba
    print("\n[2] Generando población de prueba (20 individuos)...")
    config_prueba = config.copy()
    config_prueba['poblacion']['tamaño'] = 20
    
    poblacion = generar_poblacion_inicial(
        catalogo=catalogo,
        config=config_prueba,
        entrada_usuario=entrada_usuario,
        seed=42
    )
    
    # 4. Evaluar población
    print("\n[3] Evaluando población...")
    poblacion_evaluada = evaluar_poblacion(
        poblacion=poblacion,
        catalogo=catalogo,
        config=config,
        entrada_usuario=entrada_usuario,
        requerimientos=requerimientos,
        verbose=True
    )
    
    # 5. Validar restricciones en toda la población
    print("\n[4] Validando restricciones duras...")
    for individuo in poblacion_evaluada:
        es_valido, violaciones = validar_restricciones_duras(
            individuo=individuo,
            catalogo=catalogo,
            config=config,
            entrada_usuario=entrada_usuario
        )
        
        # Las violaciones ya están en metadata, solo verificamos
        if not es_valido:
            individuo['metadata']['violaciones'].extend(violaciones)
    
    # Contar violaciones
    stats_violaciones = contar_violaciones_poblacion(poblacion_evaluada)
    
    print(f"\n📋 Estadísticas de violaciones:")
    print(f"  - Individuos válidos: {stats_violaciones['individuos_validos']}/{stats_violaciones['total_individuos']}")
    print(f"  - Individuos inválidos: {stats_violaciones['individuos_invalidos']}")
    print(f"  - Porcentaje válidos: {stats_violaciones['porcentaje_validos']:.1f}%")
    
    if stats_violaciones['violaciones_por_tipo']:
        print(f"\n  Violaciones por tipo:")
        for tipo, count in stats_violaciones['violaciones_por_tipo'].items():
            print(f"    - {tipo}: {count}")
    
    # 6. Probar reparación de un individuo inválido
    individuos_invalidos = [
        ind for ind in poblacion_evaluada 
        if not ind['metadata']['es_valido']
    ]
    
    if individuos_invalidos:
        print(f"\n[5] Probando reparación de individuos inválidos...")
        print(f"  Encontrados {len(individuos_invalidos)} individuos inválidos")
        
        # Reparar el primer inválido
        individuo_invalido = individuos_invalidos[0]
        print(f"\n  Reparando individuo con violaciones:")
        for v in individuo_invalido['metadata']['violaciones']:
            print(f"    - {v['tipo']}: {v['detalle']}")
        
        individuo_reparado = reparar_individuo(
            individuo=individuo_invalido,
            catalogo=catalogo,
            config=config,
            entrada_usuario=entrada_usuario
        )
        
        # Re-validar
        es_valido_ahora, _ = validar_restricciones_duras(
            individuo=individuo_reparado,
            catalogo=catalogo,
            config=config,
            entrada_usuario=entrada_usuario
        )
        
        print(f"\n  ✅ Individuo reparado. Válido ahora: {es_valido_ahora}")
    else:
        print(f"\n[5] No hay individuos inválidos para reparar. ¡Excelente!")
    
    # 7. Mostrar mejores individuos
    print(f"\n[6] Top 3 mejores individuos:")
    for i, individuo in enumerate(poblacion_evaluada[:3], 1):
        print(f"\n  #{i} - Fitness: {individuo['metadata']['fitness']:.4f}")
        print(f"       Costo: ${individuo['metadata']['costo_total']:.2f}")
        componentes = individuo['metadata']['fitness_componentes']
        print(f"       Componentes: C={componentes['costo']:.3f}, "
              f"N={componentes['nutricion']:.3f}, "
              f"D={componentes['desperdicio']:.3f}, "
              f"Cb={componentes['cobertura']:.3f}, "
              f"S={componentes['satisfaccion']:.3f}")
    
    print("\n" + "="*70)
    print(" ✅ TEST COMPLETADO")
    print("="*70)


if __name__ == '__main__':
    main()