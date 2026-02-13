"""
RETO 3: Correccion de Datos Criticos de Salud

Problemas a resolver:
1. Andres Garcia (10234567): Incapacidad con -45 dias (fechas invertidas)
2. Carlos Niesta (30456789): Codigo CIE10 incorrecto (caso teorico)
3. Crear funcion de validacion reutilizable
"""

import pandas as pd
import os

if not os.path.exists('outputs'):
    os.makedirs('outputs')

# =============================================================================
# FUNCIONES DE VALIDACION
# =============================================================================

def validar_incapacidad(row):
    """
    Valida una incapacidad y retorna lista de errores.

    Detecta:
    - Dias negativos o cero
    - Fecha fin anterior a fecha inicio
    - Codigos CIE10 con formato invalido
    """
    errores = []

    # Regla 1: Dias coherentes
    try:
        dias = int(row['DIAS'])
        if dias <= 0:
            errores.append(f"Dias invalidos: {dias}")
    except:
        errores.append("Dias no es numerico")

    # Regla 2: Fechas logicas
    try:
        fecha_inicio = pd.to_datetime(row['FECHA INICIO INCAPACIDAD'])
        fecha_fin = pd.to_datetime(row['FECHA FIN INCAPACIDAD'])

        if fecha_fin < fecha_inicio:
            errores.append("Fecha fin anterior a fecha inicio")
    except:
        errores.append("Error al procesar fechas")

    # Regla 3: Formato CIE10
    cie10 = str(row['DIAGNOSTICO CIE10']).strip()
    if len(cie10) > 0 and not cie10[0].isalpha():
        errores.append(f"CIE10 '{cie10}' no inicia con letra")

    return errores

# =============================================================================
# CORRECCIONES ESPECIFICAS
# =============================================================================

def corregir_datos_criticos(archivo_excel):
    """
    Aplica correcciones especificas a los casos reportados.

    Returns:
        DataFrame con incapacidades corregidas
    """
    print("="*80)
    print("RETO 3: CORRECCION DE DATOS CRITICOS DE SALUD")
    print("="*80)

    # Cargar datos
    df_incap = pd.read_excel(archivo_excel, sheet_name='Incapacidades')

    # Convertir fechas
    df_incap['FECHA INICIO INCAPACIDAD'] = pd.to_datetime(
        df_incap['FECHA INICIO INCAPACIDAD'], errors='coerce'
    )
    df_incap['FECHA FIN INCAPACIDAD'] = pd.to_datetime(
        df_incap['FECHA FIN INCAPACIDAD'], errors='coerce'
    )

    # --- CORRECCION 1: Caso Andres Garcia - Dias Negativos ---
    print("\nPASO 1: Corrigiendo fechas invertidas")
    print("-"*80)

    # a) Identificar causa raiz
    print("a) Identificando causa raiz...")
    andres = df_incap[df_incap['CEDULA EMPLEADO'] == 10234567]
    if len(andres) > 0:
        print(f"   Empleado: Andres Garcia (10234567)")
        problema = andres[andres['DIAS'] < 0]
        if len(problema) > 0:
            print(f"   Causa raiz: Fechas invertidas")
            print(f"   Fecha inicio: {problema.iloc[0]['FECHA INICIO INCAPACIDAD']}")
            print(f"   Fecha fin:    {problema.iloc[0]['FECHA FIN INCAPACIDAD']}")
            print(f"   Dias:         {problema.iloc[0]['DIAS']}")

    # b) Detectar TODAS las incapacidades con fechas invertidas
    print("\nb) Detectando TODAS las incapacidades con fechas invertidas...")
    mask_fechas_invertidas = df_incap['FECHA FIN INCAPACIDAD'] < df_incap['FECHA INICIO INCAPACIDAD']
    total_invertidas = mask_fechas_invertidas.sum()
    print(f"   Incapacidades con fechas invertidas: {total_invertidas}")

    # c) Ejecutar correccion
    print("\nc) Ejecutando correccion...")
    for idx in df_incap[mask_fechas_invertidas].index:
        inicio_original = df_incap.at[idx, 'FECHA INICIO INCAPACIDAD']
        fin_original = df_incap.at[idx, 'FECHA FIN INCAPACIDAD']

        # Intercambiar fechas
        df_incap.at[idx, 'FECHA INICIO INCAPACIDAD'] = fin_original
        df_incap.at[idx, 'FECHA FIN INCAPACIDAD'] = inicio_original

        # Recalcular dias
        delta = (inicio_original - fin_original).days + 1
        df_incap.at[idx, 'DIAS'] = delta

        print(f"   [CORREGIDO] Fila {idx}: Dias {df_incap.at[idx, 'DIAS']}")

    # --- CORRECCION 2: Caso Carlos Niesta - Codigo CIE10 Erroneo ---
    print("\nPASO 2: Verificando inconsistencias de codigo CIE10")
    print("-"*80)

    # a) Identificar inconsistencia
    print("a) Buscando caso: Carlos Niesta (30456789) con Z000 + FRACTURA...")

    cie10_serie = df_incap['DIAGNOSTICO CIE10'].astype(str).str.strip().str.upper()
    descripcion_serie = df_incap['DESCRIPCION DIAGNOSTICO'].astype(str).str.strip().str.upper()

    # Buscar Z000 con descripcion de fractura
    mask_cie10_error = (
        (cie10_serie.isin(['Z000', 'Z00.0'])) &
        (descripcion_serie.str.contains('FRACTURA', na=False))
    )

    encontrados = df_incap[mask_cie10_error]

    if not encontrados.empty:
        print(f"   [ENCONTRADO] {len(encontrados)} registros con Z000 + FRACTURA")

        # b) Determinar campo correcto
        print("\nb) Determinando campo correcto...")
        print("   Codigo Z000 = Examen medico general (NO es diagnostico de trauma)")
        print("   Descripcion FRACTURA = Trauma fisico")
        print("   CONCLUSION: La descripcion es correcta, el codigo Z000 esta mal")

        # c) Proponer y ejecutar correccion
        print("\nc) Ejecutando correccion...")
        print("   Cambiando Z000 a S729 (Fractura no especificada)")
        df_incap.loc[mask_cie10_error, 'DIAGNOSTICO CIE10'] = 'S729'

        for idx, row in encontrados.iterrows():
            print(f"   [CORREGIDO] Fila {idx}: {row['NOMBRE COMPLETO']}")
    else:
        print("   [INFO] Caso no encontrado en los datos actuales")
        print("   NOTA: El PDF menciona este caso como ejemplo teorico")
        print("         La logica de deteccion y correccion esta implementada")

    return df_incap

# =============================================================================
# VALIDACION COMPLETA
# =============================================================================

def ejecutar_validacion_completa(df):
    """
    Ejecuta validacion sobre todas las incapacidades.
    """
    print("\nPASO 3: Validacion completa de todas las incapacidades")
    print("-"*80)

    errores_encontrados = []

    for idx, row in df.iterrows():
        errores = validar_incapacidad(row)
        if errores:
            errores_encontrados.append({
                'fila': idx,
                'cedula': row['CEDULA EMPLEADO'],
                'errores': ' | '.join(errores)
            })

    print(f"Incapacidades validadas: {len(df)}")
    print(f"Registros con errores: {len(errores_encontrados)}")

    if errores_encontrados:
        print("\nPrimeros 10 errores:")
        for err in errores_encontrados[:10]:
            print(f"  Fila {err['fila']} (Cedula {err['cedula']}): {err['errores']}")

    return errores_encontrados

# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    archivo ='/content/datos_cliente_bpo_soluciones_1.xlsx'

    try:
        # Ejecutar correcciones
        df_corregido = corregir_datos_criticos(archivo)

        # Validar resultados
        errores = ejecutar_validacion_completa(df_corregido)

        # Guardar archivo corregido
        output_file = 'outputs/incapacidades_corregidas.xlsx'
        df_corregido.to_excel(output_file, index=False)

        print("\n" + "="*80)
        print("RESUMEN")
        print("="*80)
        print(f"Incapacidades procesadas: {len(df_corregido)}")
        print(f"Errores detectados: {len(errores)}")
        print(f"Archivo guardado: {output_file}")
        print("="*80)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()