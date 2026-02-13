import pandas as pd
import json
from datetime import datetime


# Nombres de las hojas del Excel
HOJA_EMPLEADOS = 'Empleados Activos'
HOJA_INCAPACIDADES = 'Incapacidades'
HOJA_EXAMENES = 'Examenes Medicos'

# ID del cliente (fijo para BPO Soluciones)
CLIENTE_ID = 'bpo-soluciones-001'

# PASO 1: CARGAR DATOS DEL EXCEL

archivo_excel = '/content/datos_cliente_bpo_soluciones_1.xlsx'
def cargar_datos(archivo_excel):

    try:
        empleados = pd.read_excel(archivo_excel, sheet_name=HOJA_EMPLEADOS)
        incapacidades = pd.read_excel(archivo_excel, sheet_name=HOJA_INCAPACIDADES)
        examenes = pd.read_excel(archivo_excel, sheet_name=HOJA_EXAMENES)

        print(f"{len(empleados)} empleados cargados exitosamente")
        print(f"{len(incapacidades)} incapacidades cargadas exitosamente")
        print(f"{len(examenes)} exámenes cargados exitosamente")

        return empleados, incapacidades, examenes

    except Exception as e:
        print(f"❌ Error al cargar el Excel: {e}")
        raise


# PASO 2: LIMPIEZA Y NORMALIZACIÓN DE DATOS

def limpiar_texto(texto):
    """
    Normaliza un texto: mayúsculas, sin espacios extra, sin tildes.

    ¿Por qué?
    - Los nombres pueden venir con formato inconsistente
    - Cosmos DB es case-sensitive, necesitamos consistencia
    """
    if pd.isna(texto) or texto == '':
        return None

    # Convertir a string y mayúsculas
    texto = str(texto).upper().strip()

    # Quitar tildes con la librería unicodedata
    import unicodedata
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

    return texto

def limpiar_empleados(df):
    """
    Limpia y valida el DataFrame de empleados.

    Validaciones:
    - Cédula no puede ser nula (es el ID)
    - Textos normalizados a mayúsculas
    """
    # Convertir cédula a string limpio (sin decimales)
    df['CEDULA'] = df['CEDULA'].astype(str).str.split('.').str[0]

    # Eliminar empleados sin cédula
    antes = len(df)
    df = df.dropna(subset=['CEDULA'])
    if len(df) < antes:
        print(f"Eliminados {antes - len(df)} empleados sin cédula")

    # Normalizar textos
    columnas_texto = ['PRIMER NOMBRE', 'SEGUNDO NOMBRE', 'PRIMER APELLIDO',
                      'SEGUNDO APELLIDO', 'CARGO', 'TIPO CONTRATO', 'AREA', 'ESTADO', 'CIUDAD']

    for col in columnas_texto:
        if col in df.columns:
            df[col] = df[col].apply(limpiar_texto)

    print(f"{len(df)} empleados validados")
    return df

def limpiar_incapacidades(df):
    # La columna se llama 'CEDULA EMPLEADO' en esta hoja
    df['CEDULA'] = df['CEDULA EMPLEADO'].astype(str).str.split('.').str[0]
    df = df.dropna(subset=['CEDULA'])

    # Convertir DIAS a número entero
    df['DIAS'] = pd.to_numeric(df['DIAS'], errors='coerce').fillna(0).astype(int)

    print(f"{len(df)} incapacidades validadas")
    return df

def limpiar_examenes(df):

    df['CEDULA'] = df['CEDULA'].astype(str).str.split('.').str[0]
    df = df.dropna(subset=['CEDULA'])

    print(f"{len(df)} exámenes validados")
    return df

# PASO 3: CONSTRUIR DOCUMENTOS COSMOS

def construir_nombres(row):
    """
    Construye el objeto 'nombres' según estructura Cosmos.

    ¿Por qué una función separada?
    - Cada objeto anidado merece su propia función
    - Fácil de testear individualmente
    - Claro qué campos van en cada parte
    """
    return {
        "primerNombre": row.get('PRIMER NOMBRE'),
        "segundoNombre": row.get('SEGUNDO NOMBRE'),
        "primerApellido": row.get('PRIMER APELLIDO'),
        "segundoApellido": row.get('SEGUNDO APELLIDO')
    }

def construir_info_laboral(row):
    """Construye el objeto 'infoLaboral'."""
    return {
        "cargo": row.get('CARGO'),
        "area": row.get('AREA'),
        "fechaIngreso": row.get('FECHA INGRESO'),
        "tipoContrato": row.get('TIPO CONTRATO'),
        "estado": row.get('ESTADO')
    }

def construir_contacto(row):
    """Construye el objeto 'contacto'."""
    return {
        "correo": row.get('CORREO CORPORATIVO'),
        "telefono": str(row.get('TELEFONO', '')) if pd.notna(row.get('TELEFONO')) else None,
        "ciudad": row.get('CIUDAD')
    }

def construir_incapacidad(row):
    """
    Construye un objeto de incapacidad con su diagnóstico anidado.

    Estructura:
    {
      "fechaInicio": "...",
      "diasIncapacidad": 14,
      "diagnostico": {
        "codigoCIE10": "...",
        "descripcion": "..."
      }
    }
    """
    return {
        "fechaInicio": row.get('FECHA INICIO INCAPACIDAD'),
        "fechaFin": row.get('FECHA FIN INCAPACIDAD'),
        "diasIncapacidad": int(row.get('DIAS', 0)),
        "tipoIncapacidad": limpiar_texto(row.get('TIPO INCAPACIDAD')),
        "diagnostico": {
            "codigoCIE10": row.get('DIAGNOSTICO CIE10'),
            "descripcion": limpiar_texto(row.get('DESCRIPCION DIAGNOSTICO'))
        },
        "entidad": limpiar_texto(row.get('ENTIDAD'))
    }

def construir_examen(row):
    """
    Construye un objeto de examen médico.

    Nota sobre RESTRICCIONES:
    - Puede venir como texto separado por comas
    - Lo convertimos a lista
    - Si está vacío, lista vacía []
    """
    restricciones_texto = row.get('RESTRICCIONES', '')

    if pd.isna(restricciones_texto) or restricciones_texto == '':
        restricciones = []
    else:
        # Separar por comas y limpiar
        restricciones = [r.strip() for r in str(restricciones_texto).split(',')]

    return {
        "tipoExamen": row.get('TIPO EXAMEN'),
        "fechaExamen": row.get('FECHA EXAMEN'),
        "resultado": row.get('RESULTADO'),
        "restricciones": restricciones,
        "proximaFecha": row.get('PROXIMA FECHA'),
        "medico": row.get('MEDICO')
    }

def construir_documento_empleado(empleado_row, incapacidades_empleado, examenes_empleado):
    """
    Construye el documento completo de un empleado para Cosmos DB.

    ¿Por qué esta estructura?
    - Cosmos DB necesita un campo 'id' único (usamos cédula)
    - 'clienteId' es la partition key (todos los empleados del mismo cliente)
    - Incapacidades y exámenes van anidados dentro del documento
    """
    cedula = empleado_row['CEDULA']

    # Construir nombre completo
    nombres = [
        empleado_row.get('PRIMER NOMBRE'),
        empleado_row.get('SEGUNDO NOMBRE'),
        empleado_row.get('PRIMER APELLIDO'),
        empleado_row.get('SEGUNDO APELLIDO')
    ]
    # Convertir a string y filtrar valores vacíos/None/nan
    nombre_completo = ' '.join([
        str(n) for n in nombres
        if n and str(n) not in ['None', 'nan', '']
    ]).strip()

    documento = {
        "id": cedula,
        "cedula": cedula,
        "nombres": construir_nombres(empleado_row),
        "nombreCompleto": nombre_completo,
        "infoLaboral": construir_info_laboral(empleado_row),
        "contacto": construir_contacto(empleado_row),
        "clienteId": CLIENTE_ID,
        "tipo": "empleado",
        "fechaCreacion": datetime.now().isoformat() + 'Z',
        "fechaActualizacion": datetime.now().isoformat() + 'Z',
        "incapacidades": incapacidades_empleado,
        "examenesMedicos": examenes_empleado
    }

    return documento

# =============================================================================
# PASO 4: PIPELINE PRINCIPAL
# =============================================================================

def ejecutar_pipeline(archivo_excel, archivo_salida='empleados_cosmos.json'):
    """
    Pipeline completo: Excel -> Cosmos JSON

    Flujo:
    1. Cargar datos
    2. Limpiar y validar
    3. Agrupar incapacidades y exámenes por empleado
    4. Construir documentos
    5. Exportar JSON
    """
    print("="*80)
    print("INICIANDO PIPELINE DE INGESTION")
    print("="*80)

    # PASO 1: Cargar
    empleados, incapacidades, examenes = cargar_datos(archivo_excel)

    # PASO 2: Limpiar
    empleados = limpiar_empleados(empleados)
    incapacidades = limpiar_incapacidades(incapacidades)
    examenes = limpiar_examenes(examenes)

    # PASO 3: Agrupar datos por cédula
    print("\nAgrupando incapacidades y exámenes por empleado...")

    # Crear diccionarios: cedula -> lista de incapacidades/examenes
    incap_por_cedula = {}
    for cedula, grupo in incapacidades.groupby('CEDULA'):
        incap_por_cedula[cedula] = [
            construir_incapacidad(row)
            for _, row in grupo.iterrows()
        ]

    exam_por_cedula = {}
    for cedula, grupo in examenes.groupby('CEDULA'):
        exam_por_cedula[cedula] = [
            construir_examen(row)
            for _, row in grupo.iterrows()
        ]

    # PASO 4: Construir documentos
    print("\nConstruyendo documentos Cosmos...")
    documentos = []

    for _, empleado in empleados.iterrows():
        cedula = empleado['CEDULA']

        # Obtener incapacidades y exámenes (si no hay, lista vacía)
        incapacidades_emp = incap_por_cedula.get(cedula, [])
        examenes_emp = exam_por_cedula.get(cedula, [])

        doc = construir_documento_empleado(empleado, incapacidades_emp, examenes_emp)
        documentos.append(doc)

    # PASO 5: Exportar
    print(f"\nExportando {len(documentos)} documentos a {archivo_salida}...")

    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(documentos, f, indent=2, ensure_ascii=False, default=str)

    print("\n" + "="*80)
    print("✅ PIPELINE COMPLETADO EXITOSAMENTE")
    print("="*80)
    print(f"\n📊 Resumen:")
    print(f"   - Empleados procesados: {len(documentos)}")
    print(f"   - Incapacidades totales: {len(incapacidades)}")
    print(f"   - Exámenes totales: {len(examenes)}")
    print(f"   - Archivo generado: {archivo_salida}")

    return documentos


# =============================================================================
# EJECUCIÓN
# =============================================================================

if __name__ == "__main__":
    # Ruta al archivo Excel
    ARCHIVO_EXCEL = '/content/datos_cliente_bpo_soluciones_1.xlsx'

    # Ejecutar pipeline
    documentos = ejecutar_pipeline(ARCHIVO_EXCEL)

    # Mostrar ejemplo del primer documento
    print("\n📄 Ejemplo del primer documento generado:")
    print(json.dumps(documentos[0], indent=2, ensure_ascii=False))