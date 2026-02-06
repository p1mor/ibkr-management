"""
Módulo de almacenamiento - Persistencia de datos.

Este paquete gestiona la escritura de datos a archivos Parquet
con buffering, compresión y esquemas estrictos.
"""

from .parquet_writer import ParquetWriter

__all__ = ['ParquetWriter']
