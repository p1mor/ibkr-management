"""
contracts.py - Constructor de contratos IBKR

Este módulo facilita la creación de contratos válidos para Interactive Brokers.

EDUCATIVO: Los contratos en IBKR deben estar perfectamente especificados
para que el sistema los reconozca. Este módulo abstrae esa complejidad.
"""

from ibapi.contract import Contract
from typing import Optional, Dict, Any
from .settings import Settings


class ContractBuilder:
    """
    Constructor de contratos IBKR con validación y defaults inteligentes.
    
    Esta clase simplifica la creación de contratos válidos, usando la
    configuración del sistema como defaults pero permitiendo overrides.
    """
    
    # Mapeo de símbolos a sus configuraciones típicas
    SYMBOL_DEFAULTS: Dict[str, Dict[str, Any]] = {
        'ES': {
            'name': 'E-mini S&P 500',
            'exchange': 'CME',
            'currency': 'USD',
            'multiplier': 50,
            'min_tick': 0.25,
            'description': 'Futuro del índice S&P 500'
        },
        'NQ': {
            'name': 'E-mini NASDAQ-100',
            'exchange': 'CME',
            'currency': 'USD',
            'multiplier': 20,
            'min_tick': 0.25,
            'description': 'Futuro del índice NASDAQ-100'
        },
        'YM': {
            'name': 'E-mini Dow Jones',
            'exchange': 'CBOT',
            'currency': 'USD',
            'multiplier': 5,
            'min_tick': 1.0,
            'description': 'Futuro del índice Dow Jones Industrial Average'
        },
        'RTY': {
            'name': 'E-mini Russell 2000',
            'exchange': 'CME',
            'currency': 'USD',
            'multiplier': 50,
            'min_tick': 0.10,
            'description': 'Futuro del índice Russell 2000'
        },
        'GC': {
            'name': 'Gold Futures',
            'exchange': 'COMEX',
            'currency': 'USD',
            'multiplier': 100,
            'min_tick': 0.10,
            'description': 'Futuro de Oro'
        },
        'CL': {
            'name': 'Crude Oil Futures',
            'exchange': 'NYMEX',
            'currency': 'USD',
            'multiplier': 1000,
            'min_tick': 0.01,
            'description': 'Futuro de Petróleo Crudo WTI'
        },
        '6E': {
            'name': 'Euro FX Futures',
            'exchange': 'CME',
            'currency': 'USD',
            'multiplier': 125000,
            'min_tick': 0.00005,
            'description': 'Futuro de Euro vs Dólar'
        },
    }
    
    @classmethod
    def create_future_contract(
        cls,
        symbol: Optional[str] = None,
        exchange: Optional[str] = None,
        currency: Optional[str] = None,
        contract_month: Optional[str] = None
    ) -> Contract:
        """
        Crea un contrato de futuros usando configuración por defecto o custom.
        
        Args:
            symbol: Símbolo del futuro (ej: 'ES', 'NQ'). Si None, usa Settings.IBKR_SYMBOL
            exchange: Exchange (ej: 'CME'). Si None, usa Settings.IBKR_EXCHANGE
            currency: Moneda (ej: 'USD'). Si None, usa Settings.IBKR_CURRENCY
            contract_month: Mes de vencimiento YYYYMM. Si None, usa Settings.IBKR_CONTRACT_MONTH
            
        Returns:
            Objeto Contract de ibapi configurado
            
        Ejemplo:
            >>> # Usar configuración por defecto
            >>> contract = ContractBuilder.create_future_contract()
            
            >>> # Override de símbolo
            >>> contract = ContractBuilder.create_future_contract(symbol='NQ')
            
            >>> # Custom completo
            >>> contract = ContractBuilder.create_future_contract(
            ...     symbol='ES',
            ...     exchange='CME',
            ...     currency='USD',
            ...     contract_month='202603'
            ... )
        """
        # Usar valores de configuración como defaults
        symbol = symbol or Settings.IBKR_SYMBOL
        exchange = exchange or Settings.IBKR_EXCHANGE
        currency = currency or Settings.IBKR_CURRENCY
        contract_month = contract_month or Settings.IBKR_CONTRACT_MONTH
        
        # Crear contrato
        contract = Contract()
        contract.symbol = symbol
        contract.secType = 'FUT'
        contract.exchange = exchange
        contract.currency = currency
        contract.lastTradeDateOrContractMonth = contract_month
        
        return contract
    
    @classmethod
    def create_stock_contract(
        cls,
        symbol: str,
        exchange: str = 'SMART',
        currency: str = 'USD'
    ) -> Contract:
        """
        Crea un contrato de acciones.
        
        Args:
            symbol: Ticker de la acción (ej: 'AAPL', 'TSLA')
            exchange: Exchange ('SMART' para routing automático)
            currency: Moneda (normalmente 'USD')
            
        Returns:
            Objeto Contract de ibapi configurado
            
        Ejemplo:
            >>> contract = ContractBuilder.create_stock_contract('AAPL')
        """
        contract = Contract()
        contract.symbol = symbol
        contract.secType = 'STK'
        contract.exchange = exchange
        contract.currency = currency
        
        return contract
    
    @classmethod
    def create_forex_contract(
        cls,
        symbol: str,
        exchange: str = 'IDEALPRO'
    ) -> Contract:
        """
        Crea un contrato de Forex (IDEALPRO).
        
        Args:
            symbol: Par de divisas (ej: 'EURUSD', 'GBPUSD')
            exchange: Exchange (IDEALPRO para forex institucional)
            
        Returns:
            Objeto Contract de ibapi configurado
            
        Ejemplo:
            >>> contract = ContractBuilder.create_forex_contract('EURUSD')
        """
        # Separar symbol en base y quote currency
        # EURUSD -> EUR = base, USD = quote
        if len(symbol) != 6:
            raise ValueError(f"Símbolo forex debe tener 6 caracteres (ej: EURUSD), recibido: {symbol}")
        
        base_currency = symbol[:3]
        quote_currency = symbol[3:]
        
        contract = Contract()
        contract.symbol = base_currency
        contract.secType = 'CASH'
        contract.exchange = exchange
        contract.currency = quote_currency
        
        return contract
    
    @classmethod
    def get_contract_info(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información pre-configurada de un símbolo conocido.
        
        Args:
            symbol: Símbolo (ej: 'ES', 'NQ')
            
        Returns:
            Dict con información del contrato o None si no existe
            
        Ejemplo:
            >>> info = ContractBuilder.get_contract_info('ES')
            >>> print(info['name'])  # 'E-mini S&P 500'
            >>> print(info['multiplier'])  # 50
        """
        return cls.SYMBOL_DEFAULTS.get(symbol.upper())
    
    @classmethod
    def list_available_symbols(cls) -> list[str]:
        """
        Lista todos los símbolos pre-configurados.
        
        Returns:
            Lista de símbolos disponibles
            
        Ejemplo:
            >>> symbols = ContractBuilder.list_available_symbols()
            >>> print(symbols)  # ['ES', 'NQ', 'YM', 'RTY', 'GC', 'CL', '6E']
        """
        return list(cls.SYMBOL_DEFAULTS.keys())
    
    @classmethod
    def print_contract_info(cls, symbol: str):
        """
        Imprime información detallada de un contrato.
        
        Args:
            symbol: Símbolo a consultar
            
        Ejemplo:
            >>> ContractBuilder.print_contract_info('ES')
        """
        info = cls.get_contract_info(symbol)
        
        if info is None:
            print(f"Símbolo '{symbol}' no encontrado en base de datos")
            print(f"Símbolos disponibles: {', '.join(cls.list_available_symbols())}")
            return
        
        print("=" * 70)
        print(f"INFORMACIÓN DEL CONTRATO: {symbol}")
        print("=" * 70)
        print(f"Nombre completo:  {info['name']}")
        print(f"Descripción:      {info['description']}")
        print(f"Exchange:         {info['exchange']}")
        print(f"Moneda:           {info['currency']}")
        print(f"Multiplicador:    {info['multiplier']} (cada punto = ${info['multiplier']})")
        print(f"Tick mínimo:      {info['min_tick']}")
        print("=" * 70)
    
    @classmethod
    def calculate_contract_value(
        cls,
        symbol: str,
        price: float,
        contracts: int = 1
    ) -> Optional[float]:
        """
        Calcula el valor nocional de una posición.
        
        Args:
            symbol: Símbolo del contrato
            price: Precio actual del contrato
            contracts: Número de contratos
            
        Returns:
            Valor nocional en USD o None si símbolo no existe
            
        Ejemplo:
            >>> # 1 contrato ES a 5875.00
            >>> value = ContractBuilder.calculate_contract_value('ES', 5875.00, 1)
            >>> print(f"Valor: ${value:,.2f}")  # Valor: $293,750.00
        """
        info = cls.get_contract_info(symbol)
        if info is None:
            return None
        
        return price * info['multiplier'] * contracts
    
    @classmethod
    def calculate_tick_value(
        cls,
        symbol: str,
        contracts: int = 1
    ) -> Optional[float]:
        """
        Calcula el valor monetario de un tick (movimiento mínimo).
        
        Args:
            symbol: Símbolo del contrato
            contracts: Número de contratos
            
        Returns:
            Valor de un tick en USD o None si símbolo no existe
            
        Ejemplo:
            >>> # Valor de 1 tick de ES (0.25 puntos)
            >>> tick_val = ContractBuilder.calculate_tick_value('ES', 1)
            >>> print(f"1 tick ES = ${tick_val}")  # 1 tick ES = $12.50
        """
        info = cls.get_contract_info(symbol)
        if info is None:
            return None
        
        return info['min_tick'] * info['multiplier'] * contracts


# Función helper para crear contrato rápidamente
def create_contract(
    symbol: Optional[str] = None,
    sec_type: str = 'FUT',
    **kwargs
) -> Contract:
    """
    Factory function para crear contratos de manera rápida.
    
    Args:
        symbol: Símbolo del instrumento
        sec_type: Tipo de seguridad ('FUT', 'STK', 'CASH')
        **kwargs: Argumentos adicionales específicos del tipo
        
    Returns:
        Objeto Contract configurado
        
    Ejemplo:
        >>> # Futuro ES con defaults
        >>> contract = create_contract()
        
        >>> # Futuro NQ custom
        >>> contract = create_contract(symbol='NQ', contract_month='202606')
        
        >>> # Acción
        >>> contract = create_contract(symbol='AAPL', sec_type='STK')
    """
    if sec_type == 'FUT':
        return ContractBuilder.create_future_contract(symbol=symbol, **kwargs)
    elif sec_type == 'STK':
        if symbol is None:
            raise ValueError("symbol es requerido para contratos STK")
        return ContractBuilder.create_stock_contract(symbol=symbol, **kwargs)
    elif sec_type == 'CASH':
        if symbol is None:
            raise ValueError("symbol es requerido para contratos CASH (forex)")
        return ContractBuilder.create_forex_contract(symbol=symbol, **kwargs)
    else:
        raise ValueError(f"sec_type no soportado: {sec_type}")
