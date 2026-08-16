Attribute VB_Name = "modDashboardConst"
Option Explicit

'=========================================================
' MODULO : modDashboardConst
' AUTOR  : Raul Espinoza
' EMPRESA: GZG Minerales
'=========================================================

'=========================
' HOJAS
'=========================
Public Const DASHBOARD_SHEET As String = "07_DASHBOARD"
Public Const CONFIG_SHEET As String = "01_CONFIG"
Public Const TRABAJADORES_SHEET As String = "02_TRABAJADORES"

'=========================
' MEDIDAS GENERALES
'=========================
Public Const MARGIN As Double = 20
Public Const GAP As Double = 12

'=========================
' HEADER
'=========================
Public Const HEADER_LEFT As Double = 15
Public Const HEADER_TOP As Double = 15
Public Const HEADER_WIDTH As Double = 1650
Public Const HEADER_HEIGHT As Double = 70

Public Const HEADER_LOGO_WIDTH As Double = 90
Public Const HEADER_INFO_WIDTH As Double = 170

'=========================
' KPI
'=========================
Public Const KPI_TOP As Double = 120
Public Const KPI_WIDTH As Double = 155
Public Const KPI_HEIGHT As Double = 75
Public Const KPI_GAP As Double = 8

'=========================
' PANELES
'=========================
Public Const PANEL_TOP As Double = 230
Public Const PANEL_HEIGHT As Double = 320

Public Const PANEL_LEFT_WIDTH As Double = 815
Public Const PANEL_RIGHT_WIDTH As Double = 815

'=========================
' COLORES
'=========================
Public Const COLOR_BACKGROUND As Long = &H37311F
Public Const COLOR_HEADER As Long = &H271811
Public Const COLOR_PANEL As Long = &H514137
Public Const COLOR_PRIMARY As Long = &HF6823B

'=========================
' TIPOGRAFIA
'=========================
Public Const FONT_NAME As String = "Segoe UI"

'=========================
' NOMBRES DE SHAPES
'=========================
Public Const SHP_HEADER As String = "HDR_FONDO"

Public Const SHP_FECHA As String = "TXT_FECHA"
Public Const SHP_HORA As String = "TXT_HORA"

Public Const SHP_KPI1 As String = "KPI1"
Public Const SHP_KPI2 As String = "KPI2"
Public Const SHP_KPI3 As String = "KPI3"
Public Const SHP_KPI4 As String = "KPI4"
Public Const SHP_KPI5 As String = "KPI5"
Public Const SHP_KPI6 As String = "KPI6"
Public Const SHP_KPI7 As String = "KPI7"
Public Const SHP_KPI8 As String = "KPI8"

Public Const GRAFICO_RESUMEN As String = "GRF_RESUMEN"

'=========================================================
' DASHBOARD V2
'=========================================================

'=========================
' DISTRIBUCIÓN
'=========================
Public Const KPI_COUNT As Long = 8

Public Const PANEL_GAP As Double = 15

Public Const CONTENT_MARGIN As Double = 15

Public Const TABLE_TOP_GAP As Double = 15

Public Const TABLE_HEIGHT As Double = 250

'=========================
' BOTONES
'=========================
Public Const BTN_WIDTH As Double = 42
Public Const BTN_HEIGHT As Double = 42
Public Const BTN_GAP As Double = 8

'=========================
' ICONOS
'=========================
Public Const ICON_SIZE As Double = 20

'=========================
' FUENTES
'=========================
Public Const FONT_TITLE As Double = 18
Public Const FONT_SUBTITLE As Double = 11
Public Const FONT_KPI_TITLE As Double = 10
Public Const FONT_KPI_VALUE As Double = 22
Public Const FONT_PANEL_TITLE As Double = 12
Public Const FONT_TABLE As Double = 9

'=========================
' COLORES SECUNDARIOS
'=========================
Public Const COLOR_SUCCESS As Long = &H5CB85C
Public Const COLOR_WARNING As Long = &H66CCFF
Public Const COLOR_DANGER As Long = &H5A5AF2
Public Const COLOR_TEXT As Long = &HFFFFFF
Public Const COLOR_TEXT_SECONDARY As Long = &HE0E0E0

'=========================
' PANELES
'=========================
Public Const PANEL_GRAFICO As String = "PNL_GRAFICO"

Public Const PANEL_PERSONAL As String = "PNL_PERSONAL"

Public Const PANEL_ESTADO As String = "PNL_ESTADO"

Public Const PANEL_ALERTAS As String = "PNL_ALERTAS"

Public Const PANEL_TABLA As String = "PNL_TABLA"

'=========================
' TABLA
'=========================
Public Const TABLA_RESUMEN As String = "TBL_RESUMEN"

'=========================
' BOTONES
'=========================
Public Const BTN_ACTUALIZAR As String = "BTN_ACTUALIZAR"

Public Const BTN_HOY As String = "BTN_HOY"

Public Const BTN_ANTERIOR As String = "BTN_ANTERIOR"

Public Const BTN_SIGUIENTE As String = "BTN_SIGUIENTE"
