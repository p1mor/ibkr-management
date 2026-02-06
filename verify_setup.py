#!/usr/bin/env python3
"""
verify_setup.py - Script de verificación de instalación

Verifica que todas las dependencias estén instaladas y la configuración
sea correcta antes de ejecutar el sistema principal.

Uso:
    python verify_setup.py
"""

import sys
from pathlib import Path


def check_python_version():
    """Verifica versión de Python."""
    print("Verificando versión de Python...")
    required_version = (3, 9)
    current_version = sys.version_info[:2]
    
    if current_version >= required_version:
        print(f"  ✓ Python {current_version[0]}.{current_version[1]} (requerido: >={required_version[0]}.{required_version[1]})")
        return True
    else:
        print(f"  ✗ Python {current_version[0]}.{current_version[1]} (requerido: >={required_version[0]}.{required_version[1]})")
        print(f"    Por favor actualiza Python a versión {required_version[0]}.{required_version[1]} o superior")
        return False


def check_dependencies():
    """Verifica dependencias instaladas."""
    print("\nVerificando dependencias...")
    
    required_packages = {
        'ibapi': 'ibapi',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'pyarrow': 'pyarrow',
        'dotenv': 'python-dotenv',
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


def check_configuration():
    """Verifica configuración del sistema."""
    print("\nVerificando configuración...")
    
    # Verificar que existe .env o podemos usar defaults
    env_file = Path('.env')
    if env_file.exists():
        print(f"  ✓ Archivo .env encontrado")
    else:
        print(f"  ⚠️  Archivo .env no encontrado - usando defaults")
        print(f"    Recomendación: cp .env.example .env")
    
    # Importar configuración
    try:
        from config import Settings
        
        # Validar configuración
        is_valid, errors = Settings.validate_config()
        
        if is_valid:
            print(f"  ✓ Configuración válida")
        else:
            print(f"  ✗ Errores en configuración:")
            for error in errors:
                print(f"    - {error}")
            return False
        
        # Mostrar configuración clave
        print(f"\n  Configuración actual:")
        print(f"    Host: {Settings.IBKR_HOST}")
        print(f"    Puerto: {Settings.IBKR_PORT} ({'Paper' if Settings.IBKR_PORT == 4001 else 'Live'})")
        print(f"    Símbolo: {Settings.IBKR_SYMBOL}")
        print(f"    Exchange: {Settings.IBKR_EXCHANGE}")
        print(f"    Contrato: {Settings.IBKR_CONTRACT_MONTH}")
        print(f"    Directorio datos: {Settings.DATA_OUTPUT_DIR.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error al cargar configuración: {e}")
        return False


def check_directories():
    """Verifica que directorios necesarios existan."""
    print("\nVerificando directorios...")
    
    try:
        from config import Settings
        
        # Verificar/crear directorio de datos
        if Settings.DATA_OUTPUT_DIR.exists():
            print(f"  ✓ Directorio de datos existe: {Settings.DATA_OUTPUT_DIR}")
        else:
            print(f"  ⚠️  Creando directorio de datos: {Settings.DATA_OUTPUT_DIR}")
            Settings.DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Directorio creado")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error con directorios: {e}")
        return False


def check_modules():
    """Verifica que módulos custom se puedan importar."""
    print("\nVerificando módulos del proyecto...")
    
    modules = [
        ('config', ['Settings', 'ContractBuilder']),
        ('core', ['OrderBook', 'DataValidator']),
        ('storage', ['ParquetWriter']),
        ('utils', ['setup_logging', 'get_logger']),
    ]
    
    all_ok = True
    for module_name, objects in modules:
        try:
            module = __import__(module_name, fromlist=objects)
            for obj in objects:
                if not hasattr(module, obj):
                    print(f"  ✗ {module_name}.{obj} - NO ENCONTRADO")
                    all_ok = False
            if all_ok:
                print(f"  ✓ {module_name} ({', '.join(objects)})")
        except ImportError as e:
            print(f"  ✗ {module_name} - ERROR: {e}")
            all_ok = False
    
    return all_ok


def main():
    """Ejecuta todas las verificaciones."""
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
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Error en verificación '{name}': {e}")
            results.append(False)
    
    # Resumen
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
        print("  3. Si funciona, ejecutar pipeline completo:")
        print("     python main.py")
    else:
        print("\n✗ Algunas verificaciones fallaron")
        print("\n⚠️  Por favor corrige los errores antes de continuar")
        print("\nRecursos:")
        print("  - SETUP_GUIDE.md - Guía de instalación paso a paso")
        print("  - README.md - Documentación completa")
    
    print("\n" + "=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
