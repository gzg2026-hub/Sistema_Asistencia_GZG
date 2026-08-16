Attribute VB_Name = "modCalculos"
Option Explicit

'==========================================================
' DETECTAR HORARIO
'==========================================================
Public Function DetectarHorario(ByVal HoraEntrada As Date) As String

    Dim H As Date

    H = TimeValue(HoraEntrada)

    'Turno Día
    If H >= HoraInicioDia And H < HoraFinDia Then

        DetectarHorario = "DIA"
        Exit Function

    End If

    'Turno Noche (puede cruzar medianoche)
    If HoraInicioNoche > HoraFinNoche Then

        If H >= HoraInicioNoche Or H < HoraFinNoche Then

            DetectarHorario = "NOCHE"

        Else

            DetectarHorario = "DESCONOCIDO"

        End If

    Else

        If H >= HoraInicioNoche And H < HoraFinNoche Then

            DetectarHorario = "NOCHE"

        Else

            DetectarHorario = "DESCONOCIDO"

        End If

    End If

End Function

'==========================================================
' CALCULAR TARDANZA (MINUTOS)
'==========================================================
Public Function CalcularTardanza( _
    ByVal Horario As String, _
    ByVal HoraEntrada As Date) As Long

    Dim HoraProgramada As Date

    Select Case Horario

        Case "DIA"
            HoraProgramada = TimeValue("07:00")

        Case "NOCHE"
            HoraProgramada = TimeValue("19:00")

        Case Else
            Exit Function

    End Select

    If HoraEntrada <= DateAdd("n", ToleranciaEntrada, HoraProgramada) Then

    CalcularTardanza = 0

    Else

    CalcularTardanza = _
        DateDiff( _
            "n", _
            DateAdd("n", ToleranciaEntrada, HoraProgramada), _
            HoraEntrada)

    End If

End Function

'==========================================================
' CALCULAR SALIDA ANTICIPADA (MINUTOS)
'==========================================================
Public Function CalcularSalidaAnticipada( _
    ByVal Horario As String, _
    ByVal HoraSalida As Date) As Long

    Dim HoraProgramada As Date

    Select Case Horario

        Case "DIA"
            HoraProgramada = TimeValue("19:00")

        Case "NOCHE"
            HoraProgramada = TimeValue("07:00")

        Case Else
            Exit Function

    End Select

    If HoraSalida >= DateAdd("n", -ToleranciaSalida, HoraProgramada) Then

    CalcularSalidaAnticipada = 0

    Else

    CalcularSalidaAnticipada = _
        DateDiff( _
            "n", _
            HoraSalida, _
            DateAdd("n", -ToleranciaSalida, HoraProgramada))

    End If

End Function

'==========================================================
' HORAS EXTRA (SUMA DE BLOQUES)
'==========================================================
Public Function CalcularHorasExtra(ByRef M As clsMarcacionDia) As Double

    Dim B As clsBloqueHE

    CalcularHorasExtra = 0

    For Each B In M.BloquesHE

        CalcularHorasExtra = CalcularHorasExtra + B.Duracion

    Next B

End Function

'==========================================================
' EXCESO DE JORNADA
'==========================================================
Public Function CalcularExcesoJornada( _
    ByVal HorasTrabajadas As Double) As Double

    Const Jornada As Double = 12 / 24

    If HorasTrabajadas > Jornada Then

        CalcularExcesoJornada = HorasTrabajadas - Jornada

    Else

        CalcularExcesoJornada = 0

    End If

End Function

'==========================================================
' TOTAL HORAS ADICIONALES
'==========================================================
Public Function CalcularTotalHorasAdicionales( _
    ByVal HorasExtra As Double, _
    ByVal Exceso As Double) As Double

    CalcularTotalHorasAdicionales = HorasExtra + Exceso

End Function

'==========================================================
' ESTADO DE ASISTENCIA
'==========================================================
Public Function ObtenerEstadoAsistencia(ByRef M As clsMarcacionDia) As String

    'Sin marcaciones
    If Not M.TieneEntrada And Not M.TieneSalida Then

        ObtenerEstadoAsistencia = "FALTA"
        Exit Function

    End If

    'Solo entrada
    If M.TieneEntrada And Not M.TieneSalida Then

        ObtenerEstadoAsistencia = "SALIDA PENDIENTE"
        Exit Function

    End If

    'Solo salida
    If Not M.TieneEntrada And M.TieneSalida Then

        ObtenerEstadoAsistencia = "ENTRADA PENDIENTE"
        Exit Function

    End If

    'Entrada y salida registradas
    If Len(Trim(M.Incidencias)) > 0 Then

        ObtenerEstadoAsistencia = "ASISTIÓ CON INCIDENCIAS"

    ElseIf M.Tardanza > 0 And M.SalidaAnticipada > 0 Then

        ObtenerEstadoAsistencia = "TARDANZA + SALIDA ANTICIPADA"

    ElseIf M.Tardanza > 0 Then

        ObtenerEstadoAsistencia = "TARDANZA"

    ElseIf M.SalidaAnticipada > 0 Then

        ObtenerEstadoAsistencia = "SALIDA ANTICIPADA"

    ElseIf M.HorasExtra > 0 Then

        ObtenerEstadoAsistencia = "ASISTIÓ CON H.E."

    Else

        ObtenerEstadoAsistencia = "ASISTIÓ"

    End If

End Function

