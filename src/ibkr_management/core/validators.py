"""
validators.py - Validaciones de calidad de datos

Este módulo implementa múltiples capas de validación para asegurar
la integridad y calidad de los datos capturados.

EDUCATIVO: En trading, datos incorrectos pueden llevar a decisiones
desastrosas. Este sistema valida cada dato antes de almacenarlo.
"""

from typing import Tuple, Dict, Any
from dataclasses import dataclass
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """
    Resultado de las validaciones aplicadas a un dato.
    
    Attributes:
        v1: Validación 1 - Precio válido (> 0)
        v2: Validación 2 - Cantidad válida (> 0)
        v3: Validación 3 - Spread positivo (best_bid < best_ask)
        v4: Validación 4 - Order book tiene liquidez
        v5: Validación 5 - Spread dentro de umbrales razonables
        p1: Protocolo 1 - Timestamp válido
        final: Todas las validaciones pasan
        flags: Bitmask compacto de validaciones (int32)
    """
    v1: bool  # Price validation
    v2: bool  # Quantity validation
    v3: bool  # Spread validation
    v4: bool  # Depth validation
    v5: bool  # Spread threshold validation
    p1: bool  # Protocol validation
    final: bool  # All validations pass
    flags: int  # Bitmask
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para almacenamiento."""
        return {
            'validation_v1': self.v1,
            'validation_v2': self.v2,
            'validation_v3': self.v3,
            'validation_v4': self.v4,
            'validation_v5': self.v5,
            'validation_p1': self.p1,
            'validation_final': self.final,
            'validation_flags': self.flags,
        }
    
    def __str__(self) -> str:
        """Representación legible."""
        status = "✓ PASS" if self.final else "✗ FAIL"
        failed = []
        if not self.v1:
            failed.append("price")
        if not self.v2:
            failed.append("qty")
        if not self.v3:
            failed.append("spread_sign")
        if not self.v4:
            failed.append("depth")
        if not self.v5:
            failed.append("spread_threshold")
        if not self.p1:
            failed.append("timestamp")
        
        if failed:
            return f"{status} (failed: {', '.join(failed)})"
        return status


class DataValidator:
    """
    Validador de datos de mercado con múltiples capas de verificación.
    
    Implementa 7 validaciones:
    - v1: Precio debe ser positivo
    - v2: Cantidad debe ser positiva
    - v3: Bid debe ser menor que Ask (spread positivo)
    - v4: Order book debe tener liquidez mínima
    - v5: Spread debe estar dentro de umbrales razonables
    - p1: Timestamp debe ser válido
    - final: Todas las anteriores deben pasar
    """
    
    def __init__(self, max_spread_threshold: float = 0.1, min_depth_levels: int = 1):
        """
        Inicializa el validador con umbrales configurables.
        
        Args:
            max_spread_threshold: Máximo spread permitido (decimal, ej: 0.1 = 10%)
            min_depth_levels: Mínimo número de niveles en cada lado del book
        """
        self.max_spread_threshold = max_spread_threshold
        self.min_depth_levels = min_depth_levels
        logger.info(
            f"DataValidator inicializado: max_spread={max_spread_threshold*100:.2f}%, "
            f"min_depth={min_depth_levels}"
        )
    
    def validate_trade(
        self,
        price: float,
        quantity: float,
        event_time: int,
        bids: list,
        asks: list
    ) -> ValidationResult:
        """
        Valida un trade individual con snapshot del order book.
        
        Args:
            price: Precio del trade
            quantity: Cantidad del trade
            event_time: Timestamp del evento (ms)
            bids: Lista de tuplas (position, {'price': float, 'size': float})
            asks: Lista de tuplas (position, {'price': float, 'size': float})
            
        Returns:
            ValidationResult con resultado de todas las validaciones
            
        Ejemplo:
            >>> validator = DataValidator()
            >>> result = validator.validate_trade(
            ...     price=5875.25,
            ...     quantity=5,
            ...     event_time=1738876543210,
            ...     bids=[(0, {'price': 5875.00, 'size': 25})],
            ...     asks=[(0, {'price': 5875.25, 'size': 30})]
            ... )
            >>> print(result)  # ✓ PASS
        """
        # V1: Precio válido
        v1 = price > 0
        
        # V2: Cantidad válida
        v2 = quantity > 0
        
        # Extraer best bid/ask
        best_bid = bids[0][1]['price'] if bids else 0
        best_ask = asks[0][1]['price'] if asks else float('inf')
        
        # V3: Spread positivo (bid < ask)
        v3 = best_bid < best_ask if (bids and asks) else False
        
        # V4: Liquidez mínima en order book
        v4 = len(bids) >= self.min_depth_levels and len(asks) >= self.min_depth_levels
        
        # V5: Spread dentro de umbrales razonables
        if best_bid > 0 and best_ask < float('inf'):
            spread = (best_ask - best_bid) / best_bid
            v5 = 0 < spread < self.max_spread_threshold
        else:
            v5 = False
        
        # P1: Timestamp válido
        p1 = event_time > 0
        
        # Final: Todas las validaciones deben pasar
        final = v1 and v2 and v3 and v4 and v5 and p1
        
        # Flags: Bitmask compacto
        flags = (
            (int(v1) << 0) |
            (int(v2) << 1) |
            (int(v3) << 2) |
            (int(v4) << 3) |
            (int(v5) << 4) |
            (int(p1) << 5)
        )
        
        result = ValidationResult(
            v1=v1, v2=v2, v3=v3, v4=v4, v5=v5, p1=p1,
            final=final, flags=flags
        )
        
        # Log si falla
        if not final:
            logger.debug(f"Validación fallida: {result}")
        
        return result
    
    def validate_depth_update(
        self,
        mid_price: float,
        bids: list,
        asks: list
    ) -> ValidationResult:
        """
        Valida una actualización del order book.
        
        Args:
            mid_price: Precio medio ((bid+ask)/2)
            bids: Lista de niveles bid
            asks: Lista de niveles ask
            
        Returns:
            ValidationResult con resultado de validaciones
            
        Nota:
            Para depth updates, v2 siempre es True (no hay quantity específica)
        """
        # V1: Mid price válido
        v1 = mid_price > 0
        
        # V2: No aplica para depth, siempre True
        v2 = True
        
        # Extraer best bid/ask
        best_bid = bids[0][1]['price'] if bids else 0
        best_ask = asks[0][1]['price'] if asks else float('inf')
        
        # V3: Spread positivo
        v3 = best_bid < best_ask if (bids and asks) else False
        
        # V4: Liquidez mínima
        v4 = len(bids) >= self.min_depth_levels and len(asks) >= self.min_depth_levels
        
        # V5: Spread razonable
        if best_bid > 0 and best_ask < float('inf'):
            spread = (best_ask - best_bid) / best_bid
            v5 = 0 < spread < self.max_spread_threshold
        else:
            v5 = False
        
        # P1: Siempre True para depth (usamos tiempo local)
        p1 = True
        
        # Final
        final = v1 and v3 and v4 and v5
        
        # Flags
        flags = (
            (int(v1) << 0) |
            (int(v2) << 1) |
            (int(v3) << 2) |
            (int(v4) << 3) |
            (int(v5) << 4) |
            (int(p1) << 5)
        )
        
        result = ValidationResult(
            v1=v1, v2=v2, v3=v3, v4=v4, v5=v5, p1=p1,
            final=final, flags=flags
        )
        
        if not final:
            logger.debug(f"Validación depth fallida: {result}")
        
        return result
    
    @staticmethod
    def parse_flags(flags: int) -> Dict[str, bool]:
        """
        Parsea el bitmask de flags a diccionario legible.
        
        Args:
            flags: Bitmask de validaciones
            
        Returns:
            Dict con cada validación expandida
            
        Ejemplo:
            >>> flags = 0b111111  # Todas las validaciones pasan
            >>> result = DataValidator.parse_flags(flags)
            >>> print(result)
            # {'v1': True, 'v2': True, 'v3': True, 'v4': True, 'v5': True, 'p1': True}
        """
        return {
            'v1': bool(flags & (1 << 0)),
            'v2': bool(flags & (1 << 1)),
            'v3': bool(flags & (1 << 2)),
            'v4': bool(flags & (1 << 3)),
            'v5': bool(flags & (1 << 4)),
            'p1': bool(flags & (1 << 5)),
        }
