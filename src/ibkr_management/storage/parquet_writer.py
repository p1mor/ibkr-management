"""
parquet_writer.py - Escritura eficiente a archivos Parquet

Este módulo maneja la persistencia de datos con buffering,
compresión y esquemas estrictos para máxima eficiencia.

EDUCATIVO: Parquet es un formato columnar que permite consultas
rápidas y compresión eficiente - ideal para datos financieros.
"""

import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from ..config.settings import Settings
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class ParquetWriter:
    """
    Escritor de archivos Parquet con buffering y thread-safety.
    
    Características:
    - Buffer en memoria con flush automático
    - Thread-safe para múltiples productores
    - Esquema estricto con timestamps UTC
    - Compresión Snappy
    - Concatenación automática a archivos existentes
    """
    
    # Esquema fijo para consistencia
    SCHEMA = pa.schema([
        ('symbol', pa.string()),
        ('trade_id', pa.int64()),
        ('atomic_type', pa.string()),               # 'trade' | 'depth'
        ('event_time_server_ms', pa.timestamp('ms', tz='UTC')),
        ('trade_time_ms', pa.timestamp('ms', tz='UTC')),
        ('received_at_ingest_ns', pa.timestamp('ns', tz='UTC')),
        ('trade_price', pa.string()),               # Decimal preciso
        ('trade_qty', pa.string()),
        ('buyer_is_maker', pa.bool_()),
        ('depth_last_update_id', pa.int64()),
        ('bids_json', pa.string()),
        ('asks_json', pa.string()),
        ('best_bid_price', pa.string()),
        ('best_bid_qty', pa.string()),
        ('best_ask_price', pa.string()),
        ('best_ask_qty', pa.string()),
        ('spread_bps', pa.string()),
        ('depth_sync_quality', pa.int32()),
        ('raw_json', pa.string()),
        ('validation_v1', pa.bool_()),
        ('validation_v2', pa.bool_()),
        ('validation_v3', pa.bool_()),
        ('validation_v4', pa.bool_()),
        ('validation_v5', pa.bool_()),
        ('validation_p1', pa.bool_()),
        ('validation_final', pa.bool_()),
        ('validation_flags', pa.int32()),
    ])
    
    def __init__(
        self,
        symbol: Optional[str] = None,
        output_dir: Optional[Path] = None,
        flush_interval: Optional[int] = None,
        max_buffer_size: Optional[int] = None,
        auto_start: bool = True
    ):
        """
        Inicializa el escritor de Parquet.
        
        Args:
            symbol: Símbolo por defecto para el archivo Parquet (usa Settings si None)
            output_dir: Directorio de salida (usa Settings si None)
            flush_interval: Segundos entre flush automático (usa Settings si None)
            max_buffer_size: Máximo registros antes de flush forzado (usa Settings si None)
            auto_start: Iniciar thread de flush automático
        """
        self.symbol = symbol or Settings.IBKR_SYMBOL
        self.output_dir = Path(output_dir) if output_dir is not None else Settings.DATA_OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.flush_interval = flush_interval or Settings.BUFFER_FLUSH_INTERVAL
        self.max_buffer_size = max_buffer_size or Settings.BUFFER_MAX_SIZE

        if self.flush_interval <= 0:
            raise ValueError("flush_interval debe ser mayor que 0")
        if self.max_buffer_size <= 0:
            raise ValueError("max_buffer_size debe ser mayor que 0")
        
        # Buffer thread-safe
        self.buffer: List[Dict[str, Any]] = []
        self.buffer_lock = threading.Lock()
        
        # Thread de flush automático
        self.writer_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Métricas
        self.total_records_written = 0
        self.flush_count = 0
        
        logger.info(
            f"ParquetWriter inicializado: "
            f"symbol={self.symbol}, "
            f"dir={self.output_dir.resolve()}, "
            f"flush_interval={self.flush_interval}s, "
            f"max_buffer={self.max_buffer_size}"
        )
        
        # Auto-start
        if auto_start:
            self.start()
    
    def start(self):
        """Inicia el thread de flush automático."""
        if self.writer_thread and self.writer_thread.is_alive():
            logger.warning("Writer thread ya está corriendo")
            return
        
        self.stop_event.clear()
        self.writer_thread = threading.Thread(
            target=self._auto_flush_loop,
            daemon=True,
            name="ParquetWriter-AutoFlush"
        )
        self.writer_thread.start()
        logger.info("Thread de auto-flush iniciado")
    
    def stop(self, flush_remaining: bool = True):
        """
        Detiene el thread de flush automático.
        
        Args:
            flush_remaining: Si True, hace flush final del buffer
        """
        logger.info("Deteniendo ParquetWriter...")
        
        # Señalar al thread que pare
        self.stop_event.set()
        
        # Esperar que termine
        if self.writer_thread and self.writer_thread.is_alive():
            self.writer_thread.join(timeout=5)
        
        # Flush final
        if flush_remaining:
            self.flush()
        
        logger.info(f"ParquetWriter detenido. Total registros: {self.total_records_written}")
    
    def add_record(self, record: Dict[str, Any]):
        """
        Agrega un registro al buffer.
        
        Args:
            record: Diccionario con los campos del SCHEMA
            
        Nota:
            Thread-safe - puede ser llamado desde múltiples threads
        """
        with self.buffer_lock:
            self.buffer.append(record)
            buffer_size = len(self.buffer)
        
        # Flush si alcanzamos max_buffer_size
        if buffer_size >= self.max_buffer_size:
            logger.info(f"Buffer lleno ({buffer_size} registros) - flushing...")
            self.flush()
    
    def add_records_batch(self, records: List[Dict[str, Any]]):
        """
        Agrega múltiples registros al buffer de manera eficiente.
        
        Args:
            records: Lista de diccionarios con registros
        """
        with self.buffer_lock:
            self.buffer.extend(records)
            buffer_size = len(self.buffer)
        
        logger.debug(f"Batch agregado: {len(records)} registros. Buffer total: {buffer_size}")
        
        # Flush si necesario
        if buffer_size >= self.max_buffer_size:
            self.flush()
    
    def flush(self, symbol: Optional[str] = None) -> int:
        """
        Escribe el buffer a disco.
        
        Args:
            symbol: Símbolo para nombre de archivo (usa Settings si None)
            
        Returns:
            Número de registros escritos
            
        Nota:
            Thread-safe - puede ser llamado manualmente o desde auto-flush
        """
        with self.buffer_lock:
            if not self.buffer:
                logger.debug("Buffer vacío - nada que escribir")
                return 0
            
            # Copiar buffer y limpiarlo
            records_to_write = self.buffer.copy()
            self.buffer.clear()
        
        try:
            # Convertir a DataFrame
            df = pd.DataFrame(records_to_write)
            
            # Convertir timestamps
            df['event_time_server_ms'] = pd.to_datetime(
                df['event_time_server_ms'],
                unit='ms',
                utc=True
            )
            df['trade_time_ms'] = pd.to_datetime(
                df['trade_time_ms'],
                unit='ms',
                utc=True
            )
            df['received_at_ingest_ns'] = pd.to_datetime(
                df['received_at_ingest_ns'],
                unit='ns',
                utc=True
            )
            
            # Crear tabla con esquema
            table = pa.Table.from_pandas(df, schema=self.SCHEMA)
            
            # Determinar nombre de archivo
            symbol = symbol or self.symbol
            filename = Settings.get_parquet_filename(symbol)
            filepath = self.output_dir / filename
            
            # Concatenar con archivo existente si existe
            if filepath.exists():
                try:
                    existing = pq.read_table(filepath)
                    table = pa.concat_tables([existing, table])
                    logger.debug(f"Concatenando con archivo existente: {filepath}")
                except Exception as e:
                    logger.warning(f"No se pudo leer archivo existente: {e} - creando nuevo")
            
            # Escribir a disco
            pq.write_table(
                table,
                filepath,
                compression='snappy'
            )
            
            # Actualizar métricas
            self.flush_count += 1
            self.total_records_written += len(records_to_write)
            
            logger.info(
                f"✓ Flush #{self.flush_count}: "
                f"{len(records_to_write)} registros → {filepath.name} "
                f"(total: {self.total_records_written})"
            )
            
            return len(records_to_write)
            
        except Exception as e:
            logger.error(f"Error al escribir Parquet: {e}", exc_info=True)
            # Re-agregar al buffer para no perder datos
            with self.buffer_lock:
                self.buffer.extend(records_to_write)
            return 0
    
    def _auto_flush_loop(self):
        """Loop del thread de auto-flush."""
        logger.info(f"Auto-flush loop iniciado (cada {self.flush_interval}s)")
        
        while not self.stop_event.is_set():
            # Esperar intervalo o hasta stop_event
            if self.stop_event.wait(self.flush_interval):
                break  # stop_event fue seteado
            
            # Hacer flush
            try:
                self.flush()
            except Exception as e:
                logger.error(f"Error en auto-flush: {e}", exc_info=True)
        
        logger.info("Auto-flush loop terminado")
    
    def get_buffer_size(self) -> int:
        """Retorna el tamaño actual del buffer."""
        with self.buffer_lock:
            return len(self.buffer)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del escritor."""
        return {
            'total_records_written': self.total_records_written,
            'flush_count': self.flush_count,
            'current_buffer_size': self.get_buffer_size(),
            'output_dir': str(self.output_dir.absolute()),
        }
    
    def __enter__(self):
        """Context manager entry."""
        if not (self.writer_thread and self.writer_thread.is_alive()):
            self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop(flush_remaining=True)
