Attribute VB_Name = "modTrabajadores"
Option Explicit

Private DicTrabajadores As Object

'==========================================================
' CARGAR ÍNDICE DE TRABAJADORES
'==========================================================
Public Sub CargarTrabajadores()

    Dim ws As Worksheet
    Dim UltFila As Long
    Dim i As Long
    Dim DNI As String

    Set DicTrabajadores = CreateObject("Scripting.Dictionary")

    Set ws = Worksheets(SH_TRABAJADORES)

    UltFila = ws.Cells(ws.Rows.Count, COL_TRAB_DNI).End(xlUp).Row

    For i = 2 To UltFila

        DNI = Trim(CStr(ws.Cells(i, COL_TRAB_DNI).Value))

        If Len(DNI) > 0 Then

            If DicTrabajadores.Exists(DNI) Then

                Err.Raise vbObjectError + 1000, _
                          "CargarTrabajadores", _
                          "DNI duplicado encontrado." & vbCrLf & _
                          "Hoja: " & SH_TRABAJADORES & vbCrLf & _
                          "DNI: " & DNI & vbCrLf & _
                          "Fila: " & i

            Else

                DicTrabajadores.Add DNI, i

            End If

        End If

    Next i

End Sub

'==========================================================
' BUSCAR TRABAJADOR
'==========================================================
Public Function BuscarTrabajador(ByVal DNI As String) As Long

    DNI = Trim(CStr(DNI))

    If DicTrabajadores Is Nothing Then
        CargarTrabajadores
    End If

    If DicTrabajadores.Exists(DNI) Then

        BuscarTrabajador = DicTrabajadores(DNI)

    Else

        Err.Raise vbObjectError + 1001, _
                  "BuscarTrabajador", _
                  "El DNI " & DNI & " no existe en la hoja " & SH_TRABAJADORES & "."

    End If

End Function

