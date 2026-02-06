"""
Módulo de utilidades - Funciones auxiliares.

Este paquete contiene configuraciones de logging y otras
utilidades compartidas.
"""

from .logging_config import setup_logging, get_logger

__all__ = ['setup_logging', 'get_logger']
