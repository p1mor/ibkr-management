```
 ██╗██████╗ ██╗  ██╗██████╗     ███╗   ███╗ █████╗ ███╗   ██╗ █████╗  ██████╗ ███████╗███╗   ███╗███████╗███╗   ██╗████████╗
 ██║██╔══██╗██║ ██╔╝██╔══██╗    ████╗ ████║██╔══██╗████╗  ██║██╔══██╗██╔════╝ ██╔════╝████╗ ████║██╔════╝████╗  ██║╚══██╔══╝
 ██║██████╔╝█████╔╝ ██████╔╝    ██╔████╔██║███████║██╔██╗ ██║███████║██║  ███╗█████╗  ██╔████╔██║█████╗  ██╔██╗ ██║   ██║   
 ██║██╔══██╗██╔═██╗ ██╔══██╗    ██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║██║   ██║██╔══╝  ██║╚██╔╝██║██╔══╝  ██║╚██╗██║   ██║   
 ██║██████╔╝██║  ██╗██║  ██║    ██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║╚██████╔╝███████╗██║ ╚═╝ ██║███████╗██║ ╚████║   ██║   
 ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   
```

# 📊 Sistema Profesional de Captura de Datos Ultra-Alta Frecuencia

## 🎯 Bienvenido Estudiante

Este proyecto te enseñará a conectarte a **Interactive Brokers** y capturar datos de mercado profesionales con arquitectura de producción.

---

## 🚀 INICIO RÁPIDO (3 pasos)

### 1️⃣ Leer la Documentación

Comienza aquí según tu nivel:

| Documento | Para quién | Tiempo |
|-----------|------------|--------|
| **[SETUP_GUIDE.md](SETUP_GUIDE.md)** | Principiantes - Quiero empezar YA | 5 min |
| **[README.md](README.md)** | Intermedio - Quiero entender TODO | 30 min |
| **[INDEX.md](INDEX.md)** | Avanzado - Referencia de módulos | Variable |

### 2️⃣ Instalar y Configurar

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con tus valores

# 3. Verificar instalación
python verify_setup.py
```

### 3️⃣ Ejecutar Primer Ejemplo

```bash
# Asegurar que IB Gateway esté corriendo y logueado

# Ejecutar ejemplo básico
python examples/basic_connection.py
```

**¿Funciona?** 🎉 ¡Felicidades! Ya estás capturando datos profesionales.

---

## 📚 Ruta de Aprendizaje Recomendada

### Nivel 1: Conceptos Básicos (1-2 horas)

1. **Leer** [`SETUP_GUIDE.md`](SETUP_GUIDE.md) completo
2. **Instalar** IB Gateway y dependencias
3. **Ejecutar** `examples/basic_connection.py`
4. **Experimentar**: Cambiar símbolo en `.env` (ES → NQ)

**Meta**: Entender el flujo básico de conexión y recepción de datos.

### Nivel 2: Arquitectura del Sistema (2-3 horas)

1. **Leer** [`README.md`](README.md) - Arquitectura y Pipeline
2. **Explorar** cada módulo con sus demos:
   ```bash
   python -m config.contracts      # Contratos IBKR
   python -m core.orderbook        # Order Book
   python -m core.validators       # Validaciones
   python -m storage.parquet_writer # Almacenamiento
   ```
3. **Analizar** el código fuente de cada módulo

**Meta**: Comprender cómo cada pieza trabaja junta.

### Nivel 3: Análisis de Datos (1-2 horas)

1. **Capturar** datos por 1 hora con `basic_connection.py`
2. **Analizar** con Pandas:
   ```python
   import pandas as pd
   import pyarrow.parquet as pq
   
   df = pq.read_table('data/es_cme_trades_YYYYMMDD.parquet').to_pandas()
   print(df.info())
   print(df.describe())
   ```
3. **Visualizar** spread, volumen, etc.

**Meta**: Extraer insights de los datos capturados.

### Nivel 4: Personalización (Avanzado)

1. **Modificar** validaciones en `core/validators.py`
2. **Agregar** nuevos campos al esquema Parquet
3. **Crear** tu propia estrategia usando los datos
4. **Escalar** a múltiples símbolos simultáneamente

**Meta**: Adaptar el sistema a tus necesidades específicas.

---

## 📁 Estructura del Proyecto

```
ibkr_management/
│
├── 📘 README.md                   # Documentación completa (30 min)
├── 🚀 SETUP_GUIDE.md              # Guía de instalación (5 min)
├── 📇 INDEX.md                    # Índice de módulos
├── ⚙️  .env.example               # Template de configuración
├── 📦 requirements.txt            # Dependencias Python
├── 🔍 verify_setup.py             # Verificar instalación
│
├── config/                        # ⚙️  Configuración
│   ├── settings.py                   # Variables de entorno
│   └── contracts.py                  # Constructor de contratos
│
├── core/                          # 🧠 Lógica principal
│   ├── orderbook.py                  # Gestión del order book
│   └── validators.py                 # Validaciones de datos
│
├── storage/                       # 💾 Almacenamiento
│   └── parquet_writer.py             # Escritura a Parquet
│
├── utils/                         # 🛠 Utilidades
│   └── logging_config.py             # Sistema de logging
│
├── examples/                      # 📖 Ejemplos educativos
│   └── basic_connection.py           # Conexión básica (¡EMPIEZA AQUÍ!)
│
└── data/                          # 📊 Datos generados
    └── es_cme_trades_*.parquet
```

---

## 🎓 Preguntas Frecuentes

### ¿Necesito cuenta de Interactive Brokers?

**Sí**, pero puedes empezar con:
- **Paper Trading** (cuenta demo gratuita)
- Market data puede requerir subscripción ($)

### ¿Qué aprenderé con este proyecto?

1. Conexión a APIs financieras profesionales (IBKR TWS API)
2. Procesamiento de datos de alta frecuencia (tick-by-tick)
3. Arquitectura de sistemas de trading (modular, escalable)
4. Order book y microestructura de mercado
5. Validación y calidad de datos
6. Almacenamiento eficiente (Parquet, compresión)
7. Logging, error handling, reconexión automática
8. Análisis de datos financieros con Pandas

### ¿Puedo usar esto para trading real?

Este sistema es **educativo**. Para producción necesitarías:
- Más robustez en manejo de errores
- Backups y redundancia
- Monitoreo 24/7
- Testing exhaustivo
- Compliance y risk management

### ¿Qué símbolos puedo capturar?

Cualquiera que IBKR ofrezca con market data:
- **Futuros**: ES, NQ, YM, RTY (índices), GC (oro), CL (petróleo)
- **Forex**: EUR/USD, GBP/USD, etc. (IDEALPRO)
- **Acciones**: AAPL, TSLA, etc. (requiere permisos)

Configurar en `.env`:
```bash
IBKR_SYMBOL=NQ      # Cambiar a lo que necesites
IBKR_EXCHANGE=CME
```

### ¿Cómo actualizo el contrato cada mes?

Futuros tienen vencimiento. Actualizar en `.env`:

```bash
# ES vence trimestral: Mar, Jun, Sep, Dic
# Si es Enero 2026, usar:
IBKR_CONTRACT_MONTH=202603  # Marzo 2026

# En Marzo, cambiar a:
IBKR_CONTRACT_MONTH=202606  # Junio 2026
```

Ver calendario en `README.md` sección "Mantenimiento Semanal".

---

## 🔧 Troubleshooting

| Error | Causa Probable | Solución |
|-------|----------------|----------|
| Connection refused | IB Gateway no está corriendo | Abrir IB Gateway y login |
| No security definition | Contrato vencido/inválido | Actualizar CONTRACT_MONTH en .env |
| Market data not subscribed | Permisos faltantes | Activar subscripción en IBKR |
| Import error | Dependencias no instaladas | `pip install -r requirements.txt` |

Ver [`SETUP_GUIDE.md`](SETUP_GUIDE.md) para troubleshooting detallado.

---

## 📞 Recursos Adicionales

**Documentación Oficial**:
- IBKR TWS API: https://interactivebrokers.github.io/tws-api/
- ibapi Python: https://github.com/InteractiveBrokers/tws-api-public
- Pandas: https://pandas.pydata.org/docs/
- PyArrow: https://arrow.apache.org/docs/python/

**Dentro del Proyecto**:
- Cada módulo `.py` tiene docstrings detallados
- Cada módulo tiene demo ejecutable (`if __name__ == "__main__"`)
- Logs detallados en `ib_gateway_audit.log`

---

## ✅ Checklist de Inicio

- [ ] Leí [`SETUP_GUIDE.md`](SETUP_GUIDE.md)
- [ ] Instalé IB Gateway
- [ ] Configuré API Settings en Gateway
- [ ] Instalé dependencias Python (`pip install -r requirements.txt`)
- [ ] Creé archivo `.env` desde `.env.example`
- [ ] Ejecuté `python verify_setup.py` sin errores
- [ ] IB Gateway está corriendo y logueado
- [ ] Ejecuté `python examples/basic_connection.py` exitosamente
- [ ] Vi datos llegando en tiempo real 🎉

---

## 🚀 ¡Comienza Tu Viaje!

```bash
# Paso 1: Verificar sistema
python verify_setup.py

# Paso 2: Ejecutar ejemplo básico
python examples/basic_connection.py

# Paso 3: ¡Analizar datos!
```

---

## 📊 Lo Que Capturarás

Cada segundo, miles de eventos como este:

```
🎯 Tick #1 | 14:35:22.123 | Precio: 5875.25 | Qty: 5 | Exchange: CME
   Order Book:
     ASK: 5875.50 @ 30
     ASK: 5875.25 @ 28  ← Mejor Ask
     ────────────────────
     MID: 5875.125  |  SPREAD: 4.25 bps
     ────────────────────
     BID: 5875.00 @ 25  ← Mejor Bid
     BID: 5874.75 @ 30
   ✓ Validaciones: 7/7 PASS
```

**¡Datos institucionales de nivel profesional en tu computadora! 📈**

---

**Versión**: 1.0.0  
**Autor**: Quant TechPulse  
**Licencia**: Uso Educativo  
**Última actualización**: Febrero 2026

**¡Buena suerte en tu aprendizaje! 🎓🚀**
