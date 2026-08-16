Attribute VB_Name = "modDashboardDesigner"
Option Explicit

'=========================================================
' MODULO : modDashboardDesigner
' AUTOR  : Raul Espinoza
' EMPRESA: GZG Minerales
' SISTEMA: Sistema de Control de Asistencia
'=========================================================

Private DicPresentes As Object
Private DicTardanzas As Object
Private DicIncidencias As Object
Dim ExcesoJornada As Double
Dim HEProgramadas As Double

'=========================================================
' CREA DASHBOARD
'=========================================================
Public Sub CrearDashboard()

    On Error GoTo ErrHandler

    Application.ScreenUpdating = False
    Application.EnableEvents = False

    InicializarLayout

    PrepararHoja

    CrearInterfazDashboard

    PrepararDatosDashboard

    ActualizarDashboardData

    ActualizarDashboard

Salir:

    Application.EnableEvents = True
    Application.ScreenUpdating = True

    Exit Sub

ErrHandler:

    MsgBox "Error al crear el Dashboard." & vbCrLf & _
           Err.Number & " - " & Err.Description, _
           vbCritical

    Resume Salir

End Sub
'=========================================================
' ACTUALIZA EL GRAFICO
'=========================================================
Private Sub RefrescarGraficoResumen( _
            ByVal Presentes As Long, _
            ByVal Ausentes As Long, _
            ByVal Tardanzas As Long, _
            ByVal Incidencias As Long)

    With Worksheets(SH_DASHBOARD)

        If .ChartObjects.Count = 0 Then Exit Sub

        With .ChartObjects(GRAFICO_RESUMEN).Chart.SeriesCollection(1)

            .Values = Array( _
                    Presentes, _
                    Ausentes, _
                    Tardanzas, _
                    Incidencias)

        End With

    End With

End Sub

'=========================================================
' PREPARA LA HOJA DASHBOARD
'=========================================================
Private Sub PrepararHoja()

    On Error GoTo ErrHandler

    Dim ws As Worksheet

    Set ws = Worksheets(SH_DASHBOARD)

    With ws

        .Cells.Clear

        DeleteAllDashboardShapes

        .Activate

        ActiveWindow.DisplayGridlines = False

    End With

Salir:
    Exit Sub

ErrHandler:

    MsgBox "Error preparando la hoja Dashboard." & vbCrLf & _
           Err.Number & " - " & Err.Description, _
           vbCritical

    Resume Salir

End Sub

'=========================================================
' PREPARA DATOS DEL DASHBOARD
'=========================================================
Private Sub PrepararDatosDashboard()

    Dim ws As Worksheet

    Set ws = Worksheets(SH_DASHBOARD)

    With ws

        .Range("AA:AB").ClearContents

        .Range("AA1").Value = "Fecha"
        .Range("AB1").Value = "Presentes"

    End With

End Sub
'=========================================================
' ACTUALIZA DASHBOARD
'=========================================================
Private Sub ActualizarDashboard()

    On Error GoTo ErrHandler

    Dim TotalPersonal As Long
    Dim Presentes As Long
    Dim Ausentes As Long
    Dim Tardanzas As Long
    Dim Incidencias As Long
    Dim HorasExtra As Double
    Dim Porcentaje As Double

    Application.ScreenUpdating = False

    ActualizarDashboardData

    With DashboardData

        TotalPersonal = .TotalPersonal
        Presentes = .Presentes
        Ausentes = .Ausentes
        Tardanzas = .Tardanzas
        ExcesoJornada = .ExcesoJornada
        HEProgramadas = .HEProgramadas
        Incidencias = .Incidencias

    End With

    If TotalPersonal > 0 Then

        Porcentaje = Presentes / TotalPersonal

    Else

        Porcentaje = 0

    End If

    ActualizarKPIs _
        TotalPersonal, _
        Presentes, _
        Ausentes, _
        Tardanzas, _
        ExcesoJornada, _
        HEProgramadas, _
        Incidencias, _
        Porcentaje

   RefrescarGraficoResumen _
        Presentes, _
        Ausentes, _
        Tardanzas, _
        Incidencias

    'ActualizarTablaResumen

    DibujarResumenVisual _
        Presentes, _
        Ausentes, _
        Tardanzas, _
        Incidencias

Salir:

    Application.ScreenUpdating = True

    Exit Sub

ErrHandler:

    Application.ScreenUpdating = True

    MsgBox _
        "Error actualizando Dashboard." & vbCrLf & _
        Err.Number & " - " & Err.Description, _
        vbCritical

End Sub
    
'=========================================================
' ACTUALIZA LOS KPI DEL DASHBOARD
'=========================================================
Private Sub ActualizarKPIs( _
    ByVal TotalPersonal As Long, _
    ByVal Presentes As Long, _
    ByVal Ausentes As Long, _
    ByVal Tardanzas As Long, _
    ByVal ExcesoJornada As Double, _
    ByVal HEProgramadas As Double, _
    ByVal Incidencias As Long, _
    ByVal Porcentaje As Double)

    ActualizarKPI SHP_KPI1, TotalPersonal
    ActualizarKPI SHP_KPI2, Presentes
    ActualizarKPI SHP_KPI3, Ausentes
    ActualizarKPI SHP_KPI4, Tardanzas

    ActualizarKPI SHP_KPI5, FormatearHoras(ExcesoJornada)
    ActualizarKPI SHP_KPI6, FormatearHoras(HEProgramadas)

    ActualizarKPI SHP_KPI7, Incidencias
    ActualizarKPI SHP_KPI8, Format(Porcentaje, "0%")

End Sub

'=========================================================
' FECHA ANTERIOR
'=========================================================
Public Sub DashboardFechaAnterior()

    With Worksheets(CONFIG_SHEET).Range("FECHA_DASHBOARD")
        .Value = DateAdd("d", -1, .Value)
    End With

    ActualizarDashboard
    CrearFechaHoraHeader

End Sub

'=========================================================
' FECHA SIGUIENTE
'=========================================================
Public Sub DashboardFechaSiguiente()

    With Worksheets(CONFIG_SHEET).Range("FECHA_DASHBOARD")
        .Value = DateAdd("d", 1, .Value)
    End With

    ActualizarDashboard
    CrearFechaHoraHeader

End Sub

'=========================================================
' CREA LA TABLA RESUMEN
'=========================================================
Private Sub CrearTablaResumen()

    Dim ws As Worksheet
    Dim Cabeceras As Variant
    Dim Anchos As Variant
    Dim i As Long

    Set ws = Worksheets(SH_DASHBOARD)

    Cabeceras = Array( _
        "DNI", _
        "TRABAJADOR", _
        "ENTRADA", _
        "SALIDA", _
        "H. EXTRA", _
        "INCIDENCIA", _
        "ESTADO")

    Anchos = Array(14, 28, 12, 12, 12, 24, 14)

    With ws

        .Range("A30:G500").Clear

        For i = 0 To UBound(Cabeceras)

            With .Cells(30, i + 1)

                .Value = Cabeceras(i)

                .Interior.Color = COLOR_PRIMARY
                .Font.Color = vbWhite
                .Font.Bold = True
                .Font.Name = FONT_NAME
                .Font.Size = 10

                .HorizontalAlignment = xlCenter
                .VerticalAlignment = xlCenter

                .Borders.LineStyle = xlContinuous
                .Borders.Weight = xlThin

            End With

            .Columns(i + 1).ColumnWidth = Anchos(i)

        Next i

        .Rows(30).RowHeight = 24

    End With

End Sub

'=========================================================
' LLENA TABLA RESUMEN (OPTIMIZADA)
'=========================================================
Private Sub ActualizarTablaResumen()

    Dim wsA As Worksheet
    Dim wsD As Worksheet

    Dim UltFila As Long
    Dim filaDestino As Long
    Dim i As Long
    
    Dim FechaDashboard As Date
    Dim Estado As String
    
    Dim Datos As Variant
      

    Set wsA = Worksheets(SH_ASISTENCIA)
    Set wsD = Worksheets(SH_DASHBOARD)

    FechaDashboard = Worksheets(SH_CONFIG).Range("FECHA_DASHBOARD").Value

    Application.ScreenUpdating = False

    wsD.Range("A31:G500").ClearContents
    wsD.Range("A31:G500").Interior.Pattern = xlNone

    UltFila = wsA.Cells(wsA.Rows.Count, "A").End(xlUp).Row

    Datos = wsA.Range("A2:Q" & UltFila).Value2

    filaDestino = 31

    For i = 1 To UBound(Datos, 1)

    If Int(Datos(i, 1)) = Int(FechaDashboard) Then

        Estado = UCase$(Trim$(CStr(Datos(i, 17))))

        With wsD

            .Cells(filaDestino, 1).Value = Datos(i, 2)

            .Cells(filaDestino, 2).Value = _
                Datos(i, 3) & " " & Datos(i, 4)

            .Cells(filaDestino, 3).Value = Datos(i, 9)

            .Cells(filaDestino, 4).Value = Datos(i, 10)

            .Cells(filaDestino, 5).Value = Datos(i, 15)

            .Cells(filaDestino, 6).Value = Datos(i, 16)

            .Cells(filaDestino, 7).Value = Estado

        End With

        ColorearEstado wsD.Cells(filaDestino, 7), Estado

        filaDestino = filaDestino + 1

    End If

Next i

   

    If filaDestino > 31 Then

        With wsD.Range("A31:G" & filaDestino - 1)

            .Borders.LineStyle = xlContinuous
            .Borders.Weight = xlThin

            .Font.Name = "Segoe UI"
            .Font.Size = 9

            .VerticalAlignment = xlCenter

        End With

    End If

    Application.ScreenUpdating = True

End Sub
'=========================================================
' CREA EL GRAFICO PRINCIPAL
'=========================================================
Private Sub CrearGraficoResumen()

    Dim ws As Worksheet
    Dim ch As ChartObject

    Set ws = Worksheets(SH_DASHBOARD)

    On Error Resume Next
    ws.ChartObjects(GRAFICO_RESUMEN).Delete
    On Error GoTo 0

    Set ch = ws.ChartObjects.Add( _
        HEADER_LEFT + 15, _
        PANEL_TOP + 22, _
        PANEL_LEFT_WIDTH - 30, _
        PANEL_HEIGHT - 40)
        
    ch.Name = GRAFICO_RESUMEN

    With ch.Chart

        .ChartType = xlColumnClustered
        .ChartArea.Format.Line.Visible = msoFalse
        .PlotArea.Format.Line.Visible = msoFalse

        .ChartArea.Format.Fill.Visible = msoFalse
        .PlotArea.Format.Fill.Visible = msoFalse

        .Axes(xlCategory).TickLabels.Font.Size = 9
        .Axes(xlValue).TickLabels.Font.Size = 9

        .HasLegend = False

        .HasTitle = True
        .ChartTitle.Text = "RESUMEN DE ASISTENCIA"

        .ChartArea.Format.Fill.Visible = msoFalse
        .PlotArea.Format.Fill.Visible = msoFalse

        .Axes(xlValue).MajorGridlines.Format.Line.Visible = msoFalse

        .SeriesCollection.NewSeries

        .SeriesCollection(1).XValues = Array( _
            "Presentes", _
            "Ausentes", _
            "Tardanzas", _
            "Incidencias")

        .SeriesCollection(1).Values = Array(0, 0, 0, 0)

    End With

End Sub

'=========================================================
' CREA UNA BARRA HORIZONTAL
'=========================================================
Private Sub CrearBarraHorizontal( _
            ByVal Nombre As String, _
            ByVal LeftPos As Double, _
            ByVal TopPos As Double, _
            ByVal AnchoMax As Double, _
            ByVal Alto As Double, _
            ByVal Valor As Double, _
            ByVal ValorMax As Double, _
            ByVal ColorBarra As Long)

    Dim ws As Worksheet
    Dim Fondo As Shape
    Dim Barra As Shape
    Dim Etiqueta As Shape

    Dim AnchoBarra As Double

    Set ws = Worksheets(SH_DASHBOARD)

    If ValorMax = 0 Then
        AnchoBarra = 0
    Else
        AnchoBarra = (Valor / ValorMax) * AnchoMax
    End If

    On Error Resume Next
    ws.Shapes(Nombre & "_BG").Delete
    ws.Shapes(Nombre).Delete
    ws.Shapes(Nombre & "_TXT").Delete
    On Error GoTo 0

    Set Fondo = ws.Shapes.AddShape( _
                    msoShapeRectangle, _
                    LeftPos, _
                    TopPos, _
                    AnchoMax, _
                    Alto)

    Fondo.Name = Nombre & "_BG"

    Fondo.Fill.ForeColor.RGB = RGB(70, 70, 70)
    Fondo.Line.Visible = msoFalse

    Set Barra = ws.Shapes.AddShape( _
                    msoShapeRectangle, _
                    LeftPos, _
                    TopPos, _
                    AnchoBarra, _
                    Alto)

    Barra.Name = Nombre

    Barra.Fill.ForeColor.RGB = ColorBarra
    Barra.Line.Visible = msoFalse

    Set Etiqueta = ws.Shapes.AddTextbox( _
                        msoTextOrientationHorizontal, _
                        LeftPos + AnchoMax + 10, _
                        TopPos - 3, _
                        60, _
                        Alto + 6)

    Etiqueta.Name = Nombre & "_TXT"

    Etiqueta.Line.Visible = msoFalse
    Etiqueta.Fill.Visible = msoFalse

    Etiqueta.TextFrame.Characters.Text = CStr(Valor)

    With Etiqueta.TextFrame.Characters.Font
        .Name = "Segoe UI"
        .Bold = True
        .Size = 10
        .Color = vbWhite
    End With

End Sub

'=========================================================
' BARRAS RESUMEN
'=========================================================
Private Sub DibujarResumenVisual( _
        Presentes As Long, _
        Ausentes As Long, _
        Tardanzas As Long, _
        Incidencias As Long)

    Dim Maximo As Long
    Dim X As Double
    Dim Y As Double
    Dim W As Double

    Maximo = Application.Max( _
                Presentes, _
                Ausentes, _
                Tardanzas, _
                Incidencias)

    If Maximo = 0 Then Maximo = 1

    X = HEADER_LEFT + 35
    Y = PANEL_TOP + PANEL_HEIGHT + 35
    W = PANEL_LEFT_WIDTH - 110

    CrearBarraHorizontal _
        "BAR_PRESENTES", _
        X, Y, W, 18, _
        Presentes, _
        Maximo, _
        RGB(46, 204, 113)

    Y = Y + 35

    CrearBarraHorizontal _
        "BAR_AUSENTES", _
        X, Y, W, 18, _
        Ausentes, _
        Maximo, _
        RGB(231, 76, 60)

    Y = Y + 35

    CrearBarraHorizontal _
        "BAR_TARDANZAS", _
        X, Y, W, 18, _
        Tardanzas, _
        Maximo, _
        RGB(241, 196, 15)

    Y = Y + 35

    CrearBarraHorizontal _
        "BAR_INCIDENCIAS", _
        X, Y, W, 18, _
        Incidencias, _
        Maximo, _
        RGB(52, 152, 219)

End Sub

Private Function FormatearHoras(ByVal Valor As Double) As String

    Dim Minutos As Long

    Minutos = CLng(Valor * 1440)

    If Minutos < 60 Then
        FormatearHoras = Minutos & " min"
    Else
        FormatearHoras = _
            Int(Minutos / 60) & " h " & _
            (Minutos Mod 60) & " min"
    End If

End Function
