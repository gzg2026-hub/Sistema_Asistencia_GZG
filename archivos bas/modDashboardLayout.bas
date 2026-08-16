Attribute VB_Name = "modDashboardLayout"
Option Explicit

'=========================================================
' MODDASHBOARDLAYOUT
' Calcula todas las posiciones del Dashboard
'=========================================================

Public Type TRect

    Left As Double
    Top As Double
    Width As Double
    Height As Double

End Type

Public LayoutHeader As TRect

Public LayoutKPI(1 To KPI_COUNT) As TRect

Public LayoutGrafico As TRect

Public LayoutPersonal As TRect

Public LayoutEstado As TRect

Public LayoutAlertas As TRect

Public LayoutTabla As TRect

Public DashboardWidth As Double

Public DashboardHeight As Double

Public Sub InicializarLayout()

    DashboardWidth = HEADER_WIDTH

    DashboardHeight = 980

    Call CalcularHeader

    Call CalcularKPIs

    Call CalcularPaneles

    Call CalcularTabla

End Sub
Private Sub CalcularHeader()

    With LayoutHeader

        .Left = HEADER_LEFT

        .Top = HEADER_TOP

        .Width = HEADER_WIDTH

        .Height = HEADER_HEIGHT

    End With

End Sub


Private Sub CalcularKPIs()

    Dim i As Long

    Dim X As Double

    X = HEADER_LEFT

    For i = 1 To KPI_COUNT

        With LayoutKPI(i)

            .Left = X

            .Top = KPI_TOP

            .Width = KPI_WIDTH

            .Height = KPI_HEIGHT

        End With

        X = X + KPI_WIDTH + KPI_GAP

    Next i

End Sub
Private Sub CalcularPaneles()

    With LayoutGrafico

        .Left = HEADER_LEFT

        .Top = PANEL_TOP

        .Width = PANEL_LEFT_WIDTH

        .Height = PANEL_HEIGHT

    End With


    With LayoutPersonal

        .Left = HEADER_LEFT + PANEL_LEFT_WIDTH + PANEL_GAP

        .Top = PANEL_TOP

        .Width = PANEL_RIGHT_WIDTH

        .Height = PANEL_HEIGHT

    End With


    With LayoutEstado

        .Left = HEADER_LEFT

        .Top = PANEL_TOP + PANEL_HEIGHT + PANEL_GAP

        .Width = PANEL_LEFT_WIDTH

        .Height = PANEL_HEIGHT

    End With


    With LayoutAlertas

        .Left = HEADER_LEFT + PANEL_LEFT_WIDTH + PANEL_GAP

        .Top = PANEL_TOP + PANEL_HEIGHT + PANEL_GAP

        .Width = PANEL_RIGHT_WIDTH

        .Height = PANEL_HEIGHT

    End With

End Sub
Private Sub CalcularTabla()

    With LayoutTabla

        .Left = HEADER_LEFT

        .Top = PANEL_TOP + PANEL_HEIGHT * 2 + PANEL_GAP * 2 + TABLE_TOP_GAP

        .Width = HEADER_WIDTH

        .Height = TABLE_HEIGHT

    End With

End Sub
