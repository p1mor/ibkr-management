"""
Módulo de configuración para el sistema IBKR.

Este paquete contiene toda la configuración necesaria para conectar
y operar con Interactive Brokers Gateway.
"""

from .settings import Settings
from .contracts import ContractBuilder

__all__ = ['Settings', 'ContractBuilder']
