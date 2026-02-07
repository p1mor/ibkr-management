"""
connection.py - Conexión a Interactive Brokers Gateway

Este módulo maneja la conexión persistente a IB Gateway usando
el patrón EWrapper/EClient de la API oficial.

EDUCATIVO: La conexión a IBKR requiere mantener un socket TCP
persistente. Este módulo abstrae esa complejidad.
"""

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class IBKRConnection(EWrapper, EClient):
    """
    Conexión persistente a IB Gateway.
    
    Maneja reconexiones automáticas y estado de conexión.
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 4001, client_id: int = 1):
        EClient.__init__(self, self)
        self.host = host
        self.port = port
        self.client_id = client_id
        self.connected = False
        
    def connect_and_run(self):
        """Conecta y ejecuta el loop de eventos."""
        self.connect(self.host, self.port, self.client_id)
        if self.isConnected():
            self.connected = True
            logger.info(f"Conectado a {self.host}:{self.port}")
            self.run()
        else:
            logger.error("No se pudo conectar")
    
    def disconnect(self):
        """Desconecta del gateway."""
        if self.connected:
            super().disconnect()
            self.connected = False
            logger.info("Desconectado")
