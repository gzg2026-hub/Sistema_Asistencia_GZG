# REGLAS OBLIGATORIAS DEL PROYECTO SISTEMA DE ASISTENCIA GZG

---

## 1. REGLA DE EXCEPCIÓN Y DESVINCULACIÓN TOTAL DE GOOGLE DRIVE
- **Cero Sincronización Local en PC**: La carpeta del proyecto en el disco local (`c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\`) está **100% desvinculada de Google Drive Desktop** (PROHIBIDO totalmente usar, copiar o vincular con la unidad `G:\` o carpetas de sincronización local de Windows).
- **Cero Subidas en Sesiones Interactivas**: Durante conversaciones, pruebas manuales o ejecuciones interactivas con el usuario, **NUNCA se sube nada a Google Drive**.
- **Subida Única en Tarea Automática Programada de 9:00 AM (Vía API Nube)**:
  - ÚNICAMENTE la tarea programada automática de las 9:00 AM (`scripts/schedule_downloader.py`) subirá mediante **API directa en la nube** (sin carpetas locales `G:\`) los siguientes **2 archivos autorizados** directamente en la raíz de la carpeta `AGOSTO`:
    1. `Transacciones_Acumuladas.xlsx` *(Maestro Acumulado de Marcaciones Crudas de HikCentral)*.
    2. `Reporte_Asistencia_GZG_YYYY-MM-DD.xlsx` *(Reportes Diarios Procesados de Días Cerrados)*.
- **PROHIBIDO TOTALMENTE EN DRIVE**:
  - NO crear subcarpetas como `Data_Cruda` o `Data_Procesada` en Google Drive.
  - `Sistema_Asistencia_GZG_v1.0.xlsx` *(Archivo raíz ejecutable en la PC, NUNCA se sube a Drive)*.
  - Cualquier otro archivo temporal, borrador o consolidado parcial.

---

## 2. PRESERVACIÓN DE DATA CRUDA REAL DEL BIOMÉTRICO
- En los archivos de data cruda (`Transacciones_Acumuladas.xlsx`), se deben mantener **los valores reales exactos** exportados por el biométrico HikCentral (`Registro de entrada`, `Registrar salida`, `Imagen de cara`, `Huella dactilar`, departamentos y cargos reales).
- Queda prohibido hardcodear o inventar valores por defecto (como "MINA", "OPERATIVO", "Semana 34", "Marcación", "Rostro").

---

## 3. LÓGICA DE DEDUCCIÓN E INTELIGENCIA ARTIFICIAL EN EL MOTOR DE ASISTENCIA
La lógica de deducción e Inteligencia Artificial se aplica **únicamente en el motor de cálculo de asistencia** (`core/attendance_engine.py`), sin alterar el texto original de la data cruda:

- **Ventana de Contexto Temporal Universal (Día Anterior, Día Actual y Día Posterior)**:
  * El motor analiza de forma continua la secuencia cronológica completa del trabajador (evaluando marcaciones del día anterior, día en curso y día posterior) para emparejar lógicamente entradas y salidas en turnos rotativos y de medianoche.
- **Deducción Universal de Error Humano en Marcación (Caso Jhon Ágreda y similar para todo el personal)**:
  * Si un trabajador presenta una marcación matutina (05:00 AM a 09:30 AM) etiquetada como `"Inicio de horas extra"` o `"Inicio H.E."`, y posteriormente registra una salida en la tarde/noche (19:00 a 20:30 PM) sin existir otra entrada matutina previa ni marcación de fin de H.E., el motor deduce un **error humano de botón/estado en la terminal biométrica**.
  * Dicha marcación se reclasifica automáticamente en la evaluación como `"Registro de entrada"`, asignándole el **Turno DÍA** y evaluando el día limpiamente como `ASISTIO`.
- **Asignación Universal de Turnos (DÍA / NOCHE / MANTENIMIENTO)**:
  * **Turno DÍA**: Entrada 07:00 AM (tolerancia hasta 07:15 AM). Salida 19:00 PM (12 Horas de Turno).
  * **Turno NOCHE**: Entrada 19:00 PM (tolerancia hasta 19:15 PM). Salida 07:00 AM del día siguiente (12 Horas de Turno).
  * **Mantenimiento / Operaciones**: Evaluación adaptativa de jornadas según catálogo de personal.
- **Doble Turno / Doble Entrada en el Mismo Día**:
  * Si un trabajador tiene 2 marcaciones de entrada el mismo día calendárico (doble turno / reingreso), se procesan ambos registros de forma independiente y se sombrea la fila en durazno pastel.
- **Filtro de Filas Fantasma / Sin Marcación (Regla Punto 9)**:
  * Se eliminan automáticamente de la vista procesada las filas donde tanto la Entrada (Fecha/Hora) como la Salida (Fecha/Hora) sean nulas, vacías o `NaN`.

---

## 4. ESTILOS Y FORMATO DEL REPORTE EXCEL EXPORTADO (`data/exporter.py`)
- **Estructura**: 23 Columnas (A a W).
- **Encabezados Corporativos**:
  * Azul Oscuro (`#1F4E78`) con texto blanco para columnas A a P (Datos generales y marcaciones).
  * Azul Claro (`#2F5597`) con texto blanco para columnas Q a U (Cálculos de Horas de Turno, Tardanzas, Excesos y Horas Extras).
- **Sombreado Pastel de Incidencias**:
  * **Durazno Pastel (`#FCE4D6`)**: Faltas, Pendientes, Sin Registro, Salidas Anticipadas y Doble Turno (doble entrada el mismo día).
  * **Sin Relleno (Blanco)**: Cambio de Guardia, Jornada Parcial y asistencias normales.
- **Formato de Celdas**:
  * Columna A (DNI): Formateada como Texto (`@`) para conservar ceros a la izquierda.
  * Horas trabajadas, tardanzas y excesos: Formateadas estrictamente en `HH:MM`.
