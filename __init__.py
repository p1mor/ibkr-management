"""
IBKR Management - Sistema de Captura de Datos Ultra-Alta Frecuencia

Framework profesional para capturar datos de mercado desde Interactive Brokers
con arquitectura modular, validaciones robustas y almacenamiento eficiente.

Uso rápido:
    from config import Settings, ContractBuilder
    from core import OrderBook, DataValidator
    from storage import ParquetWriter
    from utils import setup_logging, get_logger

Ejemplos:
    # Configuración
    Settings.print_config()
    
    # Logger
    logger = setup_logging()
    logger.info("Sistema iniciado")
    
    # Contrato
    contract = ContractBuilder.create_future_contract()
    
    # Order Book
    ob = OrderBook()
    ob.update(0, 0, 1, 5875.00, 25)
    
    # Validador
    validator = DataValidator()
    result = validator.validate_trade(5875.25, 5, 1738876543210, bids, asks)
    
    # Almacenamiento
    with ParquetWriter() as writer:
        writer.add_record(record_dict)

Documentación:
    README.md - Documentación canónica del proyecto
    START_HERE.md - Onboarding rápido

Author: Quant TechPulse
Version: 1.0.0
License: Educational Use
"""

__version__ = '1.0.0'
__author__ = 'Quant TechPulse'

# Imports convenientes
from .config import Settings, ContractBuilder
from .utils import setup_logging, get_logger

__all__ = [
    'Settings',
    'ContractBuilder',
    'setup_logging',
    'get_logger',
]
