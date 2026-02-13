# Prueba Técnica - Data Scientist
## Empathy Soluciones Corporativas S.A.S.

**Candidato:** Danier Conde  
**Fecha de entrega:** Febrero 2026  
**Posición:** Full Stack Data Scientist  
**Plataforma:** Narah - Gestion de Salud Ocupacional

---

## Contexto

Esta prueba técnica aborda tres desafíos reales del procesamiento de datos de salud ocupacional en la plataforma Narah:

1. **Pipeline de Ingesta:** Transformar datos del cliente (Excel) a formato Cosmos DB (JSON)
2. **Debugging:** Identificar discrepancia en conteo de empleados activos
3. **Calidad de Datos:** Detectar y corregir errores críticos en registros de salud
---

## Estructura del Repositorio

```
prueba-tecnica-empathy/
├── README.md                                    # Este archivo
├── Solución_PruebaTecnica_Empathy.ipynb        # Notebook con soluciones
├── datos_cliente_bpo_soluciones_1.xlsx         # Datos de entrada
├── reto1_pipeline.py                           # Pipeline de ingesta
├── reto2_debugging.py                          # Analisis de discrepancia
├── reto3_correccion.py                         # Validacion y correccion
├── outputs/
│   ├── empleados_cosmos.json                   # JSON generado (300 empleados)
│   └── incapacidades_corregidas.xlsx          # Excel con correcciones
└── docs/
    ├── DECISIONES_DISENO.md                    # Por que tome cada decision
    └── NOTAS_ENTREGA.md                        # Alcance y limitaciones
```

---

## Entregables

### 1. Notebook Jupyter (`Solución_PruebaTecnica_Empathy.ipynb`)

**Formato preferido para revision rapida**

Contiene:
- Código ejecutable de los 3 retos
- Explicaciones en Markdown
- Salidas de ejecucion
- Ejemplos de resultados

**Cómo ejecutar:**
```bash
jupyter notebook Cuaderno_respuestas.ipynb
# Ejecutar todas las celdas: Cell > Run All
```

### 2. Scripts Python Standalone

Para ejecución independiente:

```bash
# Reto 1: Pipeline de ingesta
python reto1_pipeline.py
# Output: outputs/empleados_cosmos.json

# Reto 2: Analisis de discrepancia
python reto2_debugging.py
# Output: Analisis en consola

# Reto 3: Correccion de datos
python reto3_correccion.py
# Output: outputs/incapacidades_corregidas.xlsx
```

### 3. Archivos de Salida

- `outputs/empleados_cosmos.json` - 300 documentos listos para Cosmos DB
- `outputs/incapacidades_corregidas.xlsx` - Excel con fechas corregidas

---

## Soluciones por Reto

### RETO 1: Pipeline de Ingestión

**Objetivo:** Transformar Excel (3 hojas) → JSON (estructura anidada para Cosmos DB)

**Implementación:**
- Pipeline modular con funciones de responsabilidad unica
- Limpieza y normalización de textos (mayusculas, sin tildes)
- Validación de cedulas (campo obligatorio)
- Construcción de documentos con incapacidades y exámenes anidados
- Manejo robusto de datos faltantes

**Resultado:**
- 300 empleados procesados
- 526 incapacidades agrupadas por empleado
- 473 exámenes medicos agrupados por empleado
- JSON válido para carga en Cosmos DB

**Código:** `reto1_pipeline.py` o Notebook celda 2-6

---

### RETO 2: Debugging - Discrepancia de Empleados

**Problema reportado:** Cliente dice tener 78 empleados activos, plataforma muestra 77

**Metodología aplicada:**

1. **Análisis en Excel del cliente**
   - Conteo: 289 empleados con estado ACTIVO
   - Conteo: 11 empleados con estado INACTIVO

2. **Análisis en JSON generado**
   - Conteo: 289 empleados ACTIVO
   - Los conteos coinciden

3. **Búsqueda de causa raiz**
   - Revisión de variaciones en el texto "ACTIVO"
   - Validación de normalización del pipeline
   - No se encontró discrepancia en los datos actuales

**Conclusión:** 
En los datos proporcionados no existe la discrepancia reportada (78 vs 77). 
La metodología implementada permite detectar este tipo de problemas:
- Comparación entre fuente original y datos procesados
- Identificación de registros con estados no estandar
- Análisis de normalizacion de textos

**Nota sobre queries SQL:**
El PDF indica que se puede usar "SQL de Cosmos o Python". Opte por **analisis 100% en Python** 
usando pandas, que permite debugging más rápido y es más fácil de iterar durante la investigación.

**Código:** `reto2_debugging.py` o Notebook celda 7-8

---

### RETO 3: Corrección de Datos Críticos de Salud

**Problemas identificados:**

#### Caso 1: Andres Garcia (Cedula 10234567)
- **Error:** Incapacidad con -45 dias
- **Causa raiz:** Fechas invertidas (inicio posterior a fin)
- **Datos originales:**
  - Fecha inicio: 2024-10-01
  - Fecha fin: 2024-09-17
  - Dias: -45
- **Corrección aplicada:**
  - Fecha inicio: 2024-09-17
  - Fecha fin: 2024-10-01
  - Dias: 15

#### Caso 2: Carlos Niesta (Cedula 30456789)
- **Estado:** Este caso NO existe en los datos proporcionados
- **Interpretación:** El PDF lo menciona como ejemplo teorico
- **Lógica implementada:** El codigo detectaría este tipo de inconsistencias (Z000 + descripcion de fractura) si existieran

**Funcion de validación creada:**

```python
def validar_incapacidad(row):
    """
    Detecta:
    - Dias negativos o cero
    - Fecha fin anterior a fecha inicio  
    - Codigos CIE10 con formato invalido
    """
```

**Resultado:**
- 526 incapacidades validadas
- 1 registro corregido (Andres Garcia)
- 0 errores restantes tras correccion

**Código:** `reto3_correccion.py` o Notebook celda 9-11

---

## Decisiones de Diseño

### Por qué código simple sobre codigo sofisticado

Priorice **mantenibilidad** sobre **sofisticacion tecnica**:

```python
# Evite esto (complejo):
COL_MAP = {'CEDULA': 'cedula', 'PRIMER NOMBRE': 'primerNombre', ...}
df.rename(columns=COL_MAP)

# Preferi esto (directo):
empleado.get('PRIMER NOMBRE')
```

**Razón:** Un nuevo miembro del equipo puede entender y modificar el codigo en minutos.

### Una función, una responsabilidad

Cada función hace UN trabajo específico:
- `limpiar_empleados()` - Solo limpia empleados
- `construir_nombres()` - Solo construye objeto "nombres"
- `validar_incapacidad()` - Solo valida una incapacidad

**Ventaja:** Si cambia un requerimiento, solo modificas UNA funcion.

### Validación temprana

```python
# Detectar problemas INMEDIATAMENTE
df = df.dropna(subset=['CEDULA'])  # Cedula obligatoria
```

No esperar a que llegue a Cosmos DB para descubrir errores.

**Ver detalles completos:** `docs/DECISIONES_DISENO.md`

---

## Alcance y Limitaciones

### Lo que está completo

- Pipeline de ingesta funcional y probado
- Análisis de discrepancia con metodologia clara
- Detección y corrección de errores críticos
- Función de validación reutilizable
- Código documentado y bien estructurado

### Lo que no alcanzó por tiempo

**Integración de validación al pipeline (Reto 3, punto 4):**

El PDF pide: "Agregar esta función al pipeline del Reto 1 como capa de validación antes de la carga a Cosmos."

**Estado:** La función `validar_incapacidad()` esta implementada y probada, pero no la integré 
directamente en el pipeline del Reto 1.

**Razón:** Limitaciones de tiempo debido a compromisos académicos concurrentes.

**Cómo se integraría** (concepto):
```python
def limpiar_incapacidades(df):
    # Limpieza basica...
    
    # AGREGAR: Validacion antes de continuar
    for idx, row in df.iterrows():
        errores = validar_incapacidad(row)
        if errores:
            print(f"Advertencia en fila {idx}: {errores}")
    
    return df
```

**Ver código de ejemplo:** `docs/NOTAS_ENTREGA.md`

---

## Tecnologías Utilizadas

- **Python 3.x**
- **pandas** - Manipulacion de datos
- **openpyxl** - Lectura/escritura de Excel
- **json** - Generacion de documentos JSON
- **Jupyter Notebook** - Documentacion ejecutable

---

## Cómo Ejecutar

### Requisitos

```bash
pip install pandas openpyxl jupyter
```

### Opción 1: Notebook (Recomendado)

```bash
jupyter notebook Cuaderno_respuestas.ipynb
# Ejecutar todas las celdas
```

### Opción 2: Scripts Individuales

```bash
# Asegurar que el Excel este en el mismo directorio
python reto1_pipeline.py
python reto2_debugging.py
python reto3_correccion.py
```

---

## Resultados

### Métricas

| Métrica | Valor |
|---------|-------|
| Empleados procesados | 300 |
| Incapacidades procesadas | 526 |
| Examenes medicos procesados | 473 |
| Empleados ACTIVOS | 289 |
| Empleados INACTIVOS | 11 |
| Errores criticos detectados | 1 |
| Errores criticos corregidos | 1 |
| Tiempo de ejecucion pipeline | < 5 segundos |

### Calidad de Datos

- 100% de empleados tienen cédula valida
- 100% de incapacidades tienen fechas coherentes (tras correccion)
- 0% de dias negativos en incapacidades (tras correccion)

---

## Reflexiones

### Lo que aprendí

1. **Datos de salud requieren validación rigurosa**
   - Un error de -45 dias puede afectar pagos de incapacidades
   - Codigos CIE10 incorrectos afectan decisiones médicas

2. **Normalización es crítica**
   - "ACTIVO" ≠ " Activo " ≠ "activo" en bases de datos
   - La limpieza de textos debe ser consistente

### Lo que haría con más tiempo

1. **Testing automatizado**
   ```python
   def test_validar_incapacidad_dias_negativos():
       row = {'DIAS': -45, ...}
       errores = validar_incapacidad(row)
       assert 'Dias invalidos' in errores[0]
   ```

2. **Integración completa Reto 1 + Reto 3**
   - Pipeline con validación incorporada
   - Alertas automaticas de errores

3. **Logging estructurado**
   - Trazabilidad de cada registro procesado
   - Métricas de calidad por ejecución

4. **Configuracion externalizada**
   ```yaml
   validation_rules:
     dias_min: 1
     dias_max: 365
     allow_z_codes_in_disabilities: false
   ```

---

## Contacto

Para cualquier duda o aclaración sobre las soluciones:

**Email:** cdanier@uninorte.edu.co  
---
