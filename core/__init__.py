"""
Módulo core - Lógica principal del procesador de datos IBKR.

Este paquete contiene los componentes esenciales para conectar,
procesar y validar datos de Interactive Brokers.
"""

from .connection import IBKRConnection
from .data_processor import DataProcessor
from .orderbook import OrderBook
from .validators import DataValidator

__all__ = ['IBKRConnection', 'DataProcessor', 'OrderBook', 'DataValidator']
