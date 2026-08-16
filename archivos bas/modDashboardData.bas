Attribute VB_Name = "modDashboardData"
Option Explicit

'=========================================================
' MODDASHBOARDDATA
' Sistema de Control de Asistencia
'=========================================================

Public Type TDashboardData

    TotalPersonal As Long

    Presentes As Long

    Ausentes As Long

    Tardanzas As Long

    ExcesoJornada As Double

    HEProgramadas As Double

    Incidencias As Long

    TurnoDia As Long

    TurnoNoche As Long

    Descanso As Long

    Vacaciones As Long

    Permisos As Long

End Type

Public DashboardData As TDashboardData

Private DicTrabajadores As Object

Private FechaDashboard As Date

'=========================================================
' ACTUALIZA TODOS LOS DATOS DEL DASHBOARD
'=========================================================
Public Sub ActualizarDashboardData()

    FechaDashboard = Int(Worksheets(SH_CONFIG).Range("FECHA_DASHBOARD").Value)

    LimpiarDashboardData

    Set DicTrabajadores = CreateObject("Scripting.Dictionary")

    LeerTrabajadores

    LeerAsistencia

    LeerIncidencias
    
    LeerHorasExtra

End Sub

'=========================================================
' LIMPIA VARIABLES
'=========================================================
Private Sub LimpiarDashboardData()

    With DashboardData

        .TotalPersonal = 0

        .Presentes = 0

        .Ausentes = 0

        .Tardanzas = 0

        .ExcesoJornada = 0

        .HEProgramadas = 0

        .Incidencias = 0

        .TurnoDia = 0

        .TurnoNoche = 0

        .Descanso = 0

        .Vacaciones = 0

        .Permisos = 0

    End With

    Set DicTrabajadores = Nothing

End Sub

'=========================================================
' LEE EL TOTAL DE TRABAJADORES
'=========================================================
Private Sub LeerTrabajadores()

    Dim ws As Worksheet
    Dim UltFila As Long

    Set ws = Worksheets(SH_TRABAJADORES)

    UltFila = ws.Cells(ws.Rows.Count, COL_TRAB_DNI).End(xlUp).Row

    If UltFila < 2 Then Exit Sub

    DashboardData.TotalPersonal = UltFila - 1

End Sub

'=========================================================
' LEE LA ASISTENCIA DEL DIA SELECCIONADO
'=========================================================
Private Sub LeerAsistencia()

    Dim ws As Worksheet
    Dim UltFila As Long
    Dim Fila As Long

    Set ws = Worksheets(SH_ASISTENCIA)

    UltFila = ws.Cells(ws.Rows.Count, COL_FECHA).End(xlUp).Row

    If UltFila < 2 Then Exit Sub

    For Fila = 2 To UltFila

        If IsDate(ws.Cells(Fila, COL_FECHA).Value) Then

            If Int(ws.Cells(Fila, COL_FECHA).Value) = FechaDashboard Then

                ProcesarRegistro ws, Fila

            End If

        End If

    Next Fila

End Sub

'=========================================================
' PROCESA UN TRABAJADOR SOLO UNA VEZ
'=========================================================
Private Sub ProcesarRegistro(ByVal ws As Worksheet, ByVal Fila As Long)

    Dim DNI As String

    DNI = Trim$(CStr(ws.Cells(Fila, COL_DNI).Value))

    If DNI = "" Then Exit Sub

    If DicTrabajadores.Exists(DNI) Then Exit Sub

    DicTrabajadores.Add DNI, True
    
    ContarEstado ws, Fila

    ContarTardanza ws, Fila

    ContarExcesoJornada ws, Fila

End Sub

'=========================================================
' CONTAR PRESENTES / AUSENTES
'=========================================================
Private Sub ContarEstado(ByVal ws As Worksheet, ByVal Fila As Long)

    Dim Estado As String

    Estado = UCase$(Trim$(CStr(ws.Cells(Fila, COL_ESTADO).Value)))

    Select Case Estado

        Case "FALTA"

            DashboardData.Ausentes = DashboardData.Ausentes + 1

        Case Else

            DashboardData.Presentes = DashboardData.Presentes + 1

    End Select

End Sub

'=========================================================
' CONTAR TARDANZAS
'=========================================================
Private Sub ContarTardanza(ByVal ws As Worksheet, ByVal Fila As Long)

    If Val(ws.Cells(Fila, COL_TARDANZA).Value) > 0 Then

        DashboardData.Tardanzas = DashboardData.Tardanzas + 1

    End If

End Sub

'=========================================================
' ACUMULAR HORAS EXTRA
'=========================================================
Private Sub ContarExcesoJornada(ByVal ws As Worksheet, ByVal Fila As Long)

    DashboardData.ExcesoJornada = _
        DashboardData.ExcesoJornada + _
        Val(ws.Cells(Fila, COL_EXCESO).Value)

End Sub

'=========================================================
' LEE LAS INCIDENCIAS DEL DIA
'=========================================================
Private Sub LeerIncidencias()

    Dim ws As Worksheet
    Dim UltFila As Long
    Dim Fila As Long

    Set ws = Worksheets(SH_INCIDENCIAS)

    UltFila = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row

    If UltFila < 2 Then Exit Sub

    For Fila = 2 To UltFila

        If IsDate(ws.Cells(Fila, 1).Value) Then

            If Int(ws.Cells(Fila, 1).Value) = FechaDashboard Then

                DashboardData.Incidencias = _
                    DashboardData.Incidencias + 1

            End If

        End If

    Next Fila

End Sub

'=========================================================
' FUNCIONES PUBLICAS
'=========================================================

Public Function TotalPersonal() As Long

    TotalPersonal = DashboardData.TotalPersonal

End Function

Public Function TotalPresentes() As Long

    TotalPresentes = DashboardData.Presentes

End Function

Public Function TotalAusentes() As Long

    TotalAusentes = DashboardData.Ausentes

End Function

Public Function TotalExcesoJornada() As Double

    TotalExcesoJornada = DashboardData.ExcesoJornada

End Function

Public Function TotalHEProgramadas() As Double

    TotalHEProgramadas = DashboardData.HEProgramadas

End Function

Public Function TotalIncidencias() As Long

    TotalIncidencias = DashboardData.Incidencias

End Function

Public Function TotalTardanzas() As Long

    TotalTardanzas = DashboardData.Tardanzas

End Function

'=========================================================
' LEE HORAS EXTRA PROGRAMADAS DEL DÍA
'=========================================================
Private Sub LeerHorasExtra()

    Dim ws As Worksheet
    Dim UltFila As Long
    Dim Fila As Long

    Set ws = Worksheets(SH_HORAS_EXTRA)

    UltFila = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row

    If UltFila < 2 Then Exit Sub

    For Fila = 2 To UltFila

        If IsDate(ws.Cells(Fila, 1).Value) Then

            If Int(ws.Cells(Fila, 1).Value) = FechaDashboard Then

                DashboardData.HEProgramadas = _
                    DashboardData.HEProgramadas + _
                    CDbl(ws.Cells(Fila, 8).Value)

            End If

        End If

    Next Fila

End Sub

