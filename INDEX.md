# 📦 IBKR Management - Sistema de Captura de Datos Ultra-Alta Frecuencia

## 🎯 Resumen del Proyecto

Este proyecto proporciona un framework **profesional y educativo** para capturar datos de mercado de ultra-alta frecuencia desde Interactive Brokers, diseñado específicamente para futuros del CME (ES, NQ, YM, RTY, etc.).

**Características principales**:
- ✅ Captura tick-by-tick (trades individuales)
- ✅ Order Book completo (10 niveles de profundidad)
- ✅ Validaciones múltiples de calidad de datos (7 capas)
- ✅ Almacenamiento eficiente en Parquet con compresión Snappy
- ✅ Reconexión automática y manejo de errores robusto
- ✅ Arquitectura modular y extensible
- ✅ Sin hardcodeos - todo configurable vía variables de entorno
- ✅ Documentación exhaustiva con fines educativos

---

## 📁 Estructura del Proyecto

```
ibkr_management/
│
├── README.md                      # 📘 Documentación completa (este archivo)
├── SETUP_GUIDE.md                 # 🚀 Guía de instalación rápida (5 minutos)
├── requirements.txt               # 📦 Dependencias Python
├── .env.example                   # ⚙️  Template de configuración
│
├── config/                        # Configuración del sistema
│   ├── __init__.py
│   ├── settings.py                # Variables de entorno y configuración
│   └── contracts.py               # Constructor de contratos IBKR
│
├── core/                          # Lógica principal del sistema
│   ├── __init__.py
│   ├── connection.py              # Manejo de conexión y reconexión
│   ├── data_processor.py          # Procesamiento de ticks y depth
│   ├── orderbook.py               # Gestión del order book en memoria
│   └── validators.py              # Validaciones de datos (7 capas)
│
├── storage/                       # Persistencia de datos
│   ├── __init__.py
│   └── parquet_writer.py          # Escritura a Parquet con buffering
│
├── utils/                         # Utilidades compartidas
│   ├── __init__.py
│   └── logging_config.py          # Sistema de logging centralizado
│
├── examples/                      # Ejemplos educativos
│   ├── basic_connection.py        # Ejemplo 1: Conexión simple
│   └── full_pipeline.py           # Ejemplo 2: Pipeline completo (TODO)
│
├── data/                          # Datos generados (creado automáticamente)
│   └── es_cme_trades_YYYYMMDD.parquet
│
└── main.py                        # Script principal (TODO)
```

---

## 🚀 Inicio Rápido

### Opción 1: Guía Rápida (5 minutos)

Lee [`SETUP_GUIDE.md`](SETUP_GUIDE.md) para comenzar inmediatamente.

### Opción 2: Tutorial Completo

Lee [`README.md`](README.md) en la raíz del proyecto para entender todo el sistema en detalle.

### Opción 3: Explorar por Módulos

Cada archivo `.py` contiene:
- Documentación detallada
- Ejemplos de uso
- Demo ejecutable (`if __name__ == "__main__"`)

**Recomendación de lectura**:
1. `config/settings.py` - Entender configuración
2. `config/contracts.py` - Contratos IBKR
3. `core/orderbook.py` - Cómo funciona el order book
4. `core/validators.py` - Validaciones de datos
5. `storage/parquet_writer.py` - Almacenamiento
6. `examples/basic_connection.py` - Primer script práctico

---

## 📚 Documentación por Módulo

### 1. Configuración (`config/`)

#### `settings.py`
Gestiona toda la configuración del sistema usando variables de entorno:
- Conexión IBKR (host, puerto, client ID)
- Parámetros del contrato (símbolo, exchange, vencimiento)
- Configuración de almacenamiento (directorio, flush interval)
- Logging y validaciones

**Uso**:
```python
from config import Settings

print(f"Conectando a: {Settings.IBKR_HOST}:{Settings.IBKR_PORT}")
print(f"Símbolo: {Settings.IBKR_SYMBOL}")
```

#### `contracts.py`
Constructor de contratos IBKR con información pre-configurada de símbolos populares:
- Futuros: ES, NQ, YM, RTY, GC, CL
- Forex: EURUSD, etc.
- Acciones: AAPL, etc.

**Uso**:
```python
from config import ContractBuilder

# Crear contrato ES con configuración por defecto
contract = ContractBuilder.create_future_contract()

# Custom
contract = ContractBuilder.create_future_contract(
    symbol='NQ',
    contract_month='202606'
)

# Información del contrato
ContractBuilder.print_contract_info('ES')
```

---

### 2. Core (`core/`)

#### `orderbook.py`
Mantiene el order book en memoria con actualizaciones incrementales:
- 10 niveles de bid/ask
- Cálculo automático de mid price, spread, quality score
- Export a JSON para almacenamiento

**Uso**:
```python
from core import OrderBook

ob = OrderBook(max_depth=10)

# Actualizar con evento de market depth
ob.update(position=0, operation=0, side=1, price=5875.00, size=25)

# Obtener snapshot
bids, asks = ob.get_snapshot()
mid_price = ob.get_mid_price()
spread_abs, spread_bps = ob.get_spread()

print(ob)  # Visualización legible
```

#### `validators.py`
Sistema de validación de 7 capas:
- V1: Precio válido (> 0)
- V2: Cantidad válida (> 0)
- V3: Spread positivo (bid < ask)
- V4: Liquidez mínima en order book
- V5: Spread dentro de umbrales razonables
- P1: Timestamp válido
- Final: Todas las anteriores

**Uso**:
```python
from core import DataValidator

validator = DataValidator(max_spread_threshold=0.05)

result = validator.validate_trade(
    price=5875.25,
    quantity=5,
    event_time=1738876543210,
    bids=[(0, {'price': 5875.00, 'size': 25})],
    asks=[(0, {'price': 5875.25, 'size': 30})]
)

print(result)  # ✓ PASS o ✗ FAIL con detalles
```

---

### 3. Storage (`storage/`)

#### `parquet_writer.py`
Escritura eficiente a Parquet con:
- Buffer en memoria con flush automático cada 60s
- Thread-safe para múltiples productores
- Esquema estricto con 27 campos
- Compresión Snappy
- Concatenación automática a archivos existentes

**Uso**:
```python
from storage import ParquetWriter

# Context manager (recomendado)
with ParquetWriter() as writer:
    writer.add_record(record_dict)
    # Flush automático cada 60s
    
# Manual
writer = ParquetWriter(flush_interval=60)
writer.start()
writer.add_record(record_dict)
writer.flush()  # Flush manual
writer.stop()
```

---

### 4. Utils (`utils/`)

#### `logging_config.py`
Sistema de logging centralizado con:
- Rotación de archivos (10MB, 5 backups)
- Salida a consola y archivo
- Niveles configurables (DEBUG, INFO, WARNING, ERROR)
- Logger especializado para trading con contexto

**Uso**:
```python
from utils import setup_logging, get_logger, create_trade_logger

# Logger básico
logger = get_logger(__name__)
logger.info("Mensaje")

# Logger con contexto de trading
trade_logger = create_trade_logger('ES', 'EMA-OBI')
trade_logger.info("Trade ejecutado")
# Output: [ES] [EMA-OBI] Trade ejecutado
```

---

## 🎓 Ejemplos Educativos

### Ejemplo 1: Conexión Básica

**Archivo**: `examples/basic_connection.py`

Demuestra:
- Conexión a IB Gateway
- Validación de contrato
- Subscripción a tick-by-tick
- Visualización de datos en consola

**Ejecutar**:
```bash
python examples/basic_connection.py
```

**Salida esperada**:
```
✓ Conectado a IB Gateway!
✓ CONTRATO VALIDADO
  Símbolo:       ES
  Exchange:      CME
📊 Iniciando subscripción a datos de mercado...
🎯 Tick #1 | 14:35:22 | Precio:   5875.25 | Cantidad:     5
🎯 Tick #2 | 14:35:23 | Precio:   5875.50 | Cantidad:     3
...
```

---

## ⚙️ Configuración

### Variables de Entorno

Copiar `.env.example` a `.env` y personalizar:

```bash
cp .env.example .env
nano .env
```

**Variables clave**:
```bash
# Conexión
IBKR_HOST=127.0.0.1
IBKR_PORT=4001                     # 4001=Paper, 4002=Live
IBKR_CLIENT_ID=1

# Contrato
IBKR_SYMBOL=ES
IBKR_EXCHANGE=CME
IBKR_CONTRACT_MONTH=202603         # ⚠️ Actualizar mensualmente

# Almacenamiento
DATA_OUTPUT_DIR=./data
BUFFER_FLUSH_INTERVAL=60

# Logging
LOG_LEVEL=INFO
LOG_FILE=ib_gateway_audit.log
```

### Validar Configuración

```bash
python -c "from config import Settings; Settings.print_config()"
```

---

## 📊 Esquema de Datos

Cada registro en el archivo Parquet contiene **27 campos**:

### Identificación
- `symbol`: Símbolo del instrumento
- `trade_id`: ID único incremental
- `atomic_type`: 'trade' o 'depth'

### Timestamps (3 capas)
- `event_time_server_ms`: Timestamp del servidor IBKR (UTC)
- `trade_time_ms`: Timestamp del trade (UTC)
- `received_at_ingest_ns`: Timestamp de recepción local (UTC, nanosegundos)

### Datos del Trade
- `trade_price`: Precio (string para precisión decimal)
- `trade_qty`: Cantidad
- `buyer_is_maker`: Dirección del trade

### Order Book Snapshot
- `depth_last_update_id`: ID de sincronización
- `bids_json`: Array JSON de 10 mejores bids
- `asks_json`: Array JSON de 10 mejores asks
- `best_bid_price`, `best_bid_qty`
- `best_ask_price`, `best_ask_qty`
- `spread_bps`: Spread en basis points
- `depth_sync_quality`: Score 0-100

### Metadata
- `raw_json`: Evento original completo

### Validaciones (7 + 1)
- `validation_v1` a `validation_p1`: Cada validación individual
- `validation_final`: Todas las validaciones pasan
- `validation_flags`: Bitmask compacto (int32)

---

## 📈 Análisis de Datos

```python
import pandas as pd
import pyarrow.parquet as pq

# Leer archivo
df = pq.read_table('data/es_cme_trades_20260206.parquet').to_pandas()

# Filtrar solo trades válidos
trades = df[
    (df['atomic_type'] == 'trade') &
    (df['validation_final'] == True)
]

# Análisis de volumen por minuto
trades['minute'] = trades['event_time_server_ms'].dt.floor('1min')
volume_per_min = trades.groupby('minute')['trade_qty'].astype(float).sum()

# Análisis de spread
avg_spread = trades['spread_bps'].astype(float).mean()
print(f"Spread promedio: {avg_spread:.2f} bps")

# Order book depth updates
depth_updates = df[df['atomic_type'] == 'depth']
print(f"Total depth updates: {len(depth_updates)}")
```

---

## 🔧 Troubleshooting

Ver [`SETUP_GUIDE.md`](SETUP_GUIDE.md) sección de Troubleshooting para problemas comunes.

**Problemas más frecuentes**:
1. **Connection refused**: IB Gateway no está corriendo
2. **No security definition**: Contrato vencido o inválido
3. **Market data not subscribed**: Permisos faltantes en cuenta IBKR
4. **API not enabled**: Configuración API no habilitada en Gateway

---

## 🔄 Mantenimiento

### Semanal (Domingos)
- Reiniciar IB Gateway (requiere re-login)
- Verificar que el script se reconecte automáticamente

### Mensual
- Actualizar `IBKR_CONTRACT_MONTH` al siguiente vencimiento
- ES vence trimestralmente: Mar, Jun, Sep, Dic
- Hacer rollover 1-2 semanas antes del vencimiento

---

## 🎯 Roadmap / TODO

- [ ] Crear `main.py` orquestando todos los módulos
- [ ] Implementar `core/connection.py` con reconexión robusta
- [ ] Implementar `core/data_processor.py` integrando todos los componentes
- [ ] Crear `examples/full_pipeline.py` con ejemplo completo
- [ ] Agregar tests unitarios
- [ ] Agregar métricas de performance (latencia, throughput)
- [ ] Soporte multi-símbolo simultáneo
- [ ] WebSocket para streaming de datos a clientes
- [ ] Dashboard en tiempo real (Dash/Streamlit)

---

## 📞 Soporte y Recursos

**Documentación oficial IBKR**:
- TWS API: https://interactivebrokers.github.io/tws-api/
- ibapi Python: https://github.com/InteractiveBrokers/tws-api-public

**Archivos de log**:
- `ib_gateway_audit.log` - Log principal del sistema
- IB Gateway logs: `~/Jts/` (MacOS/Linux), `C:\Jts\` (Windows)

---

## ⚖️ Disclaimer

Este sistema es para fines **educativos y de investigación**. El trading de futuros conlleva riesgo sustancial de pérdida. No somos responsables de pérdidas financieras derivadas del uso de este software.

---

## 🚀 ¡Comienza Ahora!

1. **Instalación**: Lee [`SETUP_GUIDE.md`](SETUP_GUIDE.md)
2. **Primera conexión**: Ejecuta `examples/basic_connection.py`
3. **Profundiza**: Explora cada módulo con sus demos
4. **Analiza**: Captura datos y analiza con Pandas

**¡Éxito en tu viaje de trading cuantitativo! 📊🚀**
