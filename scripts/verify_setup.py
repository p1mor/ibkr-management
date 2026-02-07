#!/usr/bin/env python3
"""Installation and configuration verification for IBKR Management.

Run with:
    python scripts/verify_setup.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def check_python_version() -> bool:
    """Validate minimum Python version."""
    print("Verificando versión de Python...")
    required_version = (3, 9)
    current_version = sys.version_info[:2]

    if current_version >= required_version:
        print(
            f"  ✓ Python {current_version[0]}.{current_version[1]} "
            f"(requerido: >={required_version[0]}.{required_version[1]})"
        )
        return True

    print(
        f"  ✗ Python {current_version[0]}.{current_version[1]} "
        f"(requerido: >={required_version[0]}.{required_version[1]})"
    )
    print(f"    Por favor actualiza Python a versión {required_version[0]}.{required_version[1]} o superior")
    return False


def check_dependencies() -> bool:
    """Validate required third-party packages."""
    print("\nVerificando dependencias...")

    required_packages = {
        "ibapi": "ibapi",
        "pandas": "pandas",
        "numpy": "numpy",
        "pyarrow": "pyarrow",
        "dotenv": "python-dotenv",
        "streamlit": "streamlit",
    }

    all_ok = True
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} - NO INSTALADO")
            all_ok = False

    if not all_ok:
        print("\n  Instalar dependencias faltantes con:")
        print("    pip install -r requirements.txt")

    return all_ok


def check_configuration() -> bool:
    """Validate repo configuration."""
    print("\nVerificando configuración...")

    env_file = Path(".env")
    if env_file.exists():
        print("  ✓ Archivo .env encontrado")
    else:
        print("  ⚠️  Archivo .env no encontrado - usando defaults")
        print("    Recomendación: cp .env.example .env")

    try:
        from ibkr_management.config import Settings

        is_valid, errors = Settings.validate_config()
        if not is_valid:
            print("  ✗ Errores en configuración:")
            for error in errors:
                print(f"    - {error}")
            return False

        print("  ✓ Configuración válida")

        port_mode = "Paper" if Settings.IBKR_PORT == 4002 else "Live"
        print("\n  Configuración actual:")
        print(f"    Host: {Settings.IBKR_HOST}")
        print(f"    Puerto: {Settings.IBKR_PORT} ({port_mode})")
        print(f"    Símbolo: {Settings.IBKR_SYMBOL}")
        print(f"    Exchange: {Settings.IBKR_EXCHANGE}")
        print(f"    Contrato: {Settings.IBKR_CONTRACT_MONTH}")
        print(f"    Directorio datos: {Settings.DATA_OUTPUT_DIR.absolute()}")

        return True

    except Exception as exc:
        print(f"  ✗ Error al cargar configuración: {exc}")
        return False


def check_directories() -> bool:
    """Validate required directories."""
    print("\nVerificando directorios...")

    try:
        from ibkr_management.config import Settings

        if Settings.DATA_OUTPUT_DIR.exists():
            print(f"  ✓ Directorio de datos existe: {Settings.DATA_OUTPUT_DIR}")
        else:
            print(f"  ⚠️  Creando directorio de datos: {Settings.DATA_OUTPUT_DIR}")
            Settings.DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            print("  ✓ Directorio creado")

        return True

    except Exception as exc:
        print(f"  ✗ Error con directorios: {exc}")
        return False


def check_modules() -> bool:
    """Validate project imports."""
    print("\nVerificando módulos del proyecto...")

    modules = [
        ("ibkr_management.config", ["Settings", "ContractBuilder"]),
        ("ibkr_management.core", ["OrderBook", "DataValidator"]),
        ("ibkr_management.storage", ["ParquetWriter"]),
        ("ibkr_management.utils", ["setup_logging", "get_logger"]),
    ]

    all_ok = True
    for module_name, objects in modules:
        module_ok = True
        try:
            module = __import__(module_name, fromlist=objects)
            for obj in objects:
                if not hasattr(module, obj):
                    print(f"  ✗ {module_name}.{obj} - NO ENCONTRADO")
                    module_ok = False
            if module_ok:
                print(f"  ✓ {module_name} ({', '.join(objects)})")
        except ImportError as exc:
            print(f"  ✗ {module_name} - ERROR: {exc}")
            module_ok = False

        if not module_ok:
            all_ok = False

    return all_ok


def main() -> int:
    """Run all setup checks."""
    print("=" * 70)
    print("VERIFICACIÓN DE INSTALACIÓN - IBKR Management")
    print("=" * 70)

    checks = [
        ("Versión Python", check_python_version),
        ("Dependencias", check_dependencies),
        ("Configuración", check_configuration),
        ("Directorios", check_directories),
        ("Módulos", check_modules),
    ]

    results = []
    for name, check_func in checks:
        try:
            results.append(check_func())
        except Exception as exc:
            print(f"\n✗ Error en verificación '{name}': {exc}")
            results.append(False)

    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)

    all_passed = all(results)

    if all_passed:
        print("\n✓ Todas las verificaciones pasaron")
        print("\n🚀 Sistema listo para usar")
        print("\nPróximos pasos:")
        print("  1. Asegurar que IB Gateway esté corriendo y logueado")
        print("  2. Ejecutar ejemplo básico:")
        print("     python examples/basic_connection.py")
        print("  3. Ejecutar dashboard:")
        print("     streamlit run examples/dashboard_app/app.py")
    else:
        print("\n✗ Algunas verificaciones fallaron")
        print("\n⚠️  Por favor corrige los errores antes de continuar")
        print("\nRecursos:")
        print("  - README.md - Documentación canónica")
        print("  - AGENTS.md - Reglas de trabajo y comandos")

    print("\n" + "=" * 70)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
