"""
Script de prueba para validar el módulo de fitness.
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
from fitness import calcular_fitness_total


def main():
    """Prueba el módulo de fitness."""
    
    print("="*70)
    print(" TEST: MÓDULO DE FITNESS")
    print("="*70)
    
    # 1. Cargar datos
    print("\n[1] Cargando datos...")
    catalogo = cargar_catalogo()
    config = cargar_configuracion()
    requerimientos = cargar_requerimientos_nutricionales()
    
    # 2. Entrada de usuario
    entrada_usuario = {
        'presupuesto': 1500,
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
    
    # 3. Generar individuo de prueba
    print("\n[2] Generando individuo de prueba...")
    individuo = generar_individuo_aleatorio(
        catalogo=catalogo,
        config=config,
        entrada_usuario=entrada_usuario,
        seed=42
    )
    
    # 4. Calcular fitness
    print("\n[3] Calculando fitness...")
    fitness_total = calcular_fitness_total(
        individuo=individuo,
        catalogo=catalogo,
        config=config,
        entrada_usuario=entrada_usuario,
        requerimientos=requerimientos
    )
    
    # 5. Mostrar resultados
    print("\n" + "="*70)
    print(" RESULTADOS DE FITNESS")
    print("="*70)
    
    print(f"\n🎯 FITNESS TOTAL: {fitness_total:.4f}")
    
    print("\n📊 COMPONENTES DE FITNESS:")
    componentes = individuo['metadata']['fitness_componentes']
    pesos = config['fitness']['pesos']
    
    print(f"  1. Costo:        {componentes['costo']:.4f} (peso: {pesos['costo']})")
    print(f"  2. Nutrición:    {componentes['nutricion']:.4f} (peso: {pesos['nutricion']})")
    print(f"  3. Desperdicio:  {componentes['desperdicio']:.4f} (peso: {pesos['desperdicio']})")
    print(f"  4. Cobertura:    {componentes['cobertura']:.4f} (peso: {pesos['cobertura']})")
    print(f"  5. Satisfacción: {componentes['satisfaccion']:.4f} (peso: {pesos['satisfaccion']})")
    
    print(f"\n💰 COSTO TOTAL: ${individuo['metadata']['costo_total']:.2f} MXN")
    print(f"   Presupuesto: ${entrada_usuario['presupuesto']:.2f} MXN")
    
    # Información nutricional
    if 'nutricion' in individuo['metadata']:
        print("\n🥗 NUTRICIÓN:")
        cumplimientos = individuo['metadata']['nutricion']['cumplimientos']
        for nutriente, cumplimiento in cumplimientos.items():
            print(f"   {nutriente}: {cumplimiento*100:.1f}%")
    
    # Información de desperdicio
    if 'desperdicio' in individuo['metadata']:
        print("\n♻️  DESPERDICIO:")
        desp = individuo['metadata']['desperdicio']
        print(f"   Estimado: ${desp['desperdicio_estimado']:.2f} MXN")
        print(f"   Ratio: {desp['ratio_desperdicio']*100:.1f}%")
        print(f"   Productos perecederos: {desp['num_perecederos']}")
    
    # Violaciones
    if individuo['metadata']['violaciones']:
        print("\n⚠️  VIOLACIONES:")
        for v in individuo['metadata']['violaciones']:
            print(f"   - {v['tipo']}: {v['detalle']}")
    else:
        print("\n✅ Sin violaciones de restricciones")
    
    print("\n" + "="*70)
    print(" ✅ TEST COMPLETADO")
    print("="*70)


if __name__ == '__main__':
    main()