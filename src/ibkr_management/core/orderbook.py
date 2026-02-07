"""
orderbook.py - Gestión del Order Book (libro de órdenes)

Este módulo mantiene una representación en memoria del order book
con actualizaciones incrementales desde IB Gateway.

EDUCATIVO: El order book muestra todos los precios disponibles para
comprar (bid) y vender (ask), con sus cantidades. Es fundamental
para entender la microestructura del mercado.
"""

import json
from typing import Dict, List, Tuple, Optional
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class OrderBook:
    """
    Representa el order book (profundidad de mercado) en tiempo real.
    
    Estructura:
        - bids: {position: {'price': float, 'size': float}}
        - asks: {position: {'price': float, 'size': float}}
    
    Las posiciones son índices (0 = mejor precio, 1 = segundo mejor, etc.)
    """
    
    def __init__(self, max_depth: int = 10):
        """
        Inicializa un order book vacío.
        
        Args:
            max_depth: Profundidad máxima a mantener (niveles por lado)
        """
        self.bids: Dict[int, Dict[str, float]] = {}
        self.asks: Dict[int, Dict[str, float]] = {}
        self.max_depth = max_depth
        self.update_count = 0
        logger.debug(f"OrderBook inicializado con profundidad máxima: {max_depth}")
    
    def update(self, position: int, operation: int, side: int, price: float, size: float):
        """
        Actualiza el order book con un evento de market depth.
        
        Args:
            position: Posición en el book (0=mejor, 1=segundo, etc.)
            operation: Tipo de operación
                - 0: Insert
                - 1: Update
                - 2: Delete
            side: Lado del book
                - 0: Ask (venta)
                - 1: Bid (compra)
            price: Precio del nivel
            size: Cantidad disponible
            
        EDUCATIVO: Las operaciones reflejan cómo cambia el book:
            - Insert: Nueva orden entra al book
            - Update: Cantidad de nivel existente cambia
            - Delete: Nivel se elimina (todas las órdenes canceladas/ejecutadas)
        """
        self.update_count += 1
        
        # Validar precio positivo
        if price <= 0:
            logger.warning(f"Precio inválido recibido: {price} (ignorado)")
            return
        
        # Seleccionar lado del book
        book_side = self.bids if side == 1 else self.asks
        side_name = 'bid' if side == 1 else 'ask'
        
        # Aplicar operación
        if operation == 2:  # Delete
            if position in book_side:
                del book_side[position]
                logger.debug(f"Eliminado {side_name} posición {position}")
        else:  # Insert (0) o Update (1)
            book_side[position] = {'price': float(price), 'size': float(size)}
            op_name = 'Insertado' if operation == 0 else 'Actualizado'
            logger.debug(f"{op_name} {side_name} pos {position}: {price}@{size}")
        
        # Mantener solo max_depth niveles
        self._trim_depth(book_side)
    
    def _trim_depth(self, book_side: Dict):
        """Mantiene solo los niveles dentro de max_depth."""
        if len(book_side) > self.max_depth:
            # Ordenar por posición y mantener solo los primeros max_depth
            sorted_positions = sorted(book_side.keys())
            for pos in sorted_positions[self.max_depth:]:
                del book_side[pos]
    
    def get_snapshot(self, max_levels: Optional[int] = None) -> Tuple[List, List]:
        """
        Obtiene snapshot actual del order book ordenado.
        
        Args:
            max_levels: Máximo niveles a retornar (None = todos)
            
        Returns:
            Tupla (bids_sorted, asks_sorted) donde cada elemento es:
            [(position, {'price': float, 'size': float}), ...]
            
        Ejemplo:
            >>> bids, asks = orderbook.get_snapshot(5)
            >>> print(f"Mejor bid: {bids[0][1]['price']}@{bids[0][1]['size']}")
            >>> print(f"Mejor ask: {asks[0][1]['price']}@{asks[0][1]['size']}")
        """
        max_levels = max_levels or self.max_depth
        
        # Ordenar bids por precio descendente (mejor primero)
        bids_sorted = sorted(
            self.bids.items(),
            key=lambda x: x[1]['price'],
            reverse=True
        )[:max_levels]
        
        # Ordenar asks por precio ascendente (mejor primero)
        asks_sorted = sorted(
            self.asks.items(),
            key=lambda x: x[1]['price']
        )[:max_levels]
        
        return bids_sorted, asks_sorted
    
    def get_best_bid_ask(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Obtiene el mejor bid y ask.
        
        Returns:
            Tupla (best_bid_price, best_ask_price)
            Retorna (None, None) si el book está vacío
        """
        bids, asks = self.get_snapshot(1)
        
        best_bid = bids[0][1]['price'] if bids else None
        best_ask = asks[0][1]['price'] if asks else None
        
        return best_bid, best_ask
    
    def get_mid_price(self) -> Optional[float]:
        """
        Calcula el mid price (precio medio entre bid y ask).
        
        Returns:
            (best_bid + best_ask) / 2, o None si el book está vacío
            
        EDUCATIVO: El mid price es un estimador del "precio justo" del
        mercado, usado frecuentemente en estrategias y valoración.
        """
        best_bid, best_ask = self.get_best_bid_ask()
        
        if best_bid is not None and best_ask is not None:
            return (best_bid + best_ask) / 2.0
        
        return None
    
    def get_spread(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Calcula el spread (diferencia entre ask y bid).
        
        Returns:
            Tupla (spread_absolute, spread_bps)
            - spread_absolute: ask - bid
            - spread_bps: ((ask - bid) / bid) * 10000
            
        EDUCATIVO: El spread es el "costo" de entrar y salir inmediatamente
        del mercado. Spread estrecho = mercado líquido.
        """
        best_bid, best_ask = self.get_best_bid_ask()
        
        if best_bid is None or best_ask is None or best_bid <= 0:
            return None, None
        
        spread_abs = best_ask - best_bid
        spread_bps = (spread_abs / best_bid) * 10000
        
        return spread_abs, spread_bps
    
    def get_depth_quality_score(self) -> int:
        """
        Calcula un score de calidad del order book.
        
        Returns:
            Score 0-100 basado en profundidad y balance
            
        Cálculo:
            - 10 puntos por cada nivel (max 10 niveles = 100)
            - Penaliza si un lado tiene mucho menos liquidez
        """
        bids, asks = self.get_snapshot()
        
        # Base score: 10 puntos por nivel (mínimo de ambos lados)
        min_levels = min(len(bids), len(asks))
        base_score = min_levels * 10
        
        # Penalizar desbalance extremo
        if len(bids) > 0 and len(asks) > 0:
            imbalance = abs(len(bids) - len(asks)) / max(len(bids), len(asks))
            penalty = int(imbalance * 20)  # Hasta -20 puntos
            base_score -= penalty
        
        return max(0, min(100, base_score))
    
    def to_json(self, max_levels: Optional[int] = None) -> Tuple[str, str]:
        """
        Serializa el order book a JSON.
        
        Args:
            max_levels: Máximo niveles a incluir
            
        Returns:
            Tupla (bids_json, asks_json)
            
        Formato JSON:
            [{"price": "5875.00", "qty": "25"}, ...]
        """
        bids, asks = self.get_snapshot(max_levels)
        
        bids_list = [
            {'price': str(level[1]['price']), 'qty': str(level[1]['size'])}
            for level in bids
        ]
        
        asks_list = [
            {'price': str(level[1]['price']), 'qty': str(level[1]['size'])}
            for level in asks
        ]
        
        return json.dumps(bids_list), json.dumps(asks_list)
    
    def is_healthy(self) -> bool:
        """
        Verifica si el order book está en estado saludable.
        
        Returns:
            True si tiene al menos 1 nivel en cada lado y spread positivo
        """
        bids, asks = self.get_snapshot(1)
        
        if not bids or not asks:
            return False
        
        best_bid = bids[0][1]['price']
        best_ask = asks[0][1]['price']
        
        return best_bid < best_ask
    
    def clear(self):
        """Limpia el order book completamente."""
        self.bids.clear()
        self.asks.clear()
        logger.info("OrderBook limpiado")
    
    def __str__(self) -> str:
        """Representación legible del order book."""
        bids, asks = self.get_snapshot(5)
        mid = self.get_mid_price()
        spread_abs, spread_bps = self.get_spread()
        
        lines = ["=" * 50]
        lines.append("ORDER BOOK")
        lines.append("=" * 50)
        
        # Asks (invertido para mostrar mejor primero arriba)
        lines.append("ASKS (venta):")
        for pos, level in reversed(asks):
            lines.append(f"  {level['price']:>10.2f} @ {level['size']:>8.1f}")
        
        # Mid price y spread
        if mid:
            lines.append("-" * 50)
            lines.append(f"  MID: {mid:.2f}  |  SPREAD: {spread_bps:.2f} bps")
            lines.append("-" * 50)
        
        # Bids
        lines.append("BIDS (compra):")
        for pos, level in bids:
            lines.append(f"  {level['price']:>10.2f} @ {level['size']:>8.1f}")
        
        lines.append("=" * 50)
        lines.append(f"Updates: {self.update_count} | Quality: {self.get_depth_quality_score()}/100")
        
        return "\n".join(lines)
