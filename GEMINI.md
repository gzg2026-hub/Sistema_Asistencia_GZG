# REGLAS OBLIGATORIAS DEL PROYECTO SISTEMA DE ASISTENCIA GZG

## 1. REGLA DE EXCEPCIÓN AUTORIZADA PARA GOOGLE DRIVE
- ÚNICAMENTE los siguientes **2 archivos** tienen autorización explícita para subida/sincronización automática a Google Drive (**Directamente en la carpeta `AGOSTO`, SIN CREAR SUBDORIOS NI SUBCARPETAS**):
  1. `Transacciones_Acumuladas.xlsx` *(Maestro Acumulado de Marcaciones Crudas)*.
  2. `Reporte_Asistencia_GZG_YYYY-MM-DD.xlsx` *(Reportes Diarios Procesados de Días Cerrados)*.
- **PROHIBIDO TOTALMENTE EN DRIVE**:
  - NO crear subcarpetas como `Data_Cruda` o `Data_Procesada` en Google Drive.
  - `Sistema_Asistencia_GZG_v1.0.xlsx` *(Archivo raíz ejecutable en la PC, NUNCA se sube a Drive)*.
  - Cualquier otro archivo temporal o de consolidado parcial.

## 2. PRESERVACIÓN DE DATA CRUDA REAL DEL BIOMÉTRICO
- En los archivos de data cruda (`Transacciones_Acumuladas.xlsx`), se deben mantener **los valores reales exactos** exportados por el biométrico HikCentral.
- Queda prohibido hardcodear o inventar valores por defecto (como "MINA", "OPERATIVO", "Semana 34", "Marcación", "Rostro").

## 3. APLICACIÓN DE LÓGICA DE ASISTENCIA
- La lógica de deducción e Inteligencia Artificial se aplica **únicamente en el motor de cálculo de asistencia** (procesar turnos, detectar entradas/salidas y calcular horas trabajadas), nunca alterando el texto original de la data cruda.
