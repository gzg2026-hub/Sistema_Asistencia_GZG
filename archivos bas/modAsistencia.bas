Attribute VB_Name = "modAsistencia"
Public Sub Procesar_Asistencia()

    On Error GoTo ManejarError

    Dim wsMar As Worksheet
    Dim wsAsis As Worksheet
    Dim wsHE As Worksheet
    Dim wsInc As Worksheet

    Dim UltFila As Long
    Dim i As Long

    Dim Dic As Object
    Dim Clave As String

    Dim M As clsMarcacionDia

    '====================================
    ' Optimización de Excel
    '====================================
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.Calculation = xlCalculationManual
    Application.StatusBar = "Preparando procesamiento..."

    Set wsMar = Worksheets(SH_MARCACIONES)
    Set wsAsis = Worksheets(SH_ASISTENCIA)
    Set wsHE = Worksheets(SH_HORAS_EXTRA)
    Set wsInc = Worksheets(SH_INCIDENCIAS)

    CargarConfiguracion
    CargarTrabajadores

    wsAsis.Rows("2:" & wsAsis.Rows.Count).ClearContents
    wsHE.Rows("2:" & wsHE.Rows.Count).ClearContents
    wsInc.Rows("2:" & wsInc.Rows.Count).ClearContents

    Set Dic = CreateObject("Scripting.Dictionary")

    UltFila = wsMar.Cells(wsMar.Rows.Count, COL_MAR_DNI).End(xlUp).Row

    For i = 2 To UltFila

        Application.StatusBar = "Leyendo marcaciones... " & (i - 1) & " de " & (UltFila - 1)

        Clave = Trim(wsMar.Cells(i, COL_MAR_DNI).Value) & "|" & _
                CStr(wsMar.Cells(i, COL_MAR_FECHA).Value)

        If Not Dic.Exists(Clave) Then

            Set M = New clsMarcacionDia

            M.DNI = Trim(wsMar.Cells(i, COL_MAR_DNI).Value)
            M.Fecha = wsMar.Cells(i, COL_MAR_FECHA).Value
            M.FilaTrabajador = BuscarTrabajador(M.DNI)

            Dic.Add Clave, M

        End If

        Dic(Clave).Filas.Add i

    Next i

    Application.StatusBar = "Procesando asistencias..."

    ProcesarGrupos Dic

Salida:

    Application.StatusBar = False
    Application.ScreenUpdating = True
    Application.EnableEvents = True
    Application.Calculation = xlCalculationAutomatic

    Exit Sub

ManejarError:

    Application.StatusBar = False
    Application.ScreenUpdating = True
    Application.EnableEvents = True
    Application.Calculation = xlCalculationAutomatic

    MsgBox "No se pudo procesar la asistencia." & vbCrLf & vbCrLf & _
           Err.Description, _
           vbCritical, "Error"

End Sub
Private Sub ProcesarGrupos(ByVal Dic As Object)

    Dim k
    Dim M As clsMarcacionDia
    Dim wsMar As Worksheet
    Dim f
    Dim MarcacionesOrdenadas As Collection

    Set wsMar = Worksheets(SH_MARCACIONES)

    For Each k In Dic.Keys

        Set M = Dic(k)

        CargarMarcaciones M, wsMar

        Set MarcacionesOrdenadas = OrdenarMarcacionesPorHora(M, wsMar)

        For Each f In MarcacionesOrdenadas

            ProcesarMarcacion _
                M, _
                wsMar.Cells(f, COL_MAR_HORA).Value, _
                wsMar.Cells(f, COL_MAR_TIPO).Value

        Next f

        CalcularRegistro M

        EscribirRegistro M

        EscribirBloquesHE M

        EscribirIncidencias M

    Next k

End Sub


Private Function CalcularHorasTrabajadas( _
        ByVal Entrada As Date, _
        ByVal Salida As Date) As Double

    If Entrada = 0 Then Exit Function
    If Salida = 0 Then Exit Function

    If Salida < Entrada Then

        CalcularHorasTrabajadas = (Salida + 1) - Entrada

    Else

        CalcularHorasTrabajadas = Salida - Entrada

    End If

End Function

Private Sub CalcularRegistro(ByRef M As clsMarcacionDia)

    'Detectar horario
    If M.TieneEntrada Then

        M.HorarioDetectado = DetectarHorario(M.Entrada)

    Else

        M.HorarioDetectado = ""

    End If

    'Horas trabajadas
    If M.TieneEntrada And M.TieneSalida Then

        M.HorasTrabajadas = _
            CalcularHorasTrabajadas( _
                M.Entrada, _
                M.Salida)

    Else

        M.HorasTrabajadas = 0

    End If

    'Tardanza
    If M.TieneEntrada Then

        M.Tardanza = _
            CalcularTardanza( _
                M.HorarioDetectado, _
                M.Entrada)

    Else

        M.Tardanza = 0

    End If

    'Salida anticipada
    If M.TieneSalida Then

        M.SalidaAnticipada = _
            CalcularSalidaAnticipada( _
                M.HorarioDetectado, _
                M.Salida)

    Else

        M.SalidaAnticipada = 0

    End If

    'Detectar bloques de horas extra
    DetectarBloquesHE M

    'Horas extra
    M.HorasExtra = CalcularHorasExtra(M)

    'Exceso de jornada
    If M.TieneEntrada And M.TieneSalida Then

        M.ExcesoJornada = _
            CalcularExcesoJornada(M.HorasTrabajadas)

    Else

        M.ExcesoJornada = 0

    End If

    'Total horas adicionales
    M.TotalHorasAdicionales = _
        CalcularTotalHorasAdicionales( _
            M.HorasExtra, _
            M.ExcesoJornada)

    'Estado de asistencia
    M.EstadoAsistencia = ObtenerEstadoAsistencia(M)

End Sub

Private Sub EscribirRegistro(ByVal M As clsMarcacionDia)

    Dim Fila As Long
    Dim ws As Worksheet
    Dim filaTrab As Long

    Set ws = Worksheets(SH_ASISTENCIA)

    Fila = ws.Cells(ws.Rows.Count, COL_FECHA).End(xlUp).Row + 1

    If Fila < 2 Then Fila = 2

    '==============================
    ' Datos básicos
    '==============================
    ws.Cells(Fila, COL_FECHA).Value = M.Fecha
    ws.Cells(Fila, COL_DNI).Value = M.DNI

    filaTrab = M.FilaTrabajador

    If filaTrab > 0 Then

        With Worksheets(SH_TRABAJADORES)

            ws.Cells(Fila, COL_APELLIDOS).Value = .Cells(filaTrab, COL_TRAB_APELLIDOS).Value
            ws.Cells(Fila, COL_NOMBRES).Value = .Cells(filaTrab, COL_TRAB_NOMBRES).Value
            ws.Cells(Fila, COL_CARGO).Value = .Cells(filaTrab, COL_TRAB_CARGO).Value
            ws.Cells(Fila, COL_AREA).Value = .Cells(filaTrab, COL_TRAB_AREA).Value

        End With

        ws.Cells(Fila, COL_TURNO).Value = M.HorarioDetectado

    Else

        ws.Cells(Fila, COL_OBSERVACIONES).Value = "TRABAJADOR NO REGISTRADO"

    End If

    ws.Cells(Fila, COL_HORARIO).Value = M.HorarioDetectado

    '==============================
    ' Entrada
    '==============================
    If M.TieneEntrada Then

        ws.Cells(Fila, COL_ENTRADA).Value = M.Entrada
        ws.Cells(Fila, COL_ENTRADA).NumberFormat = "hh:mm"

    End If

    '==============================
    ' Salida
    '==============================
    If M.TieneSalida Then

        ws.Cells(Fila, COL_SALIDA).Value = M.Salida
        ws.Cells(Fila, COL_SALIDA).NumberFormat = "hh:mm"

    End If

    '==============================
    ' Horas trabajadas
    '==============================
    If M.TieneEntrada And M.TieneSalida Then

        ws.Cells(Fila, COL_HORAS).Value = M.HorasTrabajadas
        ws.Cells(Fila, COL_HORAS).NumberFormat = "[h]:mm"

    End If

    '==============================
    ' Tardanza
    '==============================
    If M.TieneEntrada Then

        ws.Cells(Fila, COL_TARDANZA).Value = M.Tardanza
        ws.Cells(Fila, COL_TARDANZA).NumberFormat = "0"

    End If

    '==============================
    ' Salida anticipada
    '==============================
    If M.TieneSalida Then

        ws.Cells(Fila, COL_SALIDA_ANT).Value = M.SalidaAnticipada
        ws.Cells(Fila, COL_SALIDA_ANT).NumberFormat = "0"

    End If

    '==============================
    ' Exceso de jornada
    '==============================
    If M.TieneEntrada And M.TieneSalida Then

        ws.Cells(Fila, COL_EXCESO).Value = M.ExcesoJornada
        ws.Cells(Fila, COL_EXCESO).NumberFormat = "[h]:mm"

    End If

    '==============================
    ' Total horas adicionales
    '==============================
    ws.Cells(Fila, COL_TOTAL_HE).Value = M.TotalHorasAdicionales
    ws.Cells(Fila, COL_TOTAL_HE).NumberFormat = "[h]:mm"

    '==============================
    ' Incidencias
    '==============================
    ws.Cells(Fila, COL_INCIDENCIAS).Value = M.Incidencias

    '==============================
    ' Estado
    '==============================
    ws.Cells(Fila, COL_ESTADO).Value = M.EstadoAsistencia

End Sub

Private Sub EscribirBloquesHE(ByVal M As clsMarcacionDia)

    Dim ws As Worksheet
    Dim Fila As Long
    Dim filaTrab As Long
    Dim B As clsBloqueHE

    Set ws = Worksheets(SH_HORAS_EXTRA)

    filaTrab = M.FilaTrabajador

    For Each B In M.BloquesHE

        Fila = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row + 1

        If Fila < 2 Then Fila = 2

        ws.Cells(Fila, 1).Value = M.Fecha
        ws.Cells(Fila, 2).Value = M.DNI

        If filaTrab > 0 Then

            With Worksheets(SH_TRABAJADORES)

                ws.Cells(Fila, 3).Value = .Cells(filaTrab, COL_TRAB_APELLIDOS).Value
                ws.Cells(Fila, 4).Value = .Cells(filaTrab, COL_TRAB_NOMBRES).Value

            End With

            ws.Cells(Fila, 5).Value = M.HorarioDetectado

        End If

        ws.Cells(Fila, 6).Value = B.Inicio
        ws.Cells(Fila, 7).Value = B.Fin
        ws.Cells(Fila, 8).Value = B.Duracion

        ws.Cells(Fila, 6).NumberFormat = "hh:mm"
        ws.Cells(Fila, 7).NumberFormat = "hh:mm"
        ws.Cells(Fila, 8).NumberFormat = "[h]:mm"

    Next B

End Sub

Private Function OrdenarMarcacionesPorHora( _
    ByVal M As clsMarcacionDia, _
    ByVal wsMar As Worksheet) As Collection

    Dim Resultado As New Collection
    Dim Indices() As Long
    Dim i As Long
    Dim j As Long
    Dim Temp As Long

    ReDim Indices(1 To M.Filas.Count)

    For i = 1 To M.Filas.Count
        Indices(i) = M.Filas(i)
    Next i

    'Ordenamiento por hora (Bubble Sort)
    For i = 1 To UBound(Indices) - 1

        For j = i + 1 To UBound(Indices)

            If wsMar.Cells(Indices(i), COL_MAR_HORA).Value > _
               wsMar.Cells(Indices(j), COL_MAR_HORA).Value Then

                Temp = Indices(i)
                Indices(i) = Indices(j)
                Indices(j) = Temp

            End If

        Next j

    Next i

    For i = 1 To UBound(Indices)
        Resultado.Add Indices(i)
    Next i

    Set OrdenarMarcacionesPorHora = Resultado

End Function

