"""
logging_config.py - Configuración centralizada de logging

Este módulo configura el sistema de logging del proyecto con
formato consistente, rotación de archivos y niveles configurables.

EDUCATIVO: El logging es crítico para debugging y auditoría en
sistemas de trading. Aquí configuramos logs detallados pero eficientes.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
from config.settings import Settings


def setup_logging(
    log_file: Optional[Path] = None,
    log_level: Optional[str] = None,
    console_output: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configura el sistema de logging con archivo rotativo y consola.
    
    Args:
        log_file: Ruta del archivo de log (usa Settings.LOG_FILE si None)
        log_level: Nivel de logging (usa Settings.LOG_LEVEL si None)
        console_output: Si True, también imprime a consola
        max_bytes: Tamaño máximo del archivo antes de rotar
        backup_count: Número de archivos de backup a mantener
        
    Returns:
        Logger configurado
        
    Ejemplo:
        >>> logger = setup_logging()
        >>> logger.info("Sistema iniciado")
        >>> logger.error("Error crítico", exc_info=True)
    """
    # Valores por defecto desde configuración
    log_file = log_file or Settings.LOG_FILE
    log_level = log_level or Settings.LOG_LEVEL
    
    # Convertir string a nivel de logging
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Crear logger raíz
    logger = logging.getLogger('ibkr_management')
    logger.setLevel(numeric_level)
    
    # Evitar duplicados si ya está configurado
    if logger.handlers:
        return logger
    
    # Formato detallado con milisegundos
    formatter = logging.Formatter(
        fmt='%(asctime)s.%(msecs)03d [%(levelname)-8s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler de archivo con rotación
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler de consola
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        # Formato más simple para consola
        console_formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)-8s] %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Log inicial
    logger.info("=" * 70)
    logger.info("Sistema de logging inicializado")
    logger.info(f"Nivel de log: {log_level.upper()}")
    logger.info(f"Archivo de log: {log_file.absolute()}")
    logger.info("=" * 70)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger con un nombre específico.
    
    Args:
        name: Nombre del módulo o componente
        
    Returns:
        Logger configurado para ese módulo
        
    Ejemplo:
        >>> logger = get_logger(__name__)
        >>> logger.info("Mensaje desde mi módulo")
    """
    # Usar jerarquía de loggers
    full_name = f'ibkr_management.{name}' if not name.startswith('ibkr_management') else name
    return logging.getLogger(full_name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Adapter que agrega contexto adicional a los logs.
    
    Útil para agregar información de trading (símbolo, estrategia, etc.)
    a todos los mensajes de log automáticamente.
    
    Ejemplo:
        >>> base_logger = get_logger(__name__)
        >>> logger = LoggerAdapter(base_logger, {'symbol': 'ES', 'strategy': 'EMA'})
        >>> logger.info("Trade ejecutado")
        # Output: ... [ES] [EMA] Trade ejecutado
    """
    
    def process(self, msg, kwargs):
        """Agrega contexto al mensaje."""
        # Extraer información del extra dict
        symbol = self.extra.get('symbol', '')
        strategy = self.extra.get('strategy', '')
        
        # Construir prefijo
        prefix_parts = []
        if symbol:
            prefix_parts.append(f'[{symbol}]')
        if strategy:
            prefix_parts.append(f'[{strategy}]')
        
        prefix = ' '.join(prefix_parts)
        
        # Agregar prefijo al mensaje
        if prefix:
            msg = f'{prefix} {msg}'
        
        return msg, kwargs


def create_trade_logger(symbol: str, strategy: Optional[str] = None) -> LoggerAdapter:
    """
    Crea un logger especializado para trading con contexto automático.
    
    Args:
        symbol: Símbolo del instrumento
        strategy: Nombre de la estrategia (opcional)
        
    Returns:
        LoggerAdapter con contexto configurado
        
    Ejemplo:
        >>> logger = create_trade_logger('ES', 'EMA-OBI')
        >>> logger.info("Señal de compra detectada")
        # Output: ... [ES] [EMA-OBI] Señal de compra detectada
    """
    base_logger = get_logger('trading')
    extra = {'symbol': symbol}
    if strategy:
        extra['strategy'] = strategy
    
    return LoggerAdapter(base_logger, extra)


# Inicializar logging automáticamente al importar
_root_logger = setup_logging()


if __name__ == "__main__":
    # Demo de uso
    print("\nDEMO: Sistema de Logging\n")
    
    # Logger básico
    logger = get_logger(__name__)
    
    logger.debug("Mensaje de debugging (puede no aparecer según nivel)")
    logger.info("Información general del sistema")
    logger.warning("Advertencia: Posible problema")
    logger.error("Error recuperable")
    logger.critical("Error crítico del sistema")
    
    # Logger con contexto
    print("\nLogger con contexto de trading:")
    trade_logger = create_trade_logger('ES', 'EMA-OBI')
    trade_logger.info("Conectado a IB Gateway")
    trade_logger.warning("Spread elevado detectado: 15 bps")
    trade_logger.info("Trade ejecutado: LONG 2 contratos @ 5875.25")
    
    print(f"\nLogs guardados en: {Settings.LOG_FILE.absolute()}")
