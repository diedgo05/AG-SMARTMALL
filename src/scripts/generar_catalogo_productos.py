"""
Script para generar catálogo simulado de 300 productos de supermercado
con precios, información nutricional y disponibilidad realistas para México 2026.
"""

import pandas as pd
import numpy as np

def generar_catalogo_productos(n_productos=300, seed=42):
    """
    Genera catálogo de productos simulado pero realista.
    
    Parameters:
    -----------
    n_productos : int
        Número de productos a generar (default: 300)
    seed : int
        Semilla para reproducibilidad
        
    Returns:
    --------
    pd.DataFrame
        Catálogo de productos
    """
    np.random.seed(seed)
    
    # Definir categorías de productos con ejemplos mexicanos
    categorias_productos = {
        'Lácteos': [
            'Leche entera', 'Leche deslactosada', 'Leche light', 'Yogurt natural',
            'Yogurt griego', 'Queso panela', 'Queso oaxaca', 'Queso manchego',
            'Crema', 'Mantequilla', 'Queso fresco', 'Yogurt bebible'
        ],
        'Panadería': [
            'Pan blanco', 'Pan integral', 'Pan de caja', 'Tortillas de maíz',
            'Tortillas de harina', 'Bolillo', 'Pan dulce', 'Galletas saladas',
            'Galletas Marías', 'Tostadas', 'Pan tostado integral'
        ],
        'Proteínas': [
            'Huevos blancos', 'Huevos rojos', 'Pollo entero', 'Pechuga de pollo',
            'Muslo de pollo', 'Carne molida de res', 'Bistec de res', 
            'Chuleta de cerdo', 'Costilla de cerdo', 'Atún en agua',
            'Atún en aceite', 'Sardinas', 'Salchicha de pavo', 'Jamón de pavo'
        ],
        'Granos y Legumbres': [
            'Arroz blanco', 'Arroz integral', 'Frijol negro', 'Frijol pinto',
            'Lentejas', 'Garbanzo', 'Haba seca', 'Avena', 'Pasta espagueti',
            'Pasta coditos', 'Pasta tornillo', 'Sopa de pasta', 'Cereal corn flakes',
            'Cereal de avena', 'Granola'
        ],
        'Frutas': [
            'Manzana roja', 'Manzana verde', 'Plátano', 'Naranja', 'Mandarina',
            'Papaya', 'Sandía', 'Melón', 'Piña', 'Uva', 'Pera', 'Fresa',
            'Mango', 'Aguacate', 'Limón', 'Toronja'
        ],
        'Verduras': [
            'Jitomate', 'Cebolla blanca', 'Papa', 'Zanahoria', 'Lechuga romana',
            'Lechuga italiana', 'Brócoli', 'Coliflor', 'Calabaza', 'Chayote',
            'Pepino', 'Chile poblano', 'Chile jalapeño', 'Espinaca', 'Acelga',
            'Ejotes', 'Elote', 'Cilantro', 'Perejil', 'Ajo'
        ],
        'Aceites y Condimentos': [
            'Aceite vegetal', 'Aceite de oliva', 'Sal de mesa', 'Azúcar',
            'Vinagre blanco', 'Salsa de soja', 'Mayonesa', 'Mostaza',
            'Catsup', 'Salsa valentina', 'Salsa botanera', 'Consomé de pollo',
            'Pimienta negra', 'Comino'
        ],
        'Bebidas': [
            'Agua natural embotellada', 'Agua mineral', 'Jugo de naranja',
            'Jugo de manzana', 'Refresco de cola', 'Refresco de limón',
            'Té negro', 'Té verde', 'Café soluble', 'Café molido',
            'Chocolate en polvo', 'Leche de soja'
        ],
        'Enlatados': [
            'Frijoles refritos', 'Chiles jalapeños', 'Elote amarillo',
            'Champiñones', 'Puré de tomate', 'Salsa de tomate',
            'Sopa de verduras', 'Chicharos'
        ],
        'Congelados': [
            'Verduras mixtas congeladas', 'Brócoli congelado', 'Coliflor congelada',
            'Pizza congelada', 'Hamburguesa congelada', 'Helado de vainilla',
            'Helado de chocolate', 'Paletas de hielo'
        ],
        'Botanas': [
            'Papas fritas', 'Chicharrón preparado', 'Cacahuates japoneses',
            'Palomitas de maíz', 'Tostitos', 'Doritos', 'Cheetos',
            'Chocolate en barra', 'Gomitas', 'Mazapán'
        ]
    }
    
    # Supermercados disponibles
    supermercados_disponibles = ['walmart', 'soriana', 'chedraui', 'bodega']
    
    # Alérgenos comunes
    alergenos_posibles = ['gluten', 'lactosa', 'huevo', 'soja', 'nuez', 'mariscos']
    
    # Unidades de medida
    unidades_por_categoria = {
        'Lácteos': 'litro',
        'Panadería': 'paquete',
        'Proteínas': 'kg',
        'Granos y Legumbres': 'kg',
        'Frutas': 'kg',
        'Verduras': 'kg',
        'Aceites y Condimentos': 'litro',
        'Bebidas': 'litro',
        'Enlatados': 'lata',
        'Congelados': 'paquete',
        'Botanas': 'paquete'
    }
    
    # Generar productos
    productos = []
    id_producto = 1
    
    for categoria, nombres in categorias_productos.items():
        for nombre in nombres:
            # Información básica
            producto = {
                'id': id_producto,
                'nombre': nombre,
                'categoria': categoria,
                'unidad': unidades_por_categoria[categoria]
            }
            
            # Generar precios realistas (marca genérica < media < premium)
            precio_base = np.random.uniform(15, 150)
            producto['precio_generica'] = round(precio_base, 2)
            producto['precio_media'] = round(precio_base * 1.25, 2)
            producto['precio_premium'] = round(precio_base * 1.60, 2)
            
            # Información nutricional (por 100g o 100ml)
            calorias, proteinas, carbos, grasas, fibra = generar_info_nutricional(categoria)
            producto['calorias'] = calorias
            producto['proteinas_g'] = proteinas
            producto['carbohidratos_g'] = carbos
            producto['grasas_g'] = grasas
            producto['fibra_g'] = fibra
            
            # Vida útil (días)
            producto['vida_util_dias'] = asignar_vida_util(categoria)
            
            # Alérgenos
            producto['alergenos'] = asignar_alergenos(categoria, nombre)
            
            # Supermercados donde está disponible (aleatorio, 2-4 tiendas)
            n_tiendas = np.random.randint(2, 5)
            tiendas = np.random.choice(supermercados_disponibles, n_tiendas, replace=False)
            producto['supermercados'] = ','.join(sorted(tiendas))
            
            productos.append(producto)
            id_producto += 1
            
            # Si ya tenemos suficientes productos, parar
            if id_producto > n_productos:
                break
        
        if id_producto > n_productos:
            break
    
    # Convertir a DataFrame
    df = pd.DataFrame(productos)
    
    return df


def generar_info_nutricional(categoria):
    """
    Genera información nutricional realista según categoría.
    
    Returns:
    --------
    tuple: (calorias, proteinas_g, carbohidratos_g, grasas_g, fibra_g)
    """
    
    # Valores nutricionales típicos por categoría (por 100g/100ml)
    perfiles_nutricionales = {
        'Lácteos': {
            'calorias': (50, 150),
            'proteinas': (3, 10),
            'carbohidratos': (4, 15),
            'grasas': (0, 10),
            'fibra': (0, 0)
        },
        'Panadería': {
            'calorias': (200, 350),
            'proteinas': (5, 12),
            'carbohidratos': (40, 70),
            'grasas': (1, 10),
            'fibra': (1, 8)
        },
        'Proteínas': {
            'calorias': (100, 250),
            'proteinas': (15, 35),
            'carbohidratos': (0, 5),
            'grasas': (2, 20),
            'fibra': (0, 0)
        },
        'Granos y Legumbres': {
            'calorias': (300, 400),
            'proteinas': (5, 20),
            'carbohidratos': (60, 85),
            'grasas': (1, 8),
            'fibra': (2, 15)
        },
        'Frutas': {
            'calorias': (30, 90),
            'proteinas': (0, 2),
            'carbohidratos': (8, 25),
            'grasas': (0, 15),  # Aguacate alto en grasa
            'fibra': (1, 8)
        },
        'Verduras': {
            'calorias': (15, 80),
            'proteinas': (1, 5),
            'carbohidratos': (3, 18),
            'grasas': (0, 1),
            'fibra': (1, 5)
        },
        'Aceites y Condimentos': {
            'calorias': (50, 900),
            'proteinas': (0, 5),
            'carbohidratos': (0, 80),
            'grasas': (0, 100),
            'fibra': (0, 2)
        },
        'Bebidas': {
            'calorias': (0, 120),
            'proteinas': (0, 3),
            'carbohidratos': (0, 30),
            'grasas': (0, 3),
            'fibra': (0, 1)
        },
        'Enlatados': {
            'calorias': (50, 150),
            'proteinas': (2, 10),
            'carbohidratos': (8, 25),
            'grasas': (0, 5),
            'fibra': (1, 6)
        },
        'Congelados': {
            'calorias': (100, 300),
            'proteinas': (3, 15),
            'carbohidratos': (15, 40),
            'grasas': (2, 15),
            'fibra': (1, 5)
        },
        'Botanas': {
            'calorias': (400, 550),
            'proteinas': (5, 15),
            'carbohidratos': (50, 70),
            'grasas': (15, 35),
            'fibra': (1, 6)
        }
    }
    
    perfil = perfiles_nutricionales.get(categoria, perfiles_nutricionales['Granos y Legumbres'])
    
    calorias = int(np.random.uniform(*perfil['calorias']))
    proteinas = round(np.random.uniform(*perfil['proteinas']), 1)
    carbohidratos = round(np.random.uniform(*perfil['carbohidratos']), 1)
    grasas = round(np.random.uniform(*perfil['grasas']), 1)
    fibra = round(np.random.uniform(*perfil['fibra']), 1)
    
    return calorias, proteinas, carbohidratos, grasas, fibra


def asignar_vida_util(categoria):
    """Asigna vida útil en días según categoría."""
    vidas_utiles = {
        'Lácteos': (5, 14),
        'Panadería': (3, 10),
        'Proteínas': (2, 7),
        'Granos y Legumbres': (180, 730),
        'Frutas': (3, 14),
        'Verduras': (3, 10),
        'Aceites y Condimentos': (180, 730),
        'Bebidas': (30, 365),
        'Enlatados': (365, 1095),
        'Congelados': (60, 180),
        'Botanas': (60, 365)
    }
    
    rango = vidas_utiles.get(categoria, (30, 365))
    return np.random.randint(*rango)


def asignar_alergenos(categoria, nombre):
    """Asigna alérgenos según categoría y nombre de producto."""
    alergenos = []
    
    # Reglas por categoría
    if categoria == 'Lácteos':
        alergenos.append('lactosa')
    
    if categoria == 'Panadería':
        if 'integral' in nombre.lower() or 'pan' in nombre.lower() or 'tortilla de harina' in nombre.lower():
            alergenos.append('gluten')
    
    if 'huevo' in nombre.lower():
        alergenos.append('huevo')
    
    if 'soja' in nombre.lower() or 'soya' in nombre.lower():
        alergenos.append('soja')
    
    if 'cacahuate' in nombre.lower() or 'nuez' in nombre.lower():
        alergenos.append('nuez')
    
    # Casos especiales
    if nombre in ['Atún en agua', 'Atún en aceite', 'Sardinas']:
        alergenos.append('mariscos')
    
    return ','.join(alergenos) if alergenos else ''


# Ejecutar generación
if __name__ == '__main__':
    print("Generando catálogo de 300 productos...")
    
    catalogo = generar_catalogo_productos(n_productos=300, seed=42)
    
    # Guardar a CSV
    catalogo.to_csv('../data/catalogo_productos.csv', index=False, encoding='utf-8')
    
    print(f"✅ Catálogo generado: {len(catalogo)} productos")
    print(f"\nPrimeros 5 productos:")
    print(catalogo.head())
    
    print(f"\nEstadísticas:")
    print(f"- Categorías: {catalogo['categoria'].nunique()}")
    print(f"- Precio promedio genérica: ${catalogo['precio_generica'].mean():.2f} MXN")
    print(f"- Precio promedio premium: ${catalogo['precio_premium'].mean():.2f} MXN")
    print(f"- Productos con alérgenos: {(catalogo['alergenos'] != '').sum()}")
    
    print(f"\nDistribución por categoría:")
    print(catalogo['categoria'].value_counts())