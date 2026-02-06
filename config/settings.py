"""
settings.py - Configuración centralizada del sistema

Este módulo gestiona todas las variables de configuración usando variables
de entorno, permitiendo portabilidad sin hardcodeos.

EDUCATIVO: Las variables de entorno permiten configurar el sistema sin
modificar código, facilitando el despliegue en diferentes máquinas.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()


class Settings:
    """
    Clase singleton que contiene toda la configuración del sistema.
    
    Uso:
        settings = Settings()
        host = settings.IBKR_HOST
        port = settings.IBKR_PORT
    """
    
    # ========================================================================
    # CONFIGURACIÓN DE CONEXIÓN IBKR
    # ========================================================================
    
    # Host del IB Gateway (normalmente localhost)
    IBKR_HOST: str = os.getenv('IBKR_HOST', '127.0.0.1')
    
    # Puerto de conexión
    # 4001 = Paper Trading (cuenta demo/simulación)
    # 4002 = Live Trading (cuenta real)
    IBKR_PORT: int = int(os.getenv('IBKR_PORT', '4001'))
    
    # Client ID único para esta conexión
    # Cada aplicación conectada debe tener un ID diferente
    # Rango válido: 0-32 (0 es master client)
    IBKR_CLIENT_ID: int = int(os.getenv('IBKR_CLIENT_ID', '1'))
    
    # Timeout de conexión en segundos
    IBKR_TIMEOUT: int = int(os.getenv('IBKR_TIMEOUT', '30'))
    
    # ========================================================================
    # CONFIGURACIÓN DE CONTRATOS
    # ========================================================================
    
    # Símbolo del instrumento
    # ES = E-mini S&P 500
    # NQ = E-mini NASDAQ 100
    # YM = E-mini Dow Jones
    # RTY = E-mini Russell 2000
    IBKR_SYMBOL: str = os.getenv('IBKR_SYMBOL', 'ES')
    
    # Tipo de seguridad
    # FUT = Futuros
    # STK = Acciones
    # OPT = Opciones
    # FOP = Opciones sobre futuros
    IBKR_SEC_TYPE: str = os.getenv('IBKR_SEC_TYPE', 'FUT')
    
    # Exchange donde se negocia
    # CME = Chicago Mercantile Exchange
    # GLOBEX = Plataforma electrónica de CME
    IBKR_EXCHANGE: str = os.getenv('IBKR_EXCHANGE', 'CME')
    
    # Moneda del contrato
    IBKR_CURRENCY: str = os.getenv('IBKR_CURRENCY', 'USD')
    
    # Mes de vencimiento del contrato (formato YYYYMM)
    # IMPORTANTE: Actualizar mensualmente al rollover del contrato
    # ES vence trimestralmente: Mar(03), Jun(06), Sep(09), Dic(12)
    IBKR_CONTRACT_MONTH: str = os.getenv('IBKR_CONTRACT_MONTH', '202603')
    
    # ========================================================================
    # CONFIGURACIÓN DE DATOS
    # ========================================================================
    
    # Directorio base para almacenar datos
    DATA_OUTPUT_DIR: Path = Path(os.getenv('DATA_OUTPUT_DIR', './data'))
    
    # Crear directorio si no existe
    DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Intervalo de flush del buffer (segundos)
    # Cada cuánto tiempo se escriben los datos del buffer a disco
    BUFFER_FLUSH_INTERVAL: int = int(os.getenv('BUFFER_FLUSH_INTERVAL', '60'))
    
    # Tamaño máximo del buffer antes de forzar flush (número de registros)
    BUFFER_MAX_SIZE: int = int(os.getenv('BUFFER_MAX_SIZE', '10000'))
    
    # Profundidad del order book a capturar
    # Niveles de bid/ask (máximo 10 para la mayoría de contratos)
    MARKET_DEPTH_ROWS: int = int(os.getenv('MARKET_DEPTH_ROWS', '10'))
    
    # ========================================================================
    # CONFIGURACIÓN DE LOGGING
    # ========================================================================
    
    # Nivel de logging
    # DEBUG = Máximo detalle (desarrollo)
    # INFO = Información general (producción)
    # WARNING = Solo advertencias y errores
    # ERROR = Solo errores
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Archivo de log principal
    LOG_FILE: Path = Path(os.getenv('LOG_FILE', 'ib_gateway_audit.log'))
    
    # Formato de timestamp en logs
    LOG_TIMESTAMP_FORMAT: str = '%Y-%m-%d %H:%M:%S.%f'
    
    # ========================================================================
    # CONFIGURACIÓN DE RECONEXIÓN
    # ========================================================================
    
    # Intentos de reconexión antes de fallar
    MAX_RECONNECTION_ATTEMPTS: int = int(os.getenv('MAX_RECONNECTION_ATTEMPTS', '0'))  # 0 = infinito
    
    # Tiempo de espera entre intentos de reconexión (segundos)
    RECONNECTION_DELAY: int = int(os.getenv('RECONNECTION_DELAY', '10'))
    
    # ========================================================================
    # CONFIGURACIÓN DE VALIDACIÓN
    # ========================================================================
    
    # Spread máximo permitido para considerar datos válidos (porcentaje)
    # 0.1 = 10% spread máximo
    MAX_SPREAD_THRESHOLD: float = float(os.getenv('MAX_SPREAD_THRESHOLD', '0.1'))
    
    # Mínimo número de niveles en el order book para validación
    MIN_DEPTH_LEVELS: int = int(os.getenv('MIN_DEPTH_LEVELS', '1'))
    
    # ========================================================================
    # MÉTODOS AUXILIARES
    # ========================================================================
    
    @classmethod
    def get_parquet_filename(cls, symbol: Optional[str] = None) -> str:
        """
        Genera el nombre del archivo Parquet para el día actual.
        
        Args:
            symbol: Símbolo del instrumento (usa configuración por defecto si None)
            
        Returns:
            Nombre del archivo en formato: {symbol}_{exchange}_trades_{YYYYMMDD}.parquet
            
        Ejemplo:
            >>> Settings.get_parquet_filename()
            'es_cme_trades_20260206.parquet'
        """
        from datetime import datetime
        
        symbol = symbol or cls.IBKR_SYMBOL
        fecha = datetime.now().strftime('%Y%m%d')
        return f"{symbol}_{cls.IBKR_EXCHANGE}_trades_{fecha}.parquet".lower()
    
    @classmethod
    def get_parquet_path(cls, symbol: Optional[str] = None) -> Path:
        """
        Obtiene la ruta completa del archivo Parquet.
        
        Args:
            symbol: Símbolo del instrumento
            
        Returns:
            Path completo al archivo Parquet
        """
        filename = cls.get_parquet_filename(symbol)
        return cls.DATA_OUTPUT_DIR / filename
    
    @classmethod
    def validate_config(cls) -> tuple[bool, list[str]]:
        """
        Valida que la configuración sea correcta.
        
        Returns:
            Tupla (es_valida, lista_de_errores)
            
        Ejemplo:
            >>> is_valid, errors = Settings.validate_config()
            >>> if not is_valid:
            >>>     for error in errors:
            >>>         print(f"Error: {error}")
        """
        errors = []
        
        # Validar host
        if not cls.IBKR_HOST:
            errors.append("IBKR_HOST no puede estar vacío")
        
        # Validar puerto
        if cls.IBKR_PORT not in [4001, 4002]:
            errors.append(f"IBKR_PORT debe ser 4001 o 4002, recibido: {cls.IBKR_PORT}")
        
        # Validar client ID
        if not 0 <= cls.IBKR_CLIENT_ID <= 32:
            errors.append(f"IBKR_CLIENT_ID debe estar entre 0 y 32, recibido: {cls.IBKR_CLIENT_ID}")
        
        # Validar símbolo
        if not cls.IBKR_SYMBOL:
            errors.append("IBKR_SYMBOL no puede estar vacío")
        
        # Validar mes de contrato (formato YYYYMM)
        if len(cls.IBKR_CONTRACT_MONTH) != 6 or not cls.IBKR_CONTRACT_MONTH.isdigit():
            errors.append(f"IBKR_CONTRACT_MONTH debe tener formato YYYYMM, recibido: {cls.IBKR_CONTRACT_MONTH}")
        
        # Validar directorio de salida
        if not cls.DATA_OUTPUT_DIR.exists():
            try:
                cls.DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"No se pudo crear directorio de datos: {e}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def print_config(cls):
        """
        Imprime la configuración actual (útil para debugging).
        
        Ejemplo:
            >>> Settings.print_config()
        """
        print("=" * 70)
        print("CONFIGURACIÓN ACTUAL DEL SISTEMA")
        print("=" * 70)
        print(f"Conexión IBKR:")
        print(f"  Host:       {cls.IBKR_HOST}")
        print(f"  Puerto:     {cls.IBKR_PORT} ({'Paper' if cls.IBKR_PORT == 4002 else 'Live'})")
        print(f"  Client ID:  {cls.IBKR_CLIENT_ID}")
        print(f"  Timeout:    {cls.IBKR_TIMEOUT}s")
        print(f"\nContrato:")
        print(f"  Símbolo:    {cls.IBKR_SYMBOL}")
        print(f"  Tipo:       {cls.IBKR_SEC_TYPE}")
        print(f"  Exchange:   {cls.IBKR_EXCHANGE}")
        print(f"  Moneda:     {cls.IBKR_CURRENCY}")
        print(f"  Vencimiento: {cls.IBKR_CONTRACT_MONTH}")
        print(f"\nAlmacenamiento:")
        print(f"  Directorio: {cls.DATA_OUTPUT_DIR.absolute()}")
        print(f"  Flush cada: {cls.BUFFER_FLUSH_INTERVAL}s")
        print(f"  Max buffer: {cls.BUFFER_MAX_SIZE} registros")
        print(f"\nLogging:")
        print(f"  Nivel:      {cls.LOG_LEVEL}")
        print(f"  Archivo:    {cls.LOG_FILE}")
        print(f"\nReconexión:")
        print(f"  Max intentos: {'Infinito' if cls.MAX_RECONNECTION_ATTEMPTS == 0 else cls.MAX_RECONNECTION_ATTEMPTS}")
        print(f"  Delay:        {cls.RECONNECTION_DELAY}s")
        print("=" * 70)


# Instancia singleton
settings = Settings()


# Validar configuración al importar
if __name__ != "__main__":
    is_valid, errors = Settings.validate_config()
    if not is_valid:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("Advertencias en la configuración:")
        for error in errors:
            logger.warning(f"  - {error}")
