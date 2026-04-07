"""
Script de prueba para validar el módulo de inicialización.
"""

import sys
sys.path.append('src')

from utils.cargador_datos import (
    cargar_catalogo,
    cargar_configuracion,
    cargar_requerimientos_nutricionales
)
from inicializacion.poblacion import generar_poblacion_inicial


def main():
    """Prueba el módulo de inicialización."""
    
    print("="*70)
    print(" TEST: MÓDULO DE INICIALIZACIÓN")
    print("="*70)
    
    # 1. Cargar datos
    print("\n[1] Cargando datos...")
    catalogo = cargar_catalogo()
    config = cargar_configuracion()
    requerimientos = cargar_requerimientos_nutricionales()
    
    # 2. Definir entrada de usuario (ejemplo)
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
        'inventario_actual': [
            {'id_producto': 4, 'cantidad': 0.5},
        ],
        'comidas_planificadas': 21
    }
    
    print("\n[2] Entrada del usuario:")
    print(f"  - Presupuesto: ${entrada_usuario['presupuesto']} MXN")
    print(f"  - Familia: {entrada_usuario['num_personas']} personas")
    print(f"  - Periodo: {entrada_usuario['periodo_dias']} días")
    print(f"  - Alérgenos prohibidos: {entrada_usuario['alergenos_prohibidos']}")
    
    # 3. Generar población
    print("\n[3] Generando población...")
    poblacion = generar_poblacion_inicial(
        catalogo=catalogo,
        config=config,
        entrada_usuario=entrada_usuario,
        seed=42
    )
    
    # 4. Inspeccionar primer individuo
    print("\n[4] Inspeccionando primer individuo:")
    individuo_ejemplo = poblacion[0]
    
    print(f"\n  Genes (productos):")
    for i, gen in enumerate(individuo_ejemplo['genes'][:5], 1):  # Mostrar solo 5
        prod_info = catalogo[catalogo['id'] == gen['id_producto']].iloc[0]
        print(f"    {i}. {prod_info['nombre']}")
        print(f"       - Cantidad: {gen['cantidad']} {prod_info['unidad']}")
        print(f"       - Marca: {gen['marca']}")
        print(f"       - Supermercado: {gen['supermercado']}")
    
    print(f"\n  ... (mostrando solo 5 de {len(individuo_ejemplo['genes'])} productos)")
    
    print("\n" + "="*70)
    print(" ✅ TEST COMPLETADO EXITOSAMENTE")
    print("="*70)


if __name__ == '__main__':
    main()