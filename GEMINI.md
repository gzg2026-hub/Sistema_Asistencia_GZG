# REGLAS OBLIGATORIAS DEL PROYECTO SISTEMA DE ASISTENCIA GZG

---

## 1. REGLA DE EXCEPCIÓN Y DESVINCULACIÓN TOTAL DE GOOGLE DRIVE
- **Cero Sincronización Local en PC**: La carpeta del proyecto en el disco local (`c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\`) está **100% desvinculada de Google Drive Desktop** (PROHIBIDO totalmente usar, copiar o vincular con la unidad `G:\` o carpetas de sincronización local de Windows).
- **Cero Subidas en Sesiones Interactivas**: Durante conversaciones, pruebas manuales o ejecuciones interactivas con el usuario, **NUNCA se sube ni se actualiza nada a Google Drive, ÚNICAMENTE SE HARÁ A LA ORDEN O CONFIRMACIÓN EXPLÍCITA DEL USUARIO**.
- **Cero Regeneraciones o Subidas durante Modificaciones de Código**: Al editar código fuente, componentes o estilos, queda estrictamente prohibido ejecutar scripts de regeneración de bases de datos o forzar subidas a Google Drive de forma proactiva. Toda regeneración o subida manual se ejecuta ÚNICAMENTE bajo orden explícita y textual del usuario.
- **Archivos Autorizados para Google Drive (3 en Total)**:
  - **Subida Automática 9:00 AM** (`scripts/schedule_downloader.py`) → Carpeta raíz `AGOSTO` en Drive:
    1. `Transacciones_Acumuladas.xlsx` *(Maestro Acumulado de Marcaciones Crudas de HikCentral)*.
    2. `Reporte_Asistencia_GZG_YYYY-MM-DD.xlsx` *(Reportes Diarios Procesados de Días Cerrados)*.
  - **Subida Inmediata Triggered** (cada vez que un aprobador valida/rechaza en el app móvil) → Misma carpeta `AGOSTO` en Drive:
    3. `Aprobaciones_GZG_YYYY-MM.xlsx` *(Registro mensual de HE y Excesos de Jornada con estados de aprobación N1/N2)*. La subida ocurre en un **hilo background** para no bloquear la UI del app. Sin horario fijo: se actualiza en Drive en el momento exacto en que se registra la acción.
  - **Definición Estricta de Día Cerrado (Regla de 9:00 AM)**: Un día calendárico (ej. día 22) se considera **Día Cerrado** ÚNICAMENTE a partir de la ejecución automática de las 9:00 AM del día posterior (ej. día 23 a las 9:00 AM). Antes de las 9:00 AM del día posterior, el día se considera EN CURSO. Queda estrictamente PROHIBIDO emitir el reporte diario individual antes de las 9:00 AM del día siguiente.
- **Ubicaciones Exclusivas Locales de Reportes**:
  - Reportes diarios: `downloads/data_procesada/diario/Reporte_Asistencia_GZG_YYYY-MM-DD.xlsx`
  - Excel de Aprobaciones: `downloads/data_procesada/Aprobaciones_GZG_YYYY-MM.xlsx`
  - Queda estrictamente PROHIBIDO generar o dejar reportes sueltos en la raíz del proyecto o subcarpetas no autorizadas.
- **PROHIBIDO TOTALMENTE EN DRIVE**:
  - NO crear subcarpetas como `Data_Cruda` o `Data_Procesada` en Google Drive.
  - `Sistema_Asistencia_GZG_v1.0.xlsx` *(Archivo raíz ejecutable en la PC, NUNCA se sube a Drive)*.
  - Cualquier otro archivo temporal, borrador o consolidado parcial.

---

## 2. PRESERVACIÓN DE DATA CRUDA REAL DEL BIOMÉTRICO
- En los archivos de data cruda (`Transacciones_Acumuladas.xlsx`), se deben mantener **los valores reales exactos** exportados por el biométrico HikCentral (`Registro de entrada`, `Registrar salida`, `Imagen de cara`, `Huella dactilar`, departamentos y cargos reales).
- **Integridad Estricta de Marcaciones 1-a-1**: El total de marcaciones en `Transacciones_Acumuladas.xlsx` debe ser un reflejo EXACTO del 100% de transacciones de HikCentral Web (ejemplo: 533 en Web = 533 en Excel). Queda estrictamente prohibido usar parsers que descarten o silencien archivos descargados con encabezados nativos (`DNI`, `APELLIDOS`, `NOMBRES`, `FECHA`, `HORA`, `DISPOSITIVO`, `TIPO`).
- **Multi-Alias de Encabezados en Lectura**: Toda lectura o parseo de Excel en `data/data_loader.py` debe soportar explícitamente tanto el formato formateado (`ID`, `Tiempo`) como el formato nativo descargado de HikCentral (`DNI`, `HORA`, `DISPOSITIVO`, `TIPO`).
- **Descarga Robusta con Espera Activa y Reintentos (`core/hikvision_downloader.py`)**:
  * La extracción de transacciones de HikCentral debe utilizar espera activa de red (`networkidle`) y bucle de reintentos (mínimo 3 intentos) con validación de registros no vacíos, asegurando la captura integral de entradas, salidas y transacciones de medianoche antes de emitir los reportes diarios de días cerrados.
  * Queda prohibida la sobreescritura de data cruda acumulada con archivos desfasados o incompletos de carpetas externas.
- Queda prohibido hardcodear o inventar valores por defecto (como "MINA", "OPERATIVO", "Semana 34", "Marcación", "Rostro").

---

## 3. LÓGICA DE DEDUCCIÓN E INTELIGENCIA ARTIFICIAL EN EL MOTOR DE ASISTENCIA
La lógica de deducción e Inteligencia Artificial se aplica **únicamente en el motor de cálculo de asistencia** (`core/attendance_engine.py`), sin alterar el texto original de la data cruda:

- **Ventana de Contexto Temporal Universal (Día Anterior, Día Actual y Día Posterior)**:
  * El motor analiza de forma continua la secuencia cronológica completa del trabajador (evaluando marcaciones del día anterior, día en curso y día posterior) para emparejar lógicamente entradas y salidas en turnos rotativos y de medianoche.
- **Búsqueda Cruzada Universal de Medianoche (Candado Estricto Anti-Robo de Salidas en D+1)**:
  * Sin importar si el trabajador pertenece a Turno DÍA o Turno NOCHE, si ingresa el día D y no registra marcación de salida durante ese mismo día calendárico, pero registra una salida en la madrugada/mañana del día D+1 (hasta las 12:00 PM) **ESTRICTAMENTE ANTES DE CUALQUIER MARCACIÓN DE ENTRADA REGISTRADA EN EL DÍA D+1**, el motor vincula automáticamente esa salida como el término oficial de la jornada del día D.
  * Si en el día D+1 existe una entrada previa a dicha salida (ej. José Moncada con entrada 02:19 AM y salida 06:46 AM en D+1), esa salida pertenece incondicionalmente a la jornada de D+1 y NUNCA puede ser tomada por el día D, evitando turnos falsos de más de 24 horas y efectos dominó.
  * Aplica tanto para turnos de noche normales (ej. 19:00 PM a 07:00 AM) como para jornadas prolongadas/horas extras de Turno DÍA que concluyen pasada la medianoche (ej. Entrada 06:33 AM día D → Salida 00:38 AM día D+1, contabilizando 17:38 hrs trabajadas).
- **Deducción Universal de Error Humano en Marcación**:
  * **Botón H.E. Matutino (Caso Jhon Ágreda / Raúl Lázaro / Jhon Alva / Ederly Suárez)**: Si un trabajador presenta una marcación matutina (05:00 AM a 09:30 AM) etiquetada como `"Inicio de horas extra"`, `"Inicio H.E."`, `"Fin de horas extra"` o `"Fin H.E."`, el motor deduce error humano de botón y reclasifica a `"Registro de entrada"` **ÚNICAMENTE si NO existe ninguna entrada matutina explícita en el día y NO existe un "Inicio de horas extra" previo en la madrugada**.
  * Si el trabajador cuenta con un `Inicio de horas extra` en la madrugada (ej. 02:42 AM), `Fin de horas extra` a las 06:41 AM y `Registro de entrada` a las 06:42 AM, el motor preserva el bloque real de Horas Extras matutino y evalúa el Turno Día limpiamente sin generar observaciones de "Entrada duplicada".
  * **Botón de Entrada al Salir del Turno Día (Caso Clari Tocto)**: Si un trabajador registra una entrada matutina (05:00 a 08:30 AM) y luego una marcación en la tarde/noche (17:00 a 20:30 PM) etiquetada por error como `"Registro de entrada"`, y no existen salidas intermedias en la tarde ni salida nocturna en la madrugada del día siguiente (D+1), o si el trabajador es personal Administrativo, el motor deduce **error de botón al salir**. Se reclasifica la segunda marcación como `"Registrar salida"`, evitando duplicar filas falsas con `00:00` y evaluando la jornada de 12 horas en Turno DÍA como `ASISTIO`.
- **Sesión Única de Horas Extras en el Día (Caso Yencli Ordoñez / Raúl Espinoza / Jhon Alva)**:
  * Si un trabajador realiza una sola sesión de Horas Extras en el día (ya sea en la mañana antes del turno o en la noche después del turno), **permanece en la misma fila única del Turno Día**, completando las columnas `Inicio H.E.`, `Fin H.E.` y sumando sus `Horas Extras (HH:MM)` sin generar filas adicionales falsas.
- **Múltiples Sesiones de Horas Extras Diarias (Caso Bryan Cruz / Alan Rojas)**:
  * ÚNICAMENTE cuando el trabajador realiza **dos o más sesiones independientes de Horas Extras en el mismo día calendárico** (ej. sesión 1 de madrugada 01:26 a 06:42 y sesión 2 de noche 22:50 a 06:57 del día siguiente), el motor divide la jornada en sub-bloques independientes:
    - **Fila 1 (Turno Día + H.E. Previa)**: Refleja el Turno Día con sus horas trabajadas y su primera sesión matutina de H.E. (ej. Turno Día 12:08 con H.E. matutina 05:16).
    - **Fila 2 (Segundo Bloque Adicional H.E.)**: Cada bloque adicional o nocturno genera su **propia fila asignada estrictamente a la fecha calendárica en que inició la labor**, con `00:00` en horas de turno y la duración exacta en Horas Extras (ej. 08:07 H.E.). Queda prohibido dividir filas cuando el trabajador realiza una sola sesión de H.E. en el día.
- **Asignación Universal de Turnos (DÍA / NOCHE / MANTENIMIENTO)**:
  * **Turno DÍA**: Entrada 07:00 AM (tolerancia hasta 07:15 AM). Salida 19:00 PM (12 Horas de Turno).
  * **Turno NOCHE**: Entrada 19:00 PM (tolerancia hasta 19:15 PM). Salida 07:00 AM del día siguiente (12 Horas de Turno).
  * **Regla de Mantenimiento**: Aplica para el personal cuyo cargo contenga la palabra "Mantenimiento" y para **Josmell Waldir Huayama Adriano (DNI `46671923` - Jefe de Mantenimiento)**. Si la entrada ocurre antes de las 06:25 AM, se considera su marcación real de entrada. Si ingresa entre las 06:25 AM y 07:00 AM, su inicio oficial se ajusta a las 07:00 AM.
  * **Lógica de Cambio de Guardia y Previos de Turno (Ciclos de 10 Días - ej. 20 de Agosto)**:
    - El cambio oficial de guardia ocurre cada 10 días e involucra únicamente a un grupo/cuadrilla específica (el resto del personal mantiene su horario normal 07:00-19:00 / 19:00-07:00).
    - **Turno Previo Noche (1-2 días antes del cambio)**: 19:00 PM a 05:00 AM del día siguiente (10 Horas). Permite que el turno entrante empiece a las 05:00 AM.
    - **Turno Día en Cambio de Guardia**: 05:00 AM a 17:00 PM (12 Horas). Aplica para el personal que baja de turno para salir temprano.
    - **Turno Noche en Cambio de Guardia**: 17:00 PM a 07:00 AM del día siguiente (14 Horas). Aplica para el personal que recupera las 2 horas del previo noche.
    - **Tolerancia y Exceso**: Mantener 15 min de tolerancia en entrada/salida para estos horarios. NO considerar Exceso de Jornada en Cambios de Guardia, pero SÍ registrar Horas Extras si hay marcación explícita de biométrico.
    - **Etiquetado y Sombreado Obligatorio**: Todo registro evaluado como Cambio de Guardia o Relevo en ventana de transición (04:30-06:00 AM / 16:30-18:00 PM) debe etiquetarse explícitamente como `"Cambio de guardia"` en la columna **Tipo de Registro** (Columna V), garantizando su sombreado automático en **Durazno Pastel (`#FCE4D6`)** en el reporte exportado.
  * **Lógica de Media Jornada (Jornada Parcial)**:
    - **Horarios Oficiales**: 07:00 AM a 13:00 PM (Turno Mañana) y 13:00 PM a 19:00 PM (Turno Tarde).
    - Aplica únicamente para personal en cambio de guardia o que ingresa/retorna de sus días libres (Régimen 20x10 u otros).
  * **Regla de Exceso de Jornada**: Se reporta únicamente cuando las horas trabajadas superan las 12.0 horas de turno por 30 minutos o más (se omiten excesos < 30 min). Quedan excluidos Cambio de Guardia, Jornada Parcial (5-8h) y Régimen Especial (DNI 46181231 - José Moncada). Se formatea como `Exceso de Jornada (HH:MM)`.
  * **Exclusión Total de H.E. y Exceso para Personal Administrativo**:
    - El personal cuya posición / cargo sea `"Administrativo"` (DNI `74546819` Leila Lostaunau, DNI `77134790` Clari Tocto, DNI `48455175` Iván Vásquez) NO realiza ni acumula Horas Extras ni Exceso de Jornada bajo ninguna circunstancia.
    - En todos los cálculos y reportes del sistema, sus campos `HORAS EXTRAS (HH:MM)`, `EXCESO JORNADA (HH:MM)` y `TOTAL HORAS ADICIONALES (HH:MM)` permanecen estrictamente en `'00:00'` (0.0).
    - Únicamente se calculan y visualizan sus horas de turno trabajadas (`HORAS TRABAJADAS (HH:MM)`).
- **Doble Turno / Doble Entrada en el Mismo Día**:
  * Si un trabajador tiene 2 marcaciones de entrada el mismo día calendárico (doble turno / reingreso), se procesan ambos registros de forma independiente y se sombrea la fila en durazno pastel.
- **Filtro de Filas Fantasma / Sin Marcación (Regla Punto 9) y Excepción de H.E.**:
  * Se eliminan automáticamente de la vista procesada las filas donde tanto la Entrada (Fecha/Hora) como la Salida (Fecha/Hora) sean nulas, vacías o `NaN`, **salvo que la fila corresponda a un bloque exclusivo de Horas Extras** con marcaciones explícitas de biométrico.
- **Prohibición Total de Observaciones Asumidas o Textos Hardcodeados (Cero Suposiciones)**:
  * Queda estrictamente prohibido insertar o asumir observaciones automáticas por defecto en el motor de cálculo de asistencia (`core/attendance_engine.py`) o en la base de datos (como *"Abastecer petróleo / Recoger personal / Varios"*).
  * El campo `OBSERVACIONES` en asistencia y `observacion_trabajador` en aprobaciones permanecerá **limpio y vacío por defecto**, y se llenará **únicamente** con el sustento real o fotos que el trabajador o supervisor registre explícitamente desde la aplicación móvil.

---

## 4. ESTILOS Y FORMATO DEL REPORTE EXCEL EXPORTADO (`data/exporter.py`)
- **Estructura**: 23 Columnas (A a W).
- **Encabezados / Títulos de Celdas Corporativos**:
  * TODOS los encabezados de columna en cualquier archivo Excel (`Transacciones_Acumuladas.xlsx` y `Reporte_Asistencia_GZG`) deben llevar **Fondo Azul Oscuro (#1F4E78)** con texto **Blanco Bold**, alineación centrada vertical/horizontal con `wrap_text=True` y altura de fila de 28 a 32pt. (Para columnas calculadas en reportes de asistencia Q a U, se usa Azul Claro `#2F5597` / `#317F96`).
  * **Anchos de Columna Holgados sin Truncamiento**: Ningún título de columna debe quedar recortado o tapado por las flechas de filtro de Excel (ej. "Departamento", "Tiempo", "Tipo de pase de tarjeta", "Método de verificación", "Punto de control de asistencia"). Los anchos deben calcularse sumando una holgura de al menos +6 caracteres sobre la longitud del texto y un ancho mínimo de 16.
  * **Prohibición de `to_excel` Crudo**: Queda estrictamente PROHIBIDO guardar `Transacciones_Acumuladas.xlsx` o cualquier reporte de asistencia usando `pandas.to_excel` directo sin formato. Se debe invocar obligatoriamente la función `guardar_transacciones_acumuladas_excel(df, path)` de `data/exporter.py` en todos los scripts, tareas automáticas y rutinas para preservar los encabezados azul oscuro (`#1F4E78`), filtros activos y formato de celdas.
- **Sombreado Pastel de Incidencias y Registros**:
  * **Azul Pastel (`#D9E1F2`)**: Horas Extras (H.E.), Tipo de Registro con Horas Extras, bloques exclusivos de H.E. y Exceso de Jornada.
  * **Durazno Pastel (`#FCE4D6`)**: Faltas, Pendientes, Sin Registro, Salidas Anticipadas, Doble Turno (doble entrada el mismo día), Cambio de Guardia y Jornada Parcial.
  * **Sin Relleno (Blanco)**: Asistencias normales.
- **Preservación de Filas Exclusivas de Horas Extras (Excepción a Regla Punto 9)**:
  * Las filas que representen un bloque independiente de Horas Extras (sin marcaciones de entrada/salida de turno ordinario) se preservan y exportan con normalidad manteniendo su sombreado en **Azul Pastel (`#D9E1F2`)**.
- **Formato de Celdas**:
  * Columna A (DNI / ID): Formateada strictly como Texto (`@`) con `cell.number_format = '@'` en TODOS los archivos Excel generados (`Reporte_Asistencia_GZG` y `Transacciones_Acumuladas.xlsx`) para conservar ceros a la izquierda y evitar advertencias de Excel.
  * Horas trabajadas, tardanzas y excesos: Formateadas strictly en `HH:MM`.
- **Formato Limpio e Identificación de Autor en Comentarios de Aprobaciones (Columna S)**:
  * En la Columna S (*Comentario Supervisor*) de `Aprobaciones_GZG_YYYY-MM.xlsx`, cuando el trabajador o jefe registre su sustento personal en *Mis Horas Extras*, se antepone automáticamente el usuario o nombre del autor (ej. `jalva: <sustento>`, `respinoza: <sustento>`), complementado de forma ordenada por las validaciones de las jefaturas y aprobadores (ej. `N1 (msanchez): <comentario>`). Queda prohibido anteponer prefijos genéricos hardcodeados como `"Trabajador: "`.

---

## 5. NORMALIZACIÓN UNIVERSAL DE DNI Y CONTROL DE DUPLICIDAD
- **Formato Estricto e Invariante de 8 Dígitos (`digits.lstrip('0').zfill(8)`)**:
  * Todo DNI o identificador de persona en cualquier capa del sistema (lectura Excel, exportación a Excel, base de datos SQLite, reportes y padrón) se procesa mediante la función matemática invariante `digits.lstrip('0').zfill(8)`.
  * Esta regla garantiza que **NINGÚN DNI** pueda tener una longitud distinta de 8 dígitos, resolviendo de forma permanente y tajante cualquier descalce de ceros a la izquierda (ej. Franco `3208053` -> `03208053`, Yenkli `6616501` / `006616501` -> `06616501`).
  * Queda estrictamente **PROHIBIDO** el uso de diccionarios de mapeo manual o harcodeos con ceros adicionales (ej. `0066...`), así como el almacenamiento de DNIs como enteros o flotantes.
- **Consolidación Automática en SQLite y Padrón**:
  * Al ingresar nuevas marcaciones o trabajadores, el sistema consolida automáticamente por DNI normalizado de 8 dígitos, evitando duplicados en la base de datos o en `Padron_Trabajadores_GZG.xlsx`.

---

## 6. CONFIGURACIÓN DE GOOGLE DRIVE Y MANEJO DE ARCHIVOS EXCEL EN WINDOWS
- **Permisos de Cuenta de Servicio en Google Drive**:
  * Al compartir carpetas en Google Drive con la cuenta de servicio de Google Cloud (`*.gserviceaccount.com`), asignar estrictamente el rol **Colaborador** (Editor). Queda prohibido/bloqueado por Google asignar "Administrador de contenido".
- **Soporte Obligatorio para Unidades/Carpetas Compartidas (`supportsAllDrives=True`)**:
  * En la integración con la API v3 de Google Drive (`scripts/gdrive_uploader.py`), es **OBLIGATORIO** incluir los parámetros `supportsAllDrives=True` e `includeItemsFromAllDrives=True` en todas las llamadas de lectura (`files().list`), actualización (`files().update`) y creación (`files().create`), garantizando el acceso a carpetas compartidas de organización (ej. `29. CONECTIVIDAD > ASISTENCIA > AGOSTO`).
- **Limpieza Automática de Archivos Temporales de Descarga**:
  * La carpeta local `downloads/data_cruda/` debe contener **ÚNICAMENTE el archivo maestro `Transacciones_Acumuladas.xlsx`**. Todos los archivos temporales descargados por el biométrico (`Transacciones_YYYY-MM-DD_...xlsx`) deben eliminarse automáticamente tras ser fusionados en el maestro.
- **Manejo Seguro de Archivos Bloqueados en Microsoft Excel (`PermissionError`)**:
  * Cuando el usuario tiene abierto un archivo Excel (`Transacciones_Acumuladas.xlsx`, `Reporte_Asistencia_GZG_...xlsx` o `Sistema_Asistencia_GZG_v1.0.xlsx`) en su pantalla, Windows aplica un bloqueo de escritura de archivo.
  * El sistema debe capturar `PermissionError`, emitir una advertencia clara indicando que el archivo está abierto en Excel, y continuar la ejecución sin interrupciones bruscas.
  * Para visualizar las actualizaciones procesadas en segundo plano por el sistema, el usuario simplemente debe cerrar y volver a abrir la ventana de Excel en su computadora.

---

## 7. ESTÁNDARES DE INTERFAZ MÓVIL PWA Y EXPERIENCIA DE USUARIO
- **Prohibición Total y Permanente de "Built with Streamlit", Fullscreen y Footers (Doble Blindaje)**:
  * Queda estrictamente PROHIBIDO mostrar cualquier pie de página ("Built with Streamlit"), botones de fullscreen, menús de deploy o badges en cualquier ventana o vista del sistema.
  * **Capa 1 (mobile.py)**: Ocultación absoluta vía CSS estático de `footer`, `[data-testid="stFooter"]`, `div[data-testid="stBottom"]`, `div[class*="viewerBadge"]`, `div[data-testid="StyledFullScreenButton"]` y `button[title="View fullscreen"]` con `display: none !important; height: 0px !important;`.
- **Limpieza de UI de Streamlit sin Parches**: Toda ocultación de toolbar, header, deploy buttons, footer y skeletons debe realizarse exclusivamente mediante CSS estático en `<style>`, garantizando cero parpadeos (flickering) y cero bloqueos de pantalla.
- **Persistencia de Sesión ("Recordarme") y Cero Latencia**:
  * La persistencia de sesión móvil se gestiona de forma nativa mediante tokens seguros almacenados en la tabla SQLite `user_tokens` y vinculados a `st.query_params["token"]`.
  * Al cerrar sesión (`🚪 Salir`), el token se elimina inmediatamente de SQLite y de los query params, ejecutando `logout_user()` y `st.rerun()` de forma instantánea sin latencia.
- **Splash Screen Adaptativo en PWA (`index.html` y `docs/index.html`)**:
  * El wrapper PWA utiliza el evento `frame.addEventListener('load')` con un colchón adaptativo de 5 segundos posteriores a la carga base del iframe.
  * Si la señal `gzg:ready` enviada por Streamlit llega antes, la pantalla se revela de forma inmediata e instantánea.
  * Se mantiene un respaldo de seguridad de 25 segundos para proteger arranques en frío extremo (*cold start*).
- **Diseño de Métricas y Tarjetas de Evaluación**:
  * **3 Cajones KPI Simétricos**: En las vistas de Aprobador (`📋 Pendientes`) y Personal (`📝 Mis Horas Extras`), se muestran siempre 3 cajones en fila horizontal: `Pendientes` (Naranja), `Aprobadas` (Celeste) y `Rechazadas` (Rojo).
  * **Alertas de Validación Limpias**: Cero cajas de advertencia estáticas dentro de las tarjetas. Toda alerta de validación requerida se dispara al hacer clic y se ubica centrada a todo el ancho debajo de los botones de acción.
- **Sanitización de Datos en Historial y Tarjetas**:
  * Prohibición absoluta de mostrar textos `"nan"`, `"none"` o `"null"` originados por celdas vacías de Pandas.
  * Todo nombre de aprobador en el historial (`N1` / `N2`) se procesa con sanitización limpia y fallback al aprobador oficial asignado en el padrón o a `admin`.

---

## 8. SISTEMA DE APROBACIONES MÓVIL PWA Y ROLES RBAC
- **Bandeja Filtrada por Aprobador Asignado (Padrón Oficial)**:
  * En la aplicación móvil (`mobile.py`), cada usuario supervisor/jefe únicamente visualiza y aprueba a los trabajadores asignados bajo su cargo según las columnas `Nivel de Aprobacion 1` y `Nivel de Aprobacion 2` de `Padron_Trabajadores_GZG.xlsx`.
  * Los usuarios con rol `ADMINISTRACION` o `ADMIN` visualizan la totalidad de solicitudes del sistema sin restricciones.
- **Sincronización Automática e Invariante del Padrón (8 Columnas)**:
  * Toda sincronización de trabajadores entre Excel y SQLite (`data/database.py`) debe preservar obligatoriamente las 8 columnas completas: `DNI`, `Apellidos`, `Nombres`, `Departamento / Área`, `Posición / Cargo`, `Estado en Sistema`, `Nivel de Aprobacion 1`, `Nivel de Aprobacion 2`.
- **Regeneración y Subida Inmediata de `Aprobaciones_GZG_YYYY-MM.xlsx`**:
  * Tras cada acción de aprobación o rechazo en el app móvil, el sistema regenera automáticamente el archivo Excel `downloads/data_procesada/Aprobaciones_GZG_YYYY-MM.xlsx` con formato corporativo `#1F4E78` y lanza la subida inmediata a Google Drive en un **hilo background** (`threading.Thread`) para garantizar tiempo de respuesta instantáneo en la pantalla del supervisor.
- **Inmutabilidad Estricta de `Padron_Trabajadores_GZG.xlsx` (Solo Lectura Absoluta)**:
  * El archivo `Padron_Trabajadores_GZG.xlsx` en la raíz del proyecto es la fuente maestra oficial humana y es de **ESTRICTA SOLO LECTURA**.
  * Queda terminantemente PROHIBIDO que cualquier script, rutina automática, tarea programada o función de base de datos (`data/database.py`, `scripts/schedule_downloader.py`, `scripts/download_personal_info.py`, etc.) escriba, regenere o sobreescriba este archivo.
  * El sistema únicamente lee desde `Padron_Trabajadores_GZG.xlsx` para sincronizar trabajadores y aprobadores hacia SQLite.
- **Blindaje Absoluto contra Reinicios de Solicitudes y Estados de Aprobación**:
  * Queda **terminantemente prohibido** reiniciar, truncar, borrar o sobreescribir la tabla de aprobaciones (`aprobaciones`) en SQLite y los archivos Excel de aprobaciones sin orden explícita del usuario.
  * La sincronización interna de solicitudes (`sincronizar_aprobaciones_desde_asistencia`) es **estrictamente incremental (`INSERT OR IGNORE`)**: únicamente añade nuevos días con horas extras o excesos de jornada si no existen previamente en la base de datos.
- **Control Total y Aprobación de Contingencia del Rol `ADMIN`**:
  * **Superusuario Universal**: El usuario con rol `ADMINISTRADOR`, `ADMINISTRACION` o `ADMIN` tiene acceso irrestricto a la totalidad de solicitudes pendientes de todas las áreas y cuadrillas de la empresa.
  * **Aprobación de Contingencia en Ausencia de Jefaturas / Superintendencia**: Si un aprobador Nivel 1 (Jefe de Área) o Nivel 2 (Superintendente) se encuentra de descanso, vacaciones o sin conectividad, `admin` puede validar o rechazar cualquier solicitud:
    - Si la solicitud está en Nivel 1 pendiente, `admin` aprueba como Nivel 1 (avanzando al Nivel 2 o emitiendo aprobación final si no requiere N2).
    - Si la solicitud ya fue aprobada en Nivel 1 y está pendiente en Nivel 2, `admin` aprueba como Nivel 2 (emitiendo la Aprobación Final).
- **Auditoría Automática de Contingencia de `admin`**:
  * Cuando `admin` apruebe o rechace sin ingresar un texto manual, el sistema genera automáticamente el registro de auditoría `N1 (admin): Aprobado` o `N2 (admin): Aprobado` (o `Rechazado`) tanto en la Columna S del Excel oficial como en SQLite y en la vista de Historial.
- **Mandatoriedad de Comentario / Foto según Rol**:
  * **Rol `JEFE` y `PERSONAL`**: Es **100% mandatorio** ingresar al menos un comentario o adjuntar al menos una foto para aprobar/rechazar a subordinados o enviar sustento personal. El sistema bloquea el envío con campos vacíos.
  * **Rol `SUPERINTENDENTE` y `ADMINISTRADOR`**: El ingreso de comentario o foto es **opcional**, permitiendo aprobar o rechazar con 1 solo clic dado que el sustento técnico fue evaluado previamente en Nivel 1.
- **Persistencia Total y Blindaje contra Reinicios de Servidor / Cloud**:
  * Queda estrictamente PROHIBIDO reiniciar contadores o solicitudes en la base de datos o en los archivos Excel sin orden explícita del usuario.
  * **Rehidratación Obligatoria desde Drive al Inicio (`mobile.py`)**: Al iniciar sesión en `mobile.py`, el sistema ejecuta obligatoriamente `sincronizar_aprobaciones_con_gdrive()` utilizando `st.secrets["gcp_service_account"]` para descargar y restaurar en memoria los estados reales desde Google Drive, blindando la persistencia contra cualquier reinicio de Streamlit Cloud.
- **Rehidratación Bidireccional Previa Obligatoria en la PC Local**:
  * En la ejecución programada de las 9:00 AM (`scripts/schedule_downloader.py`) y en el monitor local (`scripts/auto_sync_approvals.py`), es **mandatorio** ejecutar `sincronizar_aprobaciones_con_gdrive(DB_PATH)` **antes** de generar el Excel de aprobaciones o subirlo a Google Drive.
  * Esta regla garantiza que la base de datos local SQLite absorba primero todas las aprobaciones, rechazos y comentarios registrados desde la app móvil en Streamlit Cloud, impidiendo que la PC local sobreescriba accidentalmente la nube con estados pendientes antiguos.
- **Bloqueo Estricto de Botones para Personal con Reporte Directo a Superintendencia (`msanchez`)**:
  * Para trabajadores, supervisores o jefes cuyo reporte sea directo a Superintendencia (`aprobador_n1 == 'msanchez'` y sin N2 intermedio), los botones `❌ RECHAZAR` y `✅ APROBAR` en la bandeja de `msanchez` permanecen estrictamente **bloqueados y desactivados (`disabled=True`)** mientras la solicitud no cuente con justificación o fotos registradas por el trabajador en `📝 Mis Horas Extras`.
  * Se muestra un recuadro de advertencia indicando que el trabajador debe registrar su sustento antes de poder evaluar.
  * Únicamente el rol `ADMIN` queda exento para aprobaciones de contingencia y emergencia.
- **Visualización Garantizada de Validación N1 y Sustentos en Bandeja Nivel 2**:
  * En la bandeja de pendientes del Superintendente, se presenta obligatoriamente el recuadro de **Validación Nivel 1** (`✅ Validación Nivel 1 (supervisor / admin): <comentario o Aprobado>`), junto con las fotos y el sustento personal del trabajador.
  * Al rehidratar desde Google Drive, el sistema recupera y desglosa los comentarios de N1 y N2 directamente en los campos `comentario_n1` y `comentario_n2` de la base de datos SQLite.




