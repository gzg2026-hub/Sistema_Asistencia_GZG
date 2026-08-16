Attribute VB_Name = "modDashboardCharts"
Option Explicit

'=========================================================
' MODDASHBOARDCHARTS
' Gestión de todos los gráficos del Dashboard
'=========================================================

Public Function ObtenerGrafico( _
                Nombre As String) As ChartObject

    Dim ws As Worksheet

    Set ws = DashboardSheet

    On Error Resume Next
    Set ObtenerGrafico = ws.ChartObjects(Nombre)
    On Error GoTo 0

End Function


Public Sub EliminarGrafico( _
                Nombre As String)

    Dim ch As ChartObject

    Set ch = ObtenerGrafico(Nombre)

    If Not ch Is Nothing Then

        ch.Delete

    End If

End Sub
Public Function CrearGrafico( _
                Nombre As String, _
                Area As TRect) As ChartObject

    Dim ws As Worksheet

    Set ws = DashboardSheet

    EliminarGrafico Nombre

    Set CrearGrafico = ws.ChartObjects.Add( _
                    Area.Left + CONTENT_MARGIN, _
                    Area.Top + 35, _
                    Area.Width - CONTENT_MARGIN * 2, _
                    Area.Height - 50)

    CrearGrafico.Name = Nombre

End Function
Public Sub FormatearGrafico( _
                ch As ChartObject)

    With ch.Chart

        .ChartArea.Format.Line.Visible = msoFalse

        .PlotArea.Format.Line.Visible = msoFalse

        .ChartArea.Format.Fill.Visible = msoFalse

        .PlotArea.Format.Fill.Visible = msoFalse

        .HasLegend = False

        .HasTitle = False

        .Axes(xlCategory).TickLabels.Font.Size = 9

        .Axes(xlValue).TickLabels.Font.Size = 9

        .Axes(xlCategory).Format.Line.Visible = msoFalse

        .Axes(xlValue).MajorGridlines.Format.Line.ForeColor.RGB = RGB(220, 220, 220)

    End With

End Sub
Public Sub CrearGraficoResumen()

    Dim ch As ChartObject

    Set ch = CrearGrafico( _
            "CH_RESUMEN", _
            LayoutGrafico)

    With ch.Chart

        .ChartType = xlColumnClustered

    End With

    FormatearGrafico ch

End Sub
Public Sub CrearGraficoTurnos()

End Sub


Public Sub CrearGraficoHorasExtra()

End Sub


Public Sub CrearGraficoIncidencias()

End Sub


Public Sub ActualizarTodosLosGraficos()

    CrearGraficoResumen

End Sub


