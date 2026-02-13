import pandas as pd
import json

def analizar_discrepancia():
    """
    Analiza la discrepancia entre el conteo de empleados activos
    reportado por el cliente vs lo que muestra la plataforma.

    Metodología:
    1. Contar empleados ACTIVOS en Excel original
    2. Contar empleados ACTIVOS en JSON generado
    3. Identificar diferencias
    4. Proponer corrección
    """

    print("="*80)
    print("ANÁLISIS DE DISCREPANCIA - EMPLEADOS ACTIVOS")
    print("="*80)

    # PASO 1: Analizar Excel del cliente
    print("\nPASO 1: Analizando Excel del cliente...")
    df = pd.read_excel('/content/datos_cliente_bpo_soluciones_1.xlsx', sheet_name='Empleados Activos')

    print(f"Total de empleados en Excel: {len(df)}")

    # Ver valores EXACTOS del campo ESTADO (sin normalizar)
    print(f"\nValores en campo ESTADO:")
    print(df['ESTADO'].value_counts())

    # Normalizar para análisis
    df['ESTADO_NORMALIZADO'] = df['ESTADO'].str.upper().str.strip()

    activos_excel = df[df['ESTADO_NORMALIZADO'] == 'ACTIVO']
    inactivos_excel = df[df['ESTADO_NORMALIZADO'] == 'INACTIVO']

    print(f"\nEmpleados ACTIVOS: {len(activos_excel)}")
    print(f"Empleados INACTIVOS: {len(inactivos_excel)}")

    # PASO 2: Analizar JSON generado (lo que ve la plataforma)
    print("\nPASO 2: Analizando JSON generado (plataforma Narah)...")

    with open('empleados_cosmos.json', 'r') as f:
        documentos = json.load(f)

    activos_cosmos = [
        d for d in documentos
        if d.get('infoLaboral', {}).get('estado') == 'ACTIVO'
    ]

    inactivos_cosmos = [
        d for d in documentos
        if d.get('infoLaboral', {}).get('estado') == 'INACTIVO'
    ]

    print(f"Empleados ACTIVOS en plataforma: {len(activos_cosmos)}")
    print(f"Empleados INACTIVOS en plataforma: {len(inactivos_cosmos)}")

    # PASO 3: Identificar discrepancia
    print("\nPASO 3: Identificando discrepancia...")

    discrepancia = len(activos_excel) - len(activos_cosmos)

    if discrepancia == 0:
        print("No hay discrepancia. Conteo coincide.")
    else:
        print(f"       DISCREPANCIA DETECTADA:")
        print(f"      Excel del cliente: {len(activos_excel)} activos")
        print(f"      Plataforma Narah:  {len(activos_cosmos)} activos")
        print(f"      Diferencia:        {abs(discrepancia)} empleado(s)")

    # PASO 4: Buscar la causa raíz
    print("\nPASO 4: Buscando causa raíz...")

    # Posibles causas:
    # 1. Empleado marcado como ACTIVO pero con variación en el texto
    # 2. Empleado con estado NULL/vacío
    # 3. Empleado duplicado

    # Verificar variaciones de "ACTIVO"
    print("\nVerificando variaciones en el texto 'ACTIVO':")
    for valor in df['ESTADO'].unique():
        count = len(df[df['ESTADO'] == valor])
        valor_norm = str(valor).upper().strip()
        if 'ACTIVO' in valor_norm and valor_norm != 'INACTIVO':
            print(f"      '{valor}' (normalizado: '{valor_norm}') -> {count} empleados")

    # Buscar empleados con estado problemático
    estados_validos = ['ACTIVO', 'INACTIVO']
    problematicos = df[~df['ESTADO_NORMALIZADO'].isin(estados_validos)]

    if len(problematicos) > 0:
        print(f"\nEncontrados {len(problematicos)} empleados con estado inválido:")
        print(problematicos[['CEDULA', 'PRIMER NOMBRE', 'PRIMER APELLIDO', 'ESTADO']])

    # PASO 6: Proponer corrección
    print("\n💡 PASO 6: Propuesta de corrección:")
    print("""
    CAUSA PROBABLE:
    - El pipeline normalizó correctamente el campo ESTADO a mayúsculas
    - Si el Excel tenía variaciones como "Activo ", " ACTIVO", etc.,
      el pipeline las corrigió a "ACTIVO"
    - La discrepancia reportada por el cliente puede deberse a que ellos
      cuentan manualmente sin normalizar

    CORRECCIÓN:
    1. Validar con el cliente que sus 78 empleados incluyan SOLO
       registros con estado exactamente = "ACTIVO"
    2. Revisar si hay empleados que ellos consideran activos pero que
       en el Excel están marcados como "INACTIVO"
    3. Si se confirma un error de marcación:
       - Actualizar el Excel
       - Re-ejecutar el pipeline
       - Verificar el conteo

    PREVENCIÓN:
    - Agregar validación al pipeline que reporte empleados con estados
      no estándar
    - Implementar alertas cuando el conteo difiera del esperado
    """)

    return {
        'activos_excel': len(activos_excel),
        'activos_cosmos': len(activos_cosmos),
        'discrepancia': discrepancia
    }

if __name__ == "__main__":
    resultado = analizar_discrepancia()

    print("\n" + "="*80)
    print("📊 RESUMEN")
    print("="*80)
    print(f"Empleados ACTIVOS en Excel:     {resultado['activos_excel']}")
    print(f"Empleados ACTIVOS en Cosmos:    {resultado['activos_cosmos']}")
    print(f"Discrepancia:                   {resultado['discrepancia']}")
    print("="*80)