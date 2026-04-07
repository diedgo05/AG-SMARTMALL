"""
Script para generar tabla de requerimientos nutricionales diarios
según edad y género (basado en recomendaciones de la OMS/FAO).
"""

import pandas as pd

def generar_requerimientos_nutricionales():
    """
    Genera tabla de requerimientos nutricionales diarios.
    
    Basado en:
    - OMS/FAO Guidelines
    - Norma Oficial Mexicana NOM-043-SSA2-2012
    """
    
    requerimientos = [
        {
            'edad_grupo': 'adulto',
            'genero': 'masculino',
            'calorias_dia': 2500,
            'proteinas_g_dia': 75,
            'carbohidratos_g_dia': 312,  # 50% de calorías
            'grasas_g_dia': 83,  # 30% de calorías
            'fibra_g_dia': 30,
            'descripcion': 'Hombre adulto (19-65 años) actividad moderada'
        },
        {
            'edad_grupo': 'adulto',
            'genero': 'femenino',
            'calorias_dia': 2000,
            'proteinas_g_dia': 60,
            'carbohidratos_g_dia': 250,
            'grasas_g_dia': 67,
            'fibra_g_dia': 25,
            'descripcion': 'Mujer adulta (19-65 años) actividad moderada'
        },
        {
            'edad_grupo': 'adulto',
            'genero': 'embarazada',
            'calorias_dia': 2200,
            'proteinas_g_dia': 71,
            'carbohidratos_g_dia': 275,
            'grasas_g_dia': 73,
            'fibra_g_dia': 28,
            'descripcion': 'Mujer embarazada (segundo/tercer trimestre)'
        },
        {
            'edad_grupo': 'niño_13_18',
            'genero': 'masculino',
            'calorias_dia': 2800,
            'proteinas_g_dia': 85,
            'carbohidratos_g_dia': 350,
            'grasas_g_dia': 93,
            'fibra_g_dia': 31,
            'descripcion': 'Adolescente masculino (13-18 años)'
        },
        {
            'edad_grupo': 'niño_13_18',
            'genero': 'femenino',
            'calorias_dia': 2200,
            'proteinas_g_dia': 65,
            'carbohidratos_g_dia': 275,
            'grasas_g_dia': 73,
            'fibra_g_dia': 26,
            'descripcion': 'Adolescente femenino (13-18 años)'
        },
        {
            'edad_grupo': 'niño_8_12',
            'genero': 'ambos',
            'calorias_dia': 1800,
            'proteinas_g_dia': 50,
            'carbohidratos_g_dia': 225,
            'grasas_g_dia': 60,
            'fibra_g_dia': 20,
            'descripcion': 'Niño/a (8-12 años)'
        },
        {
            'edad_grupo': 'niño_4_7',
            'genero': 'ambos',
            'calorias_dia': 1400,
            'proteinas_g_dia': 40,
            'carbohidratos_g_dia': 175,
            'grasas_g_dia': 47,
            'fibra_g_dia': 15,
            'descripcion': 'Niño/a (4-7 años)'
        },
        {
            'edad_grupo': 'niño_1_3',
            'genero': 'ambos',
            'calorias_dia': 1000,
            'proteinas_g_dia': 25,
            'carbohidratos_g_dia': 125,
            'grasas_g_dia': 33,
            'fibra_g_dia': 10,
            'descripcion': 'Niño/a (1-3 años)'
        },
        {
            'edad_grupo': 'adulto_mayor',
            'genero': 'masculino',
            'calorias_dia': 2000,
            'proteinas_g_dia': 65,
            'carbohidratos_g_dia': 250,
            'grasas_g_dia': 67,
            'fibra_g_dia': 25,
            'descripcion': 'Hombre adulto mayor (>65 años)'
        },
        {
            'edad_grupo': 'adulto_mayor',
            'genero': 'femenino',
            'calorias_dia': 1600,
            'proteinas_g_dia': 50,
            'carbohidratos_g_dia': 200,
            'grasas_g_dia': 53,
            'fibra_g_dia': 21,
            'descripcion': 'Mujer adulta mayor (>65 años)'
        }
    ]
    
    df = pd.DataFrame(requerimientos)
    return df


if __name__ == '__main__':
    print("Generando tabla de requerimientos nutricionales...")
    
    reqs = generar_requerimientos_nutricionales()
    
    # Guardar a CSV
    reqs.to_csv('../data/requerimientos_nutricionales.csv', index=False, encoding='utf-8')
    
    print(f"✅ Tabla generada: {len(reqs)} grupos demográficos")
    print("\nRequerimientos nutricionales:")
    print(reqs[['edad_grupo', 'genero', 'calorias_dia', 'proteinas_g_dia', 'descripcion']])