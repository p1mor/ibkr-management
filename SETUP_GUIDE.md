# 🚀 Guía Rápida de Instalación y Configuración

## Resumen de 5 Minutos

Esta guía te llevará de cero a capturando datos en vivo desde Interactive Brokers en menos de 5 minutos (asumiendo que ya tienes cuenta de IBKR).

---

## Paso 1: Descargar IB Gateway (2 min)

### MacOS
```bash
# Ir a: https://www.interactivebrokers.com/en/trading/ibgateway-stable.php
# Descargar: ibgateway-stable-standalone-macos-x64.dmg
# Instalar: Arrastrar a Applications
```

### Windows
```bash
# Descargar: ibgateway-stable-standalone-windows-x64.exe
# Ejecutar como administrador
# Seguir instalador
```

### Linux
```bash
chmod +x ibgateway-stable-standalone-linux-x64.sh
./ibgateway-stable-standalone-linux-x64.sh
```

---

## Paso 2: Configurar IB Gateway API (1 min)

1. **Abrir IB Gateway**
2. **Login** con tus credenciales de IBKR
3. **File → Global Configuration → API → Settings**
4. **Configurar**:
   - ✓ Enable ActiveX and Socket Clients
   - Socket port: **4001** (Paper) o **4002** (Live)
   - Trusted IPs: **127.0.0.1**
   - Read-Only API: **NO** (desactivar)
5. **Reiniciar IB Gateway**

---

## Paso 3: Instalar Python y Dependencias (1 min)

```bash
# Navegar al directorio
cd /path/to/ibkr_management

# Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # MacOS/Linux
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

---

## Paso 4: Configurar Variables de Entorno (30 seg)

```bash
# Copiar template
cp .env.example .env

# Editar .env con tu editor favorito
nano .env
# o
code .env
```

**Configuración mínima**:
```bash
IBKR_HOST=127.0.0.1
IBKR_PORT=4001              # 4001=Paper, 4002=Live
IBKR_CLIENT_ID=1
IBKR_SYMBOL=ES
IBKR_EXCHANGE=CME
IBKR_CONTRACT_MONTH=202603  # ⚠️ Actualizar según mes actual
```

**⚠️ IMPORTANTE**: Actualizar `IBKR_CONTRACT_MONTH` al contrato activo:
- Enero-Febrero: 202603 (Marzo)
- Marzo-Mayo: 202606 (Junio)
- Junio-Agosto: 202609 (Septiembre)
- Septiembre-Noviembre: 202612 (Diciembre)

---

## Paso 5: Probar Conexión (30 seg)

```bash
# Ejecutar ejemplo básico
python examples/basic_connection.py
```

**Deberías ver**:
```
✓ Conectado a IB Gateway!
✓ CONTRATO VALIDADO
  Símbolo:       ES
  Exchange:      CME
  ...
📊 Iniciando subscripción a datos de mercado...
🎯 Tick #1 | 14:35:22 | Precio:   5875.25 | Cantidad:     5 | Exchange: CME
🎯 Tick #2 | 14:35:23 | Precio:   5875.50 | Cantidad:     3 | Exchange: CME
...
```

**Si funciona**: ¡Felicidades! 🎉 Ya estás recibiendo datos en vivo.

**Si no funciona**: Ver sección de Troubleshooting abajo.

---

## Paso 6: Ejecutar Pipeline Completo (OPCIONAL)

```bash
# Pipeline completo con almacenamiento Parquet
python main.py
```

Esto capturará **trades + order book** y los guardará en:
```
data/es_cme_trades_20260206.parquet
```

---

## Troubleshooting Rápido

### ❌ "Connection refused"
- **Causa**: IB Gateway no está corriendo o puerto incorrecto
- **Solución**: 
  1. Abrir IB Gateway
  2. Verificar puerto en configuración
  3. Asegurar que estás logueado

### ❌ "No security definition found"
- **Causa**: Contrato inválido o mes vencido
- **Solución**: 
  1. Actualizar `IBKR_CONTRACT_MONTH` en `.env`
  2. Usar formato YYYYMM (ej: 202603)

### ❌ "Market data not subscribed"
- **Causa**: Tu cuenta no tiene permisos de market data
- **Solución**: 
  1. Ir a Account Management en IBKR
  2. Market Data Subscriptions
  3. Activar "US Securities Snapshot and Futures Value Bundle" (gratuito)

### ❌ "API not enabled"
- **Causa**: Settings API no configurados
- **Solución**: 
  1. IB Gateway → File → Global Configuration → API → Settings
  2. Enable ActiveX and Socket Clients = ✓
  3. Reiniciar Gateway

---

## Verificación de Sistema

Ejecuta este comando para verificar tu configuración:

```bash
python -c "from config import Settings; Settings.print_config()"
```

Debe mostrar tu configuración actual sin errores.

---

## Mantenimiento Semanal

### Cada Domingo

1. **Cerrar script** (Ctrl+C si está corriendo)
2. **Cerrar IB Gateway**
3. **Abrir IB Gateway** (pedirá credenciales)
4. **Login** con usuario/password
5. **Reiniciar script**

**¿Por qué?** IBKR hace mantenimiento dominical y requiere re-login.

---

## Actualización Mensual de Contratos

### ES (E-mini S&P 500)

Vence trimestralmente: **Marzo, Junio, Septiembre, Diciembre**

**Rollover**: 1-2 semanas antes del vencimiento (3er viernes del mes)

**Actualizar `.env`**:
```bash
# Si estamos en Enero 2026, usar Marzo:
IBKR_CONTRACT_MONTH=202603

# En Marzo, cambiar a Junio:
IBKR_CONTRACT_MONTH=202606
```

---

## Análisis de Datos Capturados

```python
import pandas as pd
import pyarrow.parquet as pq

# Leer archivo
df = pq.read_table('data/es_cme_trades_20260206.parquet').to_pandas()

# Ver estructura
print(df.info())
print(df.head())

# Solo trades válidos
clean = df[df['validation_final'] == True]

# Trades por minuto
clean['minute'] = clean['event_time_server_ms'].dt.floor('1min')
volume = clean.groupby('minute')['trade_qty'].sum()
print(volume)
```

---

## Recursos Adicionales

- **README completo**: [`README.md`](README.md)
- **Documentación IBKR API**: https://interactivebrokers.github.io/tws-api/
- **Ejemplos avanzados**: Carpeta `examples/`

---

## ¿Listo para más?

1. ✅ **Conexión básica funcionando** → `examples/basic_connection.py`
2. ✅ **Datos guardándose** → `main.py`
3. 🚀 **Siguiente nivel**: Desarrollar estrategias con los datos

---

**¡Buena suerte en tu viaje de trading cuantitativo! 📈**
