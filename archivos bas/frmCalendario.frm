VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmCalendario 
   ClientHeight    =   8595.001
   ClientLeft      =   120
   ClientTop       =   465
   ClientWidth     =   13125
   OleObjectBlob   =   "frmCalendario.frx":0000
   StartUpPosition =   1  'Centrar en propietario
End
Attribute VB_Name = "frmCalendario"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private FechaActual As Date
Private PrimeraFechaMes As Date

Private Sub UserForm_Initialize()

    FechaActual = Worksheets("01_CONFIG").Range("FECHA_DASHBOARD").Value

    MostrarMes

End Sub

Private Sub cmdAnterior_Click()

    FechaActual = DateAdd("m", -1, FechaActual)

    MostrarMes

End Sub

Private Sub cmdSiguiente_Click()

    FechaActual = DateAdd("m", 1, FechaActual)

    MostrarMes

End Sub

Private Sub MostrarMes()

    PrimeraFechaMes = DateSerial(Year(FechaActual), Month(FechaActual), 1)

    lblMes.Caption = UCase(Format(PrimeraFechaMes, "mmmm yyyy"))

    DibujarCalendario

End Sub
Private Sub DibujarCalendario()

    Dim c As Control

    For Each c In fraDias.Controls

        If TypeName(c) = "CommandButton" Then

            c.Caption = ""

            c.Enabled = False

        End If

    Next c

End Sub
