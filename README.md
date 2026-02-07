# IBKR Ultra-High Frequency Data Acquisition System

## Índice
- [Introducción](#introducción)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Instalación y Configuración](#instalación-y-configuración)
- [Conexión con IB Gateway](#conexión-con-ib-gateway)
- [Pipeline de Procesamiento de Datos](#pipeline-de-procesamiento-de-datos)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Guía de Uso](#guía-de-uso)
- [Mantenimiento Semanal](#mantenimiento-semanal)
- [Troubleshooting](#troubleshooting)

---

## Introducción

Este sistema captura datos de **ultra-alta frecuencia** (tick-by-tick y order book completo) desde Interactive Brokers (IBKR) para instrumentos futuros, específicamente diseñado para el **E-mini S&P 500 (ES)** del CME.

### ¿Qué capturamos?
- **Trades individuales**: Cada transacción ejecutada en el mercado
- **Order Book (Depth of Market)**: Los 10 mejores niveles de bid/ask en tiempo real
- **Timestamps precisos**: Servidor (IBKR), recepción local, procesamiento
- **Validaciones múltiples**: 7 capas de validación de calidad de datos

### Frecuencia y Volumen
- **Frecuencia**: Milisegundos (1-5ms típico)
- **Volumen**: ~100,000 - 500,000 eventos/hora en horario de mayor actividad
- **Calidad**: Datos institucionales de nivel profesional

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERACTIVE BROKERS                       │
│                      (IB Gateway)                            │
└────────────────────────┬────────────────────────────────────┘
                         │ TWS API (Socket Connection)
                         │ Puerto 4001/4002
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               NUESTRO SISTEMA (Local/Cloud)                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. CONNECTION MANAGER                               │  │
│  │     - Autenticación                                  │  │
│  │     - Reconexión automática                          │  │
│  │     - Health monitoring                              │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  2. DATA PROCESSOR                                   │  │
│  │     - tickByTickAllLast (Trades)                     │  │
│  │     - updateMktDepth (Order Book)                    │  │
│  │     - Validación en tiempo real                      │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  3. STORAGE ENGINE                                   │  │
│  │     - Buffer en memoria (60s)                        │  │
│  │     - Escritura Parquet con compresión Snappy        │  │
│  │     - Schema estricto con timestamps UTC             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
              Archivos Parquet locales
              es_cme_trades_YYYYMMDD.parquet
```

---

## Instalación y Configuración

### Paso 1: Requisitos Previos

**Software necesario:**
- Python 3.9+ (recomendado 3.11)
- Cuenta de Interactive Brokers (con permisos de market data)
- IB Gateway o TWS (Trader Workstation)

**Hardware recomendado:**
- CPU: 4+ cores
- RAM: 8GB mínimo (16GB recomendado)
- Disco: SSD con 100GB+ libres
- Red: Conexión estable de baja latencia

### Paso 2: Instalar IB Gateway

1. **Descargar IB Gateway**:
   - Ir a: https://www.interactivebrokers.com/en/trading/ibgateway-stable.php
   - Descargar la versión **STABLE** (no latest) para tu sistema operativo
   - MacOS: `ibgateway-stable-standalone-macos-x64.dmg`
   - Windows: `ibgateway-stable-standalone-windows-x64.exe`
   - Linux: `ibgateway-stable-standalone-linux-x64.sh`

2. **Instalar IB Gateway**:
   ```bash
   # MacOS
   open ibgateway-stable-standalone-macos-x64.dmg
   # Arrastra IB Gateway a Applications
   
   # Windows
   # Ejecutar el instalador .exe como administrador
   
   # Linux
   chmod +x ibgateway-stable-standalone-linux-x64.sh
   ./ibgateway-stable-standalone-linux-x64.sh
   ```

3. **Configuración inicial de IB Gateway**:
   - Abrir IB Gateway
   - Ingresar tu **username** y **password** de IBKR
   - Seleccionar **"IB API"** (NO "TWS")
   - Puerto por defecto: **4001** (Paper Trading) o **4002** (Live Trading)

### Paso 3: Configurar IB Gateway para Conexiones API

**CRÍTICO: Configurar API Settings**

1. Dentro de IB Gateway, ir a: **File → Global Configuration → API → Settings**

2. Configurar:
   ```
   ✓ Enable ActiveX and Socket Clients
   ✓ Socket port: 4001 (Paper) / 4002 (Live)
   ✓ Master API client ID: 0
   ✓ Read-Only API: NO (desactivado)
   ✗ Trusted IP addresses: 127.0.0.1 (agregar)
   ```

3. **IMPORTANTE**: Reiniciar IB Gateway después de estos cambios

### Paso 4: Instalar Dependencias Python

```bash
cd /path/to/ibkr_management

# Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # MacOS/Linux
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 5: Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# .env
IBKR_HOST=127.0.0.1
IBKR_PORT=4001              # 4001=Paper, 4002=Live
IBKR_CLIENT_ID=1
IBKR_SYMBOL=ES
IBKR_EXCHANGE=CME
IBKR_CONTRACT_MONTH=202603  # Actualizar según vencimiento
DATA_OUTPUT_DIR=./data
LOG_LEVEL=INFO
```

---

## Conexión con IB Gateway

### Proceso de Conexión Paso a Paso

1. **Iniciar IB Gateway**:
   ```bash
   # Abrir IB Gateway manualmente
   # O usar script de inicio automático:
   ./scripts/start_ibgateway.sh
   ```

2. **Login en IB Gateway**:
   - Usuario: Tu username de IBKR
   - Contraseña: Tu password de IBKR
   - Click en **"Login"**

3. **Verificar estado de conexión**:
   - Estado debe mostrar: **"Connected"** o **"Logged in"**
   - Puerto activo: **4001** o **4002**

4. **Ejecutar nuestro script de conexión**:
   ```bash
   # Ejemplo básico (recomendado para empezar)
   python examples/basic_connection.py
   
   # Pipeline completo
   python main.py
   ```

### Flujo de Autenticación

```
Usuario → IB Gateway → IBKR Servers → Autenticación
                ↓
           Puerto 4001/4002
                ↓
         Nuestro Script Python
                ↓
         Suscripción a datos
```

---

## Pipeline de Procesamiento de Datos

### Fase 1: Captura de Eventos

**tickByTickAllLast - Trades ejecutados**:
```python
# Cada trade que ocurre en el mercado:
{
    'event_time': 1738876543210,  # Timestamp del servidor IBKR (ms)
    'price': 5875.25,              # Precio de ejecución
    'size': 5,                     # Cantidad de contratos
    'exchange': 'CME',             # Exchange
    'received_at': 1738876543212   # Timestamp de recepción local (ns)
}
```

**updateMktDepth - Order Book**:
```python
# Cada actualización del libro de órdenes:
{
    'position': 0,        # Nivel (0 = mejor bid/ask)
    'operation': 0,       # 0=Insert, 1=Update, 2=Delete
    'side': 1,            # 0=Ask, 1=Bid
    'price': 5875.00,     # Precio del nivel
    'size': 25            # Cantidad disponible
}
```

### Fase 2: Enriquecimiento de Datos

Para cada evento, agregamos:

1. **Snapshot del Order Book**:
   - 10 mejores bids
   - 10 mejores asks
   - Best Bid/Ask Price & Quantity
   - Spread en basis points

2. **Timestamps múltiples**:
   - `event_time_server_ms`: Timestamp del servidor IBKR
   - `trade_time_ms`: Timestamp del trade
   - `received_at_ingest_ns`: Timestamp de recepción (nanosegundos)

3. **Métricas calculadas**:
   - Mid Price: `(best_bid + best_ask) / 2`
   - Spread BPS: `((ask - bid) / bid) * 10000`
   - Depth Quality: Métrica de liquidez

### Fase 3: Validaciones (7 capas)

```python
validation_v1: price > 0                    # Precio válido
validation_v2: quantity > 0                 # Cantidad válida
validation_v3: best_bid < best_ask          # Spread positivo
validation_v4: len(bids) >= 1 AND len(asks) >= 1  # Book tiene liquidez
validation_v5: 0 < spread < 10%             # Spread razonable
validation_p1: event_time > 0               # Timestamp válido
validation_final: ALL validations pass      # Pasa todas
```

**validation_flags**: Bitmask compacto (int32) de todas las validaciones

### Fase 4: Almacenamiento

**Buffer en memoria**:
- Capacidad: 60 segundos de datos
- Thread-safe con `threading.Lock()`
- Auto-flush cada minuto

**Formato Parquet**:
```python
Schema:
- symbol: string                    # "ES"
- trade_id: int64                   # ID único incremental
- atomic_type: string               # "trade" | "depth"
- event_time_server_ms: timestamp   # UTC
- trade_time_ms: timestamp          # UTC
- received_at_ingest_ns: timestamp  # UTC nanosegundos
- trade_price: string               # Decimal preciso
- trade_qty: string                 # Decimal preciso
- buyer_is_maker: bool              # Dirección del trade
- depth_last_update_id: int64       # Sincronización
- bids_json: string                 # Array JSON de bids
- asks_json: string                 # Array JSON de asks
- best_bid_price: string
- best_bid_qty: string
- best_ask_price: string
- best_ask_qty: string
- spread_bps: string                # Basis points
- depth_sync_quality: int32         # Métrica 0-100
- raw_json: string                  # Evento original
- validation_v1 a validation_final: bool
- validation_flags: int32           # Bitmask
```

**Compresión**: Snappy (balance velocidad/ratio)

**Nomenclatura**: `{symbol}_{exchange}_trades_{YYYYMMDD}.parquet`

Ejemplo: `es_cme_trades_20260206.parquet`

---

## Estructura del Proyecto

```
ibkr_management/
│
├── README.md                     # ← Este archivo (tutorial completo)
├── requirements.txt              # Dependencias Python
├── .env.example                  # Template de configuración
├── main.py                       # Script principal
│
├── config/                       # Configuración
│   ├── __init__.py
│   ├── settings.py               # Variables de entorno y configuración
│   └── contracts.py              # Definiciones de contratos IBKR
│
├── core/                         # Lógica principal
│   ├── __init__.py
│   ├── connection.py             # Manejo de conexión IB Gateway
│   ├── data_processor.py         # Procesamiento de ticks y depth
│   ├── orderbook.py              # Gestión del order book
│   └── validators.py             # Validaciones de datos
│
├── storage/                      # Persistencia
│   ├── __init__.py
│   └── parquet_writer.py         # Escritura a Parquet
│
├── utils/                        # Utilidades
│   ├── __init__.py
│   └── logging_config.py         # Configuración de logs
│
├── examples/                     # Ejemplos educativos
│   ├── basic_connection.py       # Conexión simple
│   └── full_pipeline.py          # Pipeline completo
│
└── data/                         # Datos generados (creado automáticamente)
    └── es_cme_trades_*.parquet
```

---

## Guía de Uso

### Ejemplo 1: Conexión Básica

```bash
python examples/basic_connection.py
```

Este ejemplo te muestra:
- Cómo conectar a IB Gateway
- Validar un contrato
- Recibir tus primeros ticks

### Visualización Interactiva (Dashboard)

En otra terminal (mientras `basic_connection.py` está corriendo):

```bash
streamlit run examples/live_dashboard.py
```

El dashboard lee `ib_gateway_audit.log` y muestra:
- Ticks totales, último precio, último tamaño y spread
- Gráficas de precio/cantidad
- Eventos recientes del log (incluyendo warnings/errores)

### Ejemplo 2: Pipeline Completo

```bash
python main.py
```

Captura completa con:
- Trades + Order Book
- Validaciones
- Almacenamiento Parquet
- Reconexión automática

### Análisis de Datos Capturados

```python
import pandas as pd
import pyarrow.parquet as pq

# Leer archivo Parquet
df = pq.read_table('data/es_cme_trades_20260206.parquet').to_pandas()

# Ver estructura
print(df.info())
print(df.head())

# Filtrar solo trades (no depth updates)
trades = df[df['atomic_type'] == 'trade']

# Filtrar datos validados
clean_data = df[df['validation_final'] == True]

# Análisis de spread
print(f"Spread promedio: {clean_data['spread_bps'].astype(float).mean():.2f} bps")

# Análisis de volumen por minuto
trades['minute'] = trades['event_time_server_ms'].dt.floor('1min')
volume_per_minute = trades.groupby('minute')['trade_qty'].sum()
print(volume_per_minute)
```

---

## Mantenimiento Semanal

### Reinicio de Credenciales (Domingos)

**¿Por qué los domingos?**
- Interactive Brokers realiza mantenimiento programado
- El sistema se desconecta completamente
- Se requiere re-autenticación manual

**Procedimiento cada domingo (o después de desconexión prolongada)**:

1. **Cerrar procesos activos**:
   ```bash
   # Detener nuestro script si está corriendo
   # Ctrl+C en la terminal donde corre
   
   # O usar kill
   ps aux | grep python
   kill -9 <PID>
   ```

2. **Cerrar IB Gateway**:
   - File → Exit
   - O cerrar la ventana

3. **Reiniciar IB Gateway**:
   ```bash
   # Abrir IB Gateway nuevamente
   # Login con tus credenciales
   ```

4. **Verificar configuración API**:
   - File → Global Configuration → API → Settings
   - Confirmar puerto y trusted IPs

5. **Reiniciar nuestro script**:
   ```bash
   python main.py
   ```

6. **Verificar logs**:
   ```bash
   tail -f ib_gateway_audit.log
   ```

### Actualización de Contratos

Los contratos de futuros tienen vencimiento. Actualizar mensualmente:

**En `config/contracts.py`**:
```python
# Ejemplo: ES vence cada trimestre (Mar, Jun, Sep, Dic)
# Si estamos en Enero 2026, usar contrato Marzo 2026:
CONTRACT_MONTH = "202603"  # YYYYMM

# Calendario de vencimientos ES:
# H = Mar (03)
# M = Jun (06)
# U = Sep (09)
# Z = Dic (12)
```

**O en `.env`**:
```bash
IBKR_CONTRACT_MONTH=202603
```

---

## Troubleshooting

### Problema 1: No conecta a IB Gateway

**Error**: `ConnectionRefusedError: [Errno 61] Connection refused`

**Soluciones**:
1. Verificar que IB Gateway esté abierto y logueado
2. Confirmar puerto correcto (4001 o 4002)
3. Verificar API Settings en Gateway:
   ```
   File → Global Configuration → API → Settings
   ✓ Enable ActiveX and Socket Clients
   ```
4. Agregar 127.0.0.1 a Trusted IPs

### Problema 2: No recibe datos

**Error**: Conecta pero no llegan ticks

**Soluciones**:
1. Verificar suscripción de market data en tu cuenta IBKR
2. Confirmar que el contrato es válido:
   ```python
   # Ver logs: "Contrato ES validado exitosamente"
   ```
3. Verificar horario de mercado:
   - ES trading hours: Domingo 5pm - Viernes 4pm CT
   - Fuera de horario no habrá datos

### Problema 3: Contrato no válido

**Error**: `No security definition has been found`

**Soluciones**:
1. Actualizar `CONTRACT_MONTH` al contrato activo
2. Verificar símbolo y exchange:
   ```python
   symbol = "ES"      # E-mini S&P 500
   exchange = "CME"   # Chicago Mercantile Exchange
   ```

### Problema 4: Desconexiones frecuentes

**Síntomas**: Reconecta cada pocos minutos

**Soluciones**:
1. Verificar estabilidad de red
2. Deshabilitar firewall/antivirus temporalmente
3. Aumentar timeout en `connection.py`:
   ```python
   self.setTimeout(30)  # Aumentar a 60
   ```
4. Verificar que no haya múltiples clientes conectados con mismo ID

### Problema 5: Archivos Parquet corruptos

**Error al leer**: `pyarrow.lib.ArrowInvalid`

**Soluciones**:
1. El buffer se flushea en desconexión abrupta
2. Usar `flush_buffer()` antes de cerrar
3. Verificar espacio en disco
4. Script hace flush automático cada minuto

---

## Métricas de Calidad

### Latencia Típica
- **IBKR Server → Local**: 5-15ms (depende de ubicación)
- **Procesamiento interno**: <1ms
- **Escritura a buffer**: <0.1ms

### Tasa de Validación
- **validation_final = True**: >99.9% en condiciones normales
- **validation_v3 fails**: Ocurre en market open/close (spread anormal)

### Uptime
- **Target**: >99% durante horario de mercado
- **Reconexión automática**: <10 segundos
- **Pérdida de datos**: Mínima (buffer en memoria flush)

---

## Próximos Pasos

1. **Ejecutar `basic_connection.py`** y ver tus primeros datos
2. **Analizar un día de datos** con Pandas
3. **Experimentar con diferentes símbolos** (NQ, YM, etc.)
4. **Integrar con estrategias de trading**
5. **Escalar a múltiples símbolos** simultáneamente

---

## Soporte

**Documentación oficial**:
- IBKR TWS API: https://interactivebrokers.github.io/tws-api/
- ibapi Python: https://github.com/InteractiveBrokers/tws-api-public

**Recursos para profundizar (trading algorítmico)**:
- NautilusTrader (conceptos/overview): https://nautilustrader.io/docs/latest/concepts/overview/
  - Plataforma de trading algorítmico y backtesting event-driven; útil si quieres pasar de “capturar datos” a “modelar, backtestear y ejecutar” estrategias con una arquitectura más completa.
- NautilusTrader + Interactive Brokers (adapter IBKR): https://nautilustrader.io/docs/latest/integrations/ib/
  - Explica cómo conectarse a TWS/IB Gateway, componentes (DataClient/ExecutionClient/InstrumentProvider) y ejemplos.
- Repositorio (código fuente): https://github.com/axelsnoski/NautilusTrader

**Logs**:
- `ib_gateway_audit.log`: Log principal del sistema
- IB Gateway logs: `~/Jts/` (MacOS/Linux) o `C:\Jts\` (Windows)

---

## Disclaimer

Este sistema es para fines educativos y de investigación. El trading de futuros conlleva riesgo sustancial de pérdida. No somos responsables de pérdidas financieras derivadas del uso de este software.

---

**¡Éxito en tu aprendizaje! **
