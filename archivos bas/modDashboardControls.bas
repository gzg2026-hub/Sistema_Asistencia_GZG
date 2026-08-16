Attribute VB_Name = "modDashboardControls"
Option Explicit

'=========================================================
' MODDASHBOARDCONTROLS
' Biblioteca gráfica del Dashboard
'=========================================================

Public Function DashboardSheet() As Worksheet

    Set DashboardSheet = ThisWorkbook.Worksheets(DASHBOARD_SHEET)

End Function


Public Sub DeleteShape(ByVal ShapeName As String)

    Dim ws As Worksheet

    Set ws = DashboardSheet

    On Error Resume Next
    ws.Shapes(ShapeName).Delete
    On Error GoTo 0

End Sub


Public Sub DeleteAllDashboardShapes()

    Dim ws As Worksheet
    Dim shp As Shape

    Set ws = DashboardSheet

    For Each shp In ws.Shapes

        shp.Delete

    Next shp

End Sub
Public Function CrearRectangulo( _
            Nombre As String, _
            X As Double, _
            Y As Double, _
            W As Double, _
            H As Double, _
            Color As Long) As Shape

    Dim ws As Worksheet

    Set ws = DashboardSheet

    DeleteShape Nombre

    Set CrearRectangulo = ws.Shapes.AddShape( _
                    msoShapeRoundedRectangle, _
                    X, Y, W, H)

    With CrearRectangulo

        .Name = Nombre

        .Fill.ForeColor.RGB = Color

        .Line.Visible = msoFalse

    End With

End Function
Public Function CrearTexto( _
            Nombre As String, _
            Texto As String, _
            X As Double, _
            Y As Double, _
            W As Double, _
            H As Double, _
            Tam As Double, _
            Negrita As Boolean) As Shape

    Dim ws As Worksheet

    Set ws = DashboardSheet

    DeleteShape Nombre

    Set CrearTexto = ws.Shapes.AddTextbox( _
            msoTextOrientationHorizontal, _
            X, Y, W, H)

    With CrearTexto

        .Name = Nombre

        .Line.Visible = msoFalse

        .Fill.Visible = msoFalse

        With .TextFrame2

            .VerticalAnchor = msoAnchorMiddle

            .TextRange.Text = Texto

            .TextRange.Font.Name = FONT_NAME

            .TextRange.Font.Size = Tam

            .TextRange.Font.Bold = Negrita

            .TextRange.Font.Fill.ForeColor.RGB = COLOR_TEXT

            .TextRange.ParagraphFormat.Alignment = msoAlignCenter

        End With

    End With

End Function
Public Sub CentrarShape(shp As Shape)

    With shp.TextFrame2

        .VerticalAnchor = msoAnchorMiddle

        .TextRange.ParagraphFormat.Alignment = msoAlignCenter

    End With

End Sub


Public Sub PintarPanel(shp As Shape)

    With shp

        .Fill.ForeColor.RGB = COLOR_PANEL

        .Line.Visible = msoFalse

    End With

End Sub


Public Sub PintarKPI(shp As Shape)

    With shp

        .Fill.ForeColor.RGB = COLOR_PANEL

        .Line.Visible = msoFalse

    End With

End Sub
