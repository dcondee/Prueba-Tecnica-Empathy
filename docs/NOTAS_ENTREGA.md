# Notas de Entrega

**Candidato:** Danier Conde
**Fecha:** Febrero 2026  

---

## Estado de Completitud por Reto

### RETO 1: Pipeline de Ingestión
**Estado: COMPLETO (100%)**

Todos los puntos solicitados:
- [x] Lectura de 3 hojas de Excel
- [x] Limpieza y normalización de datos
- [x] Validación de cédulas únicas
- [x] Construcción de documentos JSON con estructura anidada
- [x] Manejo de campos opcionales
- [x] Robustez ante datos faltantes
- [x] Exportación de JSON listo para Cosmos DB

**Tiempo invertido:** ~2 horas

---

### RETO 2: Debugging de Discrepancia
**Estado: COMPLETO (100% con enfoque Python)**

El PDF indica:
> "Escribir la consulta o codigo que usarias para encontrar el registro 
> faltante en una base Cosmos DB real (puedes escribirla en SQL de Cosmos 
> o en Python)."

**Decisión:** Opte por implementar el analisis 100% en Python usando pandas.

**Razón de la decisión:**

1. **Flexibilidad:** Python permite debugging iterativo más rápido
2. **Accesibilidad:** No requiere acceso a una instancia de Cosmos DB
3. **Completitud:** El análisis en Python cumple el objetivo del reto
4. **Preferencia técnica:** Para investigación de datos, pandas es más ágil que SQL

**Lo que implementé:**
- [x] Análisis comparativo Excel vs JSON
- [x] Conteo de empleados por estado
- [x] Identificación de variaciones en el texto "ACTIVO"
- [x] Búsqueda de registros problemáticos
- [x] Metodología documentada paso a paso

**Lo que no implemente:**
- [ ] Queries SQL de Cosmos DB

**Justificacion:** Consideré que al implementar el análisis completo en Python, 
cumplía con el espíritu del reto (identificar la discrepancia) sin necesidad 
de las queries SQL, que interprete como un "plus" opcional.

**Tiempo invertido:** ~1.5 hora

---

### RETO 3: Corrección de Datos Críticos
**Estado: COMPLETO (90%)**

**Lo que implementé:**

Caso 1 - Andres Garcia:
- [x] Identificación de causa raíz (fechas invertidas)
- [x] Código para detectar TODAS las incapacidades con fechas invertidas
- [x] Corrección automática aplicada
- [x] Validación post-corrección

Caso 2 - Carlos Niesta:
- [x] Búsqueda del caso en los datos
- [x] Lógica de detección implementada
- [x] Documentación de que el caso no existe en los datos reales

Función de validación:
- [x] Detección de días negativos o cero
- [x] Detección de fecha fin anterior a fecha inicio
- [x] Validación de formato CIE10
- [x] Función probada y funcional

**Lo que no implementé:**
- [ ] Integración de la funcion de validación al pipeline del Reto 1

**Razon:** Limitaciones de tiempo. La función esta lista y funcional, 
pero no la integré directamente en el código del pipeline del Reto 1.

**Cómo se integraría** (conceptualmente):

```python
def limpiar_incapacidades_con_validacion(df):
    # Limpieza basica del Reto 1
    df['CEDULA'] = df['CEDULA EMPLEADO'].astype(str).str.split('.').str[0]
    df = df.dropna(subset=['CEDULA'])
    
    # VALIDACION del Reto 3 (AGREGAR AQUI)
    errores_totales = 0
    for idx, row in df.iterrows():
        errores = validar_incapacidad(row)  # Funcion del Reto 3
        if errores:
            errores_totales += 1
            print(f"Advertencia fila {idx}: {', '.join(errores)}")
    
    if errores_totales > 0:
        print(f"\nSe detectaron {errores_totales} registros con errores")
    
    return df

# Uso en el pipeline:
# incapacidades = limpiar_incapacidades_con_validacion(incapacidades)
```

**Impacto de no tener la integración:**
- La función de validación existe y funciona
- Se puede usar de forma standalone
- Solo falta "conectarla" al pipeline existente
- Es un cambio de ~10 lineas de codigo

**Tiempo invertido:** ~2 horas

---

## Decisiones Técnicas Destacadas

### 1. Codigo Simple vs Código Sofisticado

**Decisión:** Priorice simplicidad y legibilidad sobre abstracciones complejas

**Ejemplo:**
```python
# Evite sobre-ingenieria
# (mapeos complejos, clases abstractas, patrones de diseño innecesarios)

# Preferi codigo directo
def limpiar_empleados(df):
    df['CEDULA'] = df['CEDULA'].astype(str).str.split('.').str[0]
    return df
```

**Razón:** En equipos reales, el código debe ser mantenible por cualquier 
miembro, no solo por el autor original.

### 2. Funciones Pequeñas

**Decisión:** Una función, una responsabilidad

**Ventaja:** Si cambia un requerimiento (ej: formato de nombres), 
solo modificas UNA funcion, no todo el sistema.

### 3. Validación Temprana

**Decisión:** Detectar errores al inicio del pipeline, no al final

**Razón:** Mejor fallar rápido con mensaje claro que procesar todo 
y descubrir el error al intentar cargar a Cosmos DB.

---

## Reflexión sobre el Proceso

### Lo que salió bien

1. **Pipeline robusto:** Funciona con datos reales, maneja casos extremos
2. **Código limpio:** Fácil de leer y modificar
3. **Documentación:** Expliqué el "por qué" de cada decisión
4. **Metodología:** Abordaje sistemático de cada problema

### Desafíos enfrentados

1. **Tiempo limitado:** Balance entre estudios y prueba técnica
2. **Datos incompletos:** Caso Carlos Niesta no existe (maneje como caso teorico)
3. **Priorización:** Decidí completar lo fundamental antes que pulir detalles

### Lo que haría diferente con más tiempo

1. **Testing automatizado:**
   ```python
   def test_pipeline_con_datos_faltantes():
       # Probar con empleado sin incapacidades
       # Probar con incapacidad sin examenes
       # etc.
   ```

2. **Integración completa Reto 3 → Reto 1**
   - Pipeline con validación incorporada
   - Alertas configurables

3. **Queries SQL de Cosmos DB**
   - Aunque Python cumple el objetivo
   - Las queries SQL serian un plus

---


**Fecha de entrega:** Febrero 12, 2026  
**Ultima revision:** Febrero 12, 2026, 23:00
