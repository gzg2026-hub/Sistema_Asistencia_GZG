Attribute VB_Name = "modConstantes"
Option Explicit

'========================================
' COLUMNAS 04_ASISTENCIA
'========================================

Public Const COL_FECHA As Long = 1
Public Const COL_DNI As Long = 2
Public Const COL_APELLIDOS As Long = 3
Public Const COL_NOMBRES As Long = 4
Public Const COL_CARGO As Long = 5
Public Const COL_AREA As Long = 6
Public Const COL_TURNO As Long = 7
Public Const COL_HORARIO As Long = 8

Public Const COL_ENTRADA As Long = 9
Public Const COL_SALIDA As Long = 10

Public Const COL_HORAS As Long = 11
Public Const COL_TARDANZA As Long = 12
Public Const COL_SALIDA_ANT As Long = 13

Public Const COL_EXCESO As Long = 14
Public Const COL_TOTAL_HE As Long = 15

Public Const COL_INCIDENCIAS As Long = 16
Public Const COL_ESTADO As Long = 17
Public Const COL_OBSERVACIONES As Long = 18

'=========================================
' HOJA 02_TRABAJADORES
'=========================================
Public Const COL_TRAB_DNI As Long = 1
Public Const COL_TRAB_APELLIDOS As Long = 2
Public Const COL_TRAB_NOMBRES As Long = 3
Public Const COL_TRAB_CARGO As Long = 4
Public Const COL_TRAB_AREA As Long = 5
'========================================
' HOJA 03_MARCACIONES
'========================================
Public Const COL_MAR_DNI As Long = 1
Public Const COL_MAR_FECHA As Long = 6
Public Const COL_MAR_HORA As Long = 8
Public Const COL_MAR_TIPO As Long = 9

'=========================================
' NOMBRES DE HOJAS
'=========================================
Public Const SH_CONFIG As String = "01_CONFIG"
Public Const SH_TRABAJADORES As String = "02_TRABAJADORES"
Public Const SH_MARCACIONES As String = "03_MARCACIONES"
Public Const SH_ASISTENCIA As String = "04_ASISTENCIA"
Public Const SH_HORAS_EXTRA As String = "05_HORAS_EXTRA"
Public Const SH_INCIDENCIAS As String = "06_INCIDENCIAS"
Public Const SH_DASHBOARD As String = "07_DASHBOARD"
Public Const SH_REPORTES As String = "08_REPORTES"
