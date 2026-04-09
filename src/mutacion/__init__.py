"""
Módulo de operadores de mutación para el Algoritmo Genético.

Tipos de mutación disponibles:
- Cambio de producto: Reemplaza un producto por otro
- Cambio de cantidad: Ajusta la cantidad de un producto
- Cambio de marca: Cambia entre genérica/media/premium
- Cambio de supermercado: Cambia el supermercado de compra

La mutación es clave para:
- Mantener diversidad genética
- Evitar convergencia prematura
- Explorar nuevas soluciones
"""

from .mutacion_cambio_producto import mutar_cambio_producto
from .mutacion_cambio_cantidad import mutar_cambio_cantidad
from .mutacion_cambio_marca import mutar_cambio_marca
from .mutacion_cambio_supermercado import mutar_cambio_supermercado
from .mutacion_combinada import aplicar_mutacion, aplicar_mutacion_poblacion, calcular_estadisticas_mutacion

__all__ = [
    'mutar_cambio_producto',
    'mutar_cambio_cantidad',
    'mutar_cambio_marca',
    'mutar_cambio_supermercado',
    'aplicar_mutacion',
    'aplicar_mutacion_poblacion',
    'calcular_estadisticas_mutacion'
]