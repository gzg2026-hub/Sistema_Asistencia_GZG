Attribute VB_Name = "modConfig"
Option Explicit

Public HoraInicioDia As Date
Public HoraFinDia As Date

Public HoraInicioNoche As Date
Public HoraFinNoche As Date

Public ToleranciaEntrada As Long
Public ToleranciaSalida As Long

Public HorasMinimas As Double

Public Sub CargarConfiguracion()

    Dim ws As Worksheet

    Set ws = Worksheets(SH_CONFIG)

    HoraInicioDia = CDate(ws.Range("B2").Value)
    HoraFinDia = CDate(ws.Range("B3").Value)

    HoraInicioNoche = CDate(ws.Range("B4").Value)
    HoraFinNoche = CDate(ws.Range("B5").Value)

    HorasMinimas = CDbl(ws.Range("B6").Value)

    ToleranciaEntrada = CLng(ws.Range("B7").Value)
    ToleranciaSalida = CLng(ws.Range("B8").Value)

End Sub
