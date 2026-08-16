VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "clsMarcacionDia"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = False
Option Explicit

'=========================================
' DATOS DEL TRABAJADOR
'=========================================
Public DNI As String
Public Fecha As Date
Public FilaTrabajador As Long

'Datos del trabajador (cache)
Public Apellidos As String
Public Nombres As String
Public Cargo As String
Public Area As String

'=========================================
' MARCACIONES PRINCIPALES
'=========================================
Public Entrada As Date
Public Salida As Date

'=========================================
' RESULTADOS DEL CÁLCULO
'=========================================
Public HorarioDetectado As String
Public EstadoAsistencia As String

Public HorasTrabajadas As Double
Public Tardanza As Long
Public SalidaAnticipada As Long

'Duración total de los bloques de Horas Extra
Public HorasExtra As Double

'Tiempo trabajado por encima de la jornada programada
Public ExcesoJornada As Double

'Exceso de jornada + Horas Extra
Public TotalHorasAdicionales As Double

'=========================================
' INCIDENCIAS
'=========================================
Public Incidencias As String

'=========================================
' BANDERAS
'=========================================
Public TieneEntrada As Boolean
Public TieneSalida As Boolean

'=========================================
' COLECCIONES
'=========================================
Public Filas As Collection
Public Marcaciones As Collection
Public BloquesHE As Collection
Public ListaIncidencias As Collection

'=========================================
' INICIALIZACIÓN
'=========================================
Private Sub Class_Initialize()

    Set Filas = New Collection
    Set Marcaciones = New Collection
    Set BloquesHE = New Collection
    Set ListaIncidencias = New Collection

    TieneEntrada = False
    TieneSalida = False

    DNI = ""
    Fecha = 0
    FilaTrabajador = 0

    Apellidos = ""
    Nombres = ""
    Cargo = ""
    Area = ""

    Entrada = 0
    Salida = 0

    HorarioDetectado = ""
    EstadoAsistencia = ""

    HorasTrabajadas = 0
    Tardanza = 0
    SalidaAnticipada = 0

    HorasExtra = 0
    ExcesoJornada = 0
    TotalHorasAdicionales = 0

    Incidencias = ""

End Sub
