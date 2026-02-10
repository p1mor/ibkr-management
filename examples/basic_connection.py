"""
basic_connection.py - Ejemplo básico de conexión a IB Gateway

Este script demuestra cómo conectarse a Interactive Brokers Gateway,
validar un contrato y recibir tus primeros ticks de mercado.

EDUCATIVO: Empieza aquí para entender el flujo básico de conexión.
Este ejemplo valida contrato, captura ticks/depth y persiste en Parquet.
"""

from pathlib import Path
import time
import sys
from ibapi.client import EClient
from ibapi.wrapper import EWrapper

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ibkr_management.config import ContractBuilder, Settings
from ibkr_management.core import OrderBook
from ibkr_management.storage import ParquetWriter
from ibkr_management.utils import get_logger, setup_logging

# Configurar logging
setup_logging()
logger = get_logger(__name__)


class SimpleIBKRApp(EWrapper, EClient):
    """
    Aplicación simple para demostrar conexión básica a IBKR.
    
    Hereda de:
        - EWrapper: Recibe callbacks del API
        - EClient: Envía requests al API
    """
    
    def __init__(self):
        EClient.__init__(self, self)
        self.contract_validated = False
        self.tick_count = 0
        self.orderbook = OrderBook(max_depth=10)
        self.writer = ParquetWriter()
        logger.info("SimpleIBKRApp inicializada")
    
    # ========================================================================
    # CALLBACKS DE CONEXIÓN
    # ========================================================================
    
    def nextValidId(self, orderId: int):
        """
        Llamado cuando la conexión se establece exitosamente.
        
        Este es el punto de entrada principal - aquí iniciamos nuestras
        subscripciones a datos.
        """
        logger.info(f"✓ Conectado a IB Gateway! Next Order ID: {orderId}")
        logger.info(f"Solicitando validación de contrato: {Settings.IBKR_SYMBOL}")
        
        # Crear contrato usando nuestro builder
        contract = ContractBuilder.create_future_contract()
        
        # Solicitar detalles del contrato (validación)
        self.reqContractDetails(999, contract)
    
    def error(self, reqId: int, errorCode: int, errorString: str, advancedOrderRejectJson: str = ""):
        """Maneja errores y mensajes del sistema."""
        # Códigos 2100-2110 son informativos, no errores reales
        if 2100 <= errorCode < 2110:
            logger.info(f"[Info {errorCode}] {errorString}")
        else:
            logger.error(f"[Error {errorCode}] ReqID:{reqId} - {errorString}")
    
    def connectionClosed(self):
        """Llamado cuando la conexión se pierde."""
        logger.warning("Conexión cerrada por IB Gateway")
    
    # ========================================================================
    # CALLBACKS DE VALIDACIÓN DE CONTRATO
    # ========================================================================
    
    def contractDetails(self, reqId: int, contractDetails):
        """
        Recibe detalles del contrato solicitado.
        
        Si llegamos aquí, el contrato es válido y podemos subscribirnos a datos.
        """
        contract = contractDetails.contract
        logger.info("=" * 70)
        logger.info("✓ CONTRATO VALIDADO")
        logger.info("=" * 70)
        logger.info(f"  Símbolo:       {contract.symbol}")
        logger.info(f"  Tipo:          {contract.secType}")
        logger.info(f"  Exchange:      {contract.exchange}")
        logger.info(f"  Moneda:        {contract.currency}")
        logger.info(f"  Vencimiento:   {contract.lastTradeDateOrContractMonth}")
        logger.info(f"  Contract ID:   {contract.conId}")
        logger.info("=" * 70)
        
        self.contract_validated = True
        self.validated_contract = contract
    
    def contractDetailsEnd(self, reqId: int):
        """
        Llamado cuando terminan de llegar los detalles del contrato.
        
        Aquí iniciamos la subscripción a datos de mercado.
        """
        if self.contract_validated:
            logger.info("\n[DATA] Iniciando subscripción a datos de mercado...")
            logger.info("(Presiona Ctrl+C para detener)\n")
            
            # Subscribirse a tick-by-tick (trades individuales)
            # Parámetros:
            #   19001 = Request ID único
            #   contract = Contrato validado
            #   "AllLast" = Tipo de ticks (todos los trades)
            #   0 = Number of ticks (0 = streaming continuo)
            #   False = ignoreSize
            self.reqTickByTickData(
                19001,
                self.validated_contract,
                "AllLast",
                0,
                False
            )
            
            # Subscribirse a market depth (order book)
            # Parámetros:
            #   19002 = Request ID único
            #   contract = Contrato validado
            #   10 = Número de niveles de profundidad
            #   True = isSmartDepth
            #   [] = mktDepthOptions
            self.reqMktDepth(
                19002,
                self.validated_contract,
                10,
                True,
                []
            )
            
            logger.info("✓ Subscripción activa - esperando datos...")
            logger.info("Nota: en fin de semana/fuera de horario puede no haber ticks aunque la conexión esté OK.")
        else:
            logger.error("[ERROR] No se pudo validar el contrato")
            self.disconnect()
    
    # ========================================================================
    # CALLBACKS DE DATOS DE MERCADO
    # ========================================================================
    
    def tickByTickAllLast(
        self,
        reqId: int,
        tickType: int,
        event_time: int,
        price: float,
        size: float,
        tickAttribLast,
        exchange: str,
        specialConditions: str
    ):
        """
        Recibe cada trade individual ejecutado en el mercado.
        
        ¡Este es el flujo de datos principal!
        """
        self.tick_count += 1
        
        # Convertir timestamp Unix a legible
        from datetime import datetime
        time_str = datetime.fromtimestamp(event_time).strftime('%H:%M:%S')
        
        # Formatear y mostrar
        logger.info(
            f"[TARGET] Tick #{self.tick_count:>6d} | "
            f"{time_str} | "
            f"Precio: {price:>10.2f} | "
            f"Cantidad: {size:>5.0f} | "
            f"Exchange: {exchange}"
        )
        
        # Crear registro para almacenamiento
        record = {
            'symbol': Settings.IBKR_SYMBOL,
            'trade_id': self.tick_count,
            'atomic_type': 'trade',
            'event_time_server_ms': event_time * 1000,  # Convertir a ms
            'trade_time_ms': event_time * 1000,
            'received_at_ingest_ns': time.time_ns(),
            'trade_price': str(price),
            'trade_qty': str(size),
            'buyer_is_maker': False,  # No disponible en tick-by-tick
            'depth_last_update_id': 0,
            'bids_json': '[]',  # No disponible
            'asks_json': '[]',
            'best_bid_price': '0',
            'best_bid_qty': '0',
            'best_ask_price': '0',
            'best_ask_qty': '0',
            'spread_bps': '0',
            'depth_sync_quality': 0,
            'raw_json': f'{{"reqId": {reqId}, "tickType": {tickType}, "exchange": "{exchange}"}}',
            'validation_v1': True,
            'validation_v2': True,
            'validation_v3': True,
            'validation_v4': True,
            'validation_v5': True,
            'validation_p1': True,
            'validation_final': True,
            'validation_flags': 63,
        }
        
        # Guardar en Parquet
        self.writer.add_record(record)
        
        # Cada 100 ticks, mostrar estadística
        if self.tick_count % 100 == 0:
            logger.info("=" * 70)
            logger.info(f"[OK] {self.tick_count} ticks recibidos exitosamente")
            logger.info("=" * 70)
    
    def updateMktDepth(
        self,
        reqId: int,
        position: int,
        operation: int,
        side: int,
        price: float,
        size: float
    ):
        """
        Recibe actualizaciones del order book (profundidad de mercado).
        
        Parameters:
            reqId: Request ID
            position: Posición en el book (0=mejor precio)
            operation: 0=insert, 1=update, 2=delete
            side: 0=ask (venta), 1=bid (compra)
            price: Precio del nivel
            size: Cantidad en ese precio
        """
        # Actualizar order book
        self.orderbook.update(position, operation, side, price, size)
        
        # Mostrar order book cada 10 actualizaciones
        if (position + 1) % 10 == 0:
            self._display_orderbook()
    
    def _display_orderbook(self):
        """
        Muestra el order book actual con 10 niveles de profundidad.
        """
        logger.info("\n" + "=" * 80)
        logger.info("ORDER BOOK - PROFUNDIDAD DE MERCADO (10 NIVELES)")
        logger.info("=" * 80)
        
        # Obtener bids y asks
        bids = self.orderbook.bids
        asks = self.orderbook.asks
        
        # Mostrar asks (venta) - del mejor al peor
        logger.info("ASKS (VENTA):")
        for pos in range(10):
            if pos in asks:
                level = asks[pos]
                logger.info(f"  Nivel {pos}: Precio {level['price']:.2f} | Cantidad {level['size']:.0f}")
            else:
                logger.info(f"  Nivel {pos}: -- vacío --")
        
        # Línea separadora con mid price
        mid = self.orderbook.get_mid_price()
        spread = self.orderbook.get_spread()[0] if self.orderbook.get_spread()[0] else 0
        logger.info("-" * 80)
        logger.info(f"MID PRICE: {mid:.2f} | SPREAD: {spread:.2f} puntos")
        logger.info("-" * 80)
        
        # Mostrar bids (compra) - del mejor al peor
        logger.info("BIDS (COMPRA):")
        for pos in range(10):
            if pos in bids:
                level = bids[pos]
                logger.info(f"  Nivel {pos}: Precio {level['price']:.2f} | Cantidad {level['size']:.0f}")
            else:
                logger.info(f"  Nivel {pos}: -- vacío --")
        
        logger.info("=" * 80)
        logger.info(f"Updates totales: {self.orderbook.update_count} | Quality: {self.orderbook.get_depth_quality_score()}/100")
        logger.info("=" * 80)


def main():
    """Función principal."""
    print("\n" + "=" * 70)
    print("EJEMPLO BÁSICO: Conexión a IB Gateway")
    print("=" * 70)
    
    # Mostrar configuración
    print(f"\nConexión:")
    print(f"  Host:     {Settings.IBKR_HOST}")
    print(f"  Puerto:   {Settings.IBKR_PORT}")  # Paper=4002, Live=4001 (IB Gateway por defecto)
    print(f"  ClientID: {Settings.IBKR_CLIENT_ID}")
    print(f"\nContrato:")
    print(f"  Símbolo:  {Settings.IBKR_SYMBOL}")
    print(f"  Exchange: {Settings.IBKR_EXCHANGE}")
    print(f"  Mes:      {Settings.IBKR_CONTRACT_MONTH}")
    
    # Validar configuración
    is_valid, errors = Settings.validate_config()
    if not is_valid:
        print("\n[WARNING] ERRORES EN CONFIGURACIÓN:")
        for error in errors:
            print(f"  - {error}")
        print("\nPor favor corrige estos errores en tu archivo .env")
        return
    
    print("\n✓ Configuración validada")
    print("\n" + "=" * 70)
    print("Conectando a IB Gateway...")
    print("=" * 70 + "\n")
    
    # Crear aplicación
    app = SimpleIBKRApp()
    
    try:
        # Conectar
        app.connect(
            Settings.IBKR_HOST,
            Settings.IBKR_PORT,
            Settings.IBKR_CLIENT_ID
        )
        
        # Verificar conexión
        if not app.isConnected():
            logger.error("✗ No se pudo conectar a IB Gateway")
            logger.error("\nVerifica que:")
            logger.error("  1. IB Gateway esté abierto y logueado")
            logger.error("  2. Puerto correcto (IB Gateway: 4002 paper, 4001 live)")
            logger.error("  3. API Settings estén habilitados en Gateway")
            return
        
        logger.info("✓ Socket conectado exitosamente")
        
        # Correr el event loop
        # Esto bloquea y procesa callbacks hasta Ctrl+C
        app.run()
        
    except KeyboardInterrupt:
        logger.info("\n\n" + "=" * 70)
        logger.info("Interrupción manual detectada (Ctrl+C)")
        logger.info("=" * 70)
        logger.info(f"Total de ticks recibidos: {app.tick_count}")
        logger.info("Desconectando...")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        
    finally:
        if app.isConnected():
            app.disconnect()
        app.writer.stop()  # Guardar datos restantes
        logger.info("✓ Desconectado correctamente")
        logger.info("\n¡Gracias por usar el sistema!")


if __name__ == "__main__":
    main()
