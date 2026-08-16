Attribute VB_Name = "modDashboardUI"
Option Explicit

'=========================================================
' MODULO : modDashboardUI
'=========================================================

Private Const COLOR_BLANCO As Long = vbWhite
Private Const COLOR_NEGRO As Long = vbBlack

'=========================================================
' DEVUELVE LA HOJA DEL DASHBOARD
'=========================================================
Private Function DashboardSheet() As Worksheet

    Set DashboardSheet = Worksheets(DASHBOARD_SHEET)

End Function

'=========================================================
' ELIMINA UN SHAPE SI EXISTE
'=========================================================
Public Sub DeleteShape(ByVal ShapeName As String)

    On Error Resume Next
    DashboardSheet.Shapes(ShapeName).Delete
    On Error GoTo 0

End Sub

'=========================================================
' CREA UN RECTANGULO REDONDEADO
'=========================================================
Public Function CrearRectangulo( _
        ByVal Nombre As String, _
        ByVal LeftPos As Double, _
        ByVal TopPos As Double, _
        ByVal WidthPos As Double, _
        ByVal HeightPos As Double, _
        ByVal FillColor As Long) As Shape

    Dim shp As Shape

    DeleteShape Nombre

    Set shp = DashboardSheet.Shapes.AddShape( _
                msoShapeRoundedRectangle, _
                LeftPos, _
                TopPos, _
                WidthPos, _
                HeightPos)

    shp.Name = Nombre

    shp.Fill.ForeColor.RGB = FillColor

    shp.Line.Visible = msoFalse

    Set CrearRectangulo = shp

End Function

'=========================================================
' CREA UNA ETIQUETA DE TEXTO
'=========================================================
Public Function CrearTexto( _
        ByVal Nombre As String, _
        ByVal Texto As String, _
        ByVal LeftPos As Double, _
        ByVal TopPos As Double, _
        ByVal WidthPos As Double, _
        ByVal HeightPos As Double, _
        Optional ByVal FontSize As Long = 10, _
        Optional ByVal Bold As Boolean = False, _
        Optional ByVal ColorFuente As Long = vbWhite) As Shape

    Dim txt As Shape

    DeleteShape Nombre

    Set txt = DashboardSheet.Shapes.AddTextbox( _
                msoTextOrientationHorizontal, _
                LeftPos, _
                TopPos, _
                WidthPos, _
                HeightPos)

    txt.Name = Nombre

    txt.Fill.Visible = msoFalse
    txt.Line.Visible = msoFalse

    With txt.TextFrame2

        .WordWrap = msoFalse
        .VerticalAnchor = msoAnchorMiddle

        .TextRange.Text = Texto

        With .TextRange.Font

            .Name = FONT_NAME
            .Size = FontSize
            .Bold = Bold
            .Fill.ForeColor.RGB = ColorFuente

        End With

        .TextRange.ParagraphFormat.Alignment = msoAlignLeft

    End With

    Set CrearTexto = txt

End Function

'=========================================================
' CREA EL HEADER PRINCIPAL
'=========================================================
Public Sub CrearHeader()

    Dim Fondo As Shape

    Set Fondo = CrearRectangulo( _
                    SHP_HEADER, _
                    HEADER_LEFT, _
                    HEADER_TOP, _
                    HEADER_WIDTH, _
                    HEADER_HEIGHT, _
                    COLOR_HEADER)

    'Sin borde
    Fondo.Line.Visible = msoFalse

    '----------------------------------------------------
    ' TITULO PRINCIPAL
    '----------------------------------------------------
    CrearTexto _
        "TXT_EMPRESA", _
        "GZG MINERALES", _
        HEADER_LEFT + 20, _
        HEADER_TOP + 8, _
        260, _
        24, _
        18, _
        True

    CrearTexto _
        "TXT_SISTEMA", _
        "CENTRO DE CONTROL DE ASISTENCIA", _
        HEADER_LEFT + 20, _
        HEADER_TOP + 34, _
        380, _
        20, _
        10, _
        False

    '----------------------------------------------------
    ' FECHA Y HORA
    '----------------------------------------------------
    CrearFechaHoraHeader

End Sub

'=========================================================
' CREA LA FILA DE KPI
'=========================================================
Public Sub CrearFilaKPIs()

    Dim X As Double
    Dim Espacio As Double

    Espacio = KPI_GAP
    X = HEADER_LEFT

    CrearKPI SHP_KPI1, "PERSONAL", X, KPI_TOP
    X = X + KPI_WIDTH + Espacio

    CrearKPI SHP_KPI2, "PRESENTES", X, KPI_TOP
    X = X + KPI_WIDTH + Espacio

    CrearKPI SHP_KPI3, "AUSENTES", X, KPI_TOP
    X = X + KPI_WIDTH + Espacio

    CrearKPI SHP_KPI4, "TARDANZAS", X, KPI_TOP
    X = X + KPI_WIDTH + Espacio

    CrearKPI SHP_KPI5, "EXCESO JORNADA", X, KPI_TOP
    X = X + KPI_WIDTH + Espacio

    CrearKPI SHP_KPI6, "H.E. PROGRAMADAS", X, KPI_TOP
    X = X + KPI_WIDTH + Espacio

    CrearKPI SHP_KPI7, "INCIDENCIAS", X, KPI_TOP
    X = X + KPI_WIDTH + Espacio

    CrearKPI SHP_KPI8, "% ASISTENCIA", X, KPI_TOP

End Sub
'=========================================================
' CREA FECHA Y HORA
'=========================================================
Public Sub CrearFechaHoraHeader()

    Dim FechaDashboard As Variant
    Dim FechaTexto As String

    On Error Resume Next
    FechaDashboard = Worksheets(CONFIG_SHEET).Range("FECHA_DASHBOARD").Value
    On Error GoTo 0

    If IsDate(FechaDashboard) Then
        FechaTexto = Format(CDate(FechaDashboard), "dddd dd mmmm yyyy")
    Else
        FechaTexto = Format(Date, "dddd dd mmmm yyyy")
    End If

    CrearTexto _
        SHP_FECHA, _
        UCase$(FechaTexto), _
        HEADER_LEFT + HEADER_WIDTH - 270, _
        HEADER_TOP + 12, _
        240, _
        20, _
        10, _
        True

    CrearTexto _
        SHP_HORA, _
        Format(Now, "HH:MM:SS"), _
        HEADER_LEFT + HEADER_WIDTH - 270, _
        HEADER_TOP + 35, _
        240, _
        20, _
        10, _
        False

End Sub
'=========================================================
' CREA KPI PROFESIONAL
'=========================================================
Public Sub CrearKPI( _
            ByVal Nombre As String, _
            ByVal Titulo As String, _
            ByVal LeftPos As Double, _
            ByVal TopPos As Double)

    Dim Fondo As Shape
    Dim Barra As Shape

    Set Fondo = CrearRectangulo( _
                    Nombre, _
                    LeftPos, _
                    TopPos, _
                    KPI_WIDTH, _
                    KPI_HEIGHT, _
                    COLOR_PANEL)

    Fondo.Line.Visible = msoFalse

    '-------------------------------------------
    ' Barra superior
    '-------------------------------------------
    Set Barra = DashboardSheet.Shapes.AddShape( _
                    msoShapeRectangle, _
                    LeftPos, _
                    TopPos, _
                    KPI_WIDTH, _
                    3)

    Barra.Name = Nombre & "_TOP"

    Barra.Line.Visible = msoFalse
    Barra.Fill.ForeColor.RGB = COLOR_PRIMARY

    '-------------------------------------------
    ' Título
    '-------------------------------------------
    CrearTexto _
        Nombre & "_TIT", _
        UCase$(Titulo), _
        LeftPos + 8, _
        TopPos + 8, _
        KPI_WIDTH - 16, _
        16, _
        8, _
        True

    '-------------------------------------------
    ' Valor
    '-------------------------------------------
    CrearTexto _
        Nombre & "_VAL", _
        "0", _
        LeftPos + 8, _
        TopPos + 28, _
        KPI_WIDTH - 16, _
        34, _
        18, _
        True

End Sub
'=========================================================
' ACTUALIZA KPI
'=========================================================
Public Sub ActualizarKPI( _
            ByVal Nombre As String, _
            ByVal Valor As Variant)

    On Error Resume Next

    With DashboardSheet.Shapes(Nombre & "_VAL").TextFrame2

        .TextRange.Text = CStr(Valor)

        .TextRange.ParagraphFormat.Alignment = msoAlignCenter

        With .TextRange.Font

            .Size = 18
            .Bold = True
            .Fill.ForeColor.RGB = vbWhite

        End With

    End With

    On Error GoTo 0

End Sub
'=========================================================
' CREA PANEL PROFESIONAL
'=========================================================
Public Function CrearPanel( _
            ByVal Nombre As String, _
            ByVal Titulo As String, _
            ByVal LeftPos As Double, _
            ByVal TopPos As Double, _
            ByVal WidthPos As Double, _
            ByVal HeightPos As Double) As Shape

    Dim Fondo As Shape
    Dim Barra As Shape

    Set Fondo = CrearRectangulo( _
                    Nombre, _
                    LeftPos, _
                    TopPos, _
                    WidthPos, _
                    HeightPos, _
                    COLOR_PANEL)

    Fondo.Line.Visible = msoFalse

    '---------------------------------------------------
    ' Barra superior del panel
    '---------------------------------------------------
    Set Barra = DashboardSheet.Shapes.AddShape( _
                    msoShapeRectangle, _
                    LeftPos, _
                    TopPos, _
                    WidthPos, _
                    4)

    Barra.Name = Nombre & "_TOP"

    Barra.Line.Visible = msoFalse
    Barra.Fill.ForeColor.RGB = COLOR_PRIMARY

    '---------------------------------------------------
    ' Título
    '---------------------------------------------------
    CrearTexto _
        Nombre & "_TITULO", _
        UCase$(Titulo), _
        LeftPos + 12, _
        TopPos + 10, _
        WidthPos - 24, _
        20, _
        10, _
        True

    Set CrearPanel = Fondo

End Function
'=========================================================
' ACTUALIZA FECHA Y HORA
'=========================================================
Public Sub RefrescarFechaHora()

    Dim FechaDashboard As Variant
    Dim FechaTexto As String

    On Error Resume Next
    FechaDashboard = Worksheets(CONFIG_SHEET).Range("FECHA_DASHBOARD").Value
    On Error GoTo 0

    If IsDate(FechaDashboard) Then
        FechaTexto = Format(CDate(FechaDashboard), "dddd dd mmmm yyyy")
    Else
        FechaTexto = Format(Date, "dddd dd mmmm yyyy")
    End If

    On Error Resume Next

    DashboardSheet.Shapes(SHP_FECHA).TextFrame2.TextRange.Text = UCase$(FechaTexto)

    DashboardSheet.Shapes(SHP_HORA).TextFrame2.TextRange.Text = Format(Now, "HH:MM:SS")

    On Error GoTo 0

End Sub
'=========================================================
' CREA TODOS LOS PANELES DEL DASHBOARD
'=========================================================
Public Sub CrearPanelesPrincipales()

    Dim X1 As Double
    Dim X2 As Double
    Dim Y As Double

    X1 = HEADER_LEFT
    X2 = HEADER_LEFT + PANEL_LEFT_WIDTH + GAP
    Y = PANEL_TOP

    CrearPanel _
        "PNL_GRAFICO", _
        "RESUMEN DE ASISTENCIA", _
        X1, _
        Y, _
        PANEL_LEFT_WIDTH, _
        PANEL_HEIGHT

    CrearPanel _
        "PNL_PERSONAL", _
        "PERSONAL TRABAJANDO", _
        X2, _
        Y, _
        PANEL_RIGHT_WIDTH, _
        PANEL_HEIGHT

    Y = Y + PANEL_HEIGHT + GAP

    CrearPanel _
        "PNL_ESTADO", _
        "ESTADO DE TURNOS", _
        X1, _
        Y, _
        PANEL_LEFT_WIDTH, _
        PANEL_HEIGHT

    CrearPanel _
        "PNL_ALERTAS", _
        "ALERTAS", _
        X2, _
        Y, _
        PANEL_RIGHT_WIDTH, _
        PANEL_HEIGHT

End Sub
'=========================================================
' CREA BOTON
'=========================================================
Public Function CrearBoton( _
        ByVal Nombre As String, _
        ByVal Texto As String, _
        ByVal LeftPos As Double, _
        ByVal TopPos As Double, _
        ByVal WidthPos As Double, _
        ByVal HeightPos As Double) As Shape

    Dim shp As Shape

    Set shp = CrearRectangulo( _
                    Nombre, _
                    LeftPos, _
                    TopPos, _
                    WidthPos, _
                    HeightPos, _
                    COLOR_PRIMARY)

    shp.Line.Visible = msoFalse

    shp.TextFrame2.TextRange.Text = Texto

    With shp.TextFrame2.TextRange.Font

        .Name = FONT_NAME
        .Size = 10
        .Bold = msoTrue
        .Fill.ForeColor.RGB = vbWhite

    End With

    shp.TextFrame2.HorizontalAnchor = msoAnchorCenter
    shp.TextFrame2.VerticalAnchor = msoAnchorMiddle

    Set CrearBoton = shp

End Function
'=========================================================
' CREA BOTONES SUPERIORES
'=========================================================
Public Sub CrearBotones()

    Dim X As Double

    X = HEADER_LEFT + HEADER_WIDTH - 520

    CrearBoton "BTN_ACTUALIZAR", "ACTUALIZAR", X, HEADER_TOP + 18, 95, 30

    X = X + 105

    CrearBoton "BTN_PDF", "PDF", X, HEADER_TOP + 18, 80, 30

    X = X + 90

    CrearBoton "BTN_REPORTES", "REPORTES", X, HEADER_TOP + 18, 100, 30

    X = X + 110

    CrearBoton "BTN_CONFIG", "CONFIG.", X, HEADER_TOP + 18, 95, 30

End Sub
'=========================================================
' CENTRAR TEXTO
'=========================================================
Public Sub CentrarTexto(ByVal shp As Shape)

    With shp.TextFrame2

        .HorizontalAnchor = msoAnchorCenter
        .VerticalAnchor = msoAnchorMiddle

        With .TextRange.ParagraphFormat

            .Alignment = msoAlignCenter

        End With

    End With

End Sub
'=========================================================
' FORMATEAR BOTON
'=========================================================
Public Sub FormatearBoton(ByVal shp As Shape)

    shp.Line.Visible = msoFalse

    shp.Fill.ForeColor.RGB = COLOR_PRIMARY

    With shp.TextFrame2.TextRange.Font

        .Name = FONT_NAME
        .Size = 10
        .Bold = msoTrue
        .Fill.ForeColor.RGB = vbWhite

    End With

    CentrarTexto shp

End Sub
'=========================================================
' ASIGNAR MACROS
'=========================================================
Public Sub AsignarMacros()

    Dim ws As Worksheet

    Set ws = DashboardSheet

    On Error Resume Next

    ws.Shapes("BTN_ACTUALIZAR").OnAction = "ActualizarDashboard"

    ws.Shapes("BTN_PDF").OnAction = "ExportarDashboardPDF"

    ws.Shapes("BTN_REPORTES").OnAction = "AbrirReportes"

    ws.Shapes("BTN_CONFIG").OnAction = "AbrirConfiguracion"

    On Error GoTo 0

End Sub
'=========================================================
' CREA TODA LA INTERFAZ
'=========================================================
Public Sub CrearInterfazDashboard()

    CrearHeader

    CrearFilaKPIs

    CrearPanelesPrincipales

    CrearBotones

    AsignarMacros

End Sub
'=========================================================
' COLOREA EL ESTADO EN LA TABLA
'=========================================================
Public Sub ColorearEstado(ByVal Celda As Range, ByVal Estado As String)

    Select Case UCase$(Trim$(Estado))

        Case "PRESENTE"

            Celda.Interior.Color = RGB(46, 204, 113)
            Celda.Font.Color = vbWhite

        Case "AUSENTE"

            Celda.Interior.Color = RGB(231, 76, 60)
            Celda.Font.Color = vbWhite

        Case "TARDANZA"

            Celda.Interior.Color = RGB(241, 196, 15)
            Celda.Font.Color = vbBlack

        Case "INCIDENCIA"

            Celda.Interior.Color = RGB(52, 152, 219)
            Celda.Font.Color = vbWhite

        Case Else

            Celda.Interior.Pattern = xlNone
            Celda.Font.Color = vbBlack

    End Select

End Sub

