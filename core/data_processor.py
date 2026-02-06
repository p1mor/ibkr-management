"""
data_processor.py - Procesador de datos en tiempo real

Este módulo coordina el flujo de datos desde IBKR hasta el almacenamiento,
aplicando validaciones y enriqueciendo con order book.

EDUCATIVO: El procesamiento de datos en tiempo real requiere buffering,
validación y sincronización entre múltiples fuentes de datos.
"""

from typing import Dict, Any
from .orderbook import OrderBook
from .validators import DataValidator
from storage.parquet_writer import ParquetWriter
from utils.logging_config import get_logger

logger = get_logger(__name__)


class DataProcessor:
    """
    Procesa y coordina datos de IBKR.
    
    Recibe ticks y depth updates, valida, enriquece y almacena.
    """
    
    def __init__(self, symbol: str = "ES"):
        self.symbol = symbol
        self.orderbook = OrderBook()
        self.validator = DataValidator()
        self.writer = ParquetWriter(symbol=symbol)
        
    def process_tick(self, tick_data: Dict[str, Any]):
        """Procesa un tick de precio."""
        # Validar
        result = self.validator.validate_tick(tick_data)
        if result.final:
            # Enriquecer con order book
            enriched = self._enrich_with_orderbook(tick_data)
            # Almacenar
            self.writer.write_tick(enriched)
        else:
            logger.warning(f"Tick inválido: {tick_data}")
    
    def process_depth(self, depth_data: Dict[str, Any]):
        """Procesa una actualización de profundidad."""
        # Actualizar order book
        self.orderbook.update(**depth_data)
        # Validar
        result = self.validator.validate_depth(self.orderbook)
        if result.final:
            # Almacenar snapshot
            snapshot = self.orderbook.to_dict()
            self.writer.write_depth(snapshot)
    
    def _enrich_with_orderbook(self, tick_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enriquece tick con datos del order book."""
        # Agregar mid price, spread, etc.
        mid = self.orderbook.get_mid_price()
        spread = self.orderbook.get_spread()
        return {
            **tick_data,
            'orderbook_mid': mid,
            'orderbook_spread': spread
        }

if __name__ == "__main__":
    # Demo básico
    processor = DataProcessor()
    print("DataProcessor creado (demo)")