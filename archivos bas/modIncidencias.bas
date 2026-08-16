Attribute VB_Name = "modIncidencias"
Option Explicit

'==========================================================
' AGREGAR INCIDENCIA
'==========================================================
Public Sub AgregarIncidencia(ByRef M As clsMarcacionDia, _
                             ByVal Texto As String, _
                             Optional ByVal Hora As Date = 0)

    Dim i As clsIncidencia

    Set i = New clsIncidencia

    i.Fecha = M.Fecha
    i.DNI = M.DNI
    i.Descripcion = Texto
    i.Hora = Hora
    i.Observacion = ""

    Select Case True

        Case InStr(1, Texto, "Entrada", vbTextCompare) > 0

            i.Tipo = "ENTRADA"
            i.Severidad = "MEDIA"

        Case InStr(1, Texto, "Salida", vbTextCompare) > 0

            i.Tipo = "SALIDA"
            i.Severidad = "MEDIA"

        Case InStr(1, Texto, "H.E.", vbTextCompare) > 0

            i.Tipo = "HORAS EXTRA"
            i.Severidad = "ALTA"

        Case Else

            i.Tipo = "GENERAL"
            i.Severidad = "BAJA"

    End Select

    M.ListaIncidencias.Add i

    If Len(M.Incidencias) = 0 Then
        M.Incidencias = Texto
    Else
        M.Incidencias = M.Incidencias & "; " & Texto
    End If

End Sub

'==========================================================
' ESCRIBIR INCIDENCIAS
'==========================================================
Public Sub EscribirIncidencias(ByVal M As clsMarcacionDia)

    Dim ws As Worksheet
    Dim Fila As Long
    Dim i As clsIncidencia
    Dim filaTrab As Long

    Set ws = Worksheets(SH_INCIDENCIAS)

    For Each i In M.ListaIncidencias

        Fila = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row + 1

        If Fila < 2 Then Fila = 2

        ws.Cells(Fila, 1).Value = i.Fecha
        ws.Cells(Fila, 2).Value = i.DNI

        filaTrab = M.FilaTrabajador

        If filaTrab > 0 Then

            With Worksheets(SH_TRABAJADORES)

                ws.Cells(Fila, 3).Value = .Cells(filaTrab, COL_TRAB_APELLIDOS).Value
                ws.Cells(Fila, 4).Value = .Cells(filaTrab, COL_TRAB_NOMBRES).Value

            End With

        End If

        ws.Cells(Fila, 5).Value = i.Tipo

        If i.Hora <> 0 Then

            ws.Cells(Fila, 6).Value = i.Hora
            ws.Cells(Fila, 6).NumberFormat = "hh:mm"

        End If

        ws.Cells(Fila, 7).Value = i.Descripcion
        ws.Cells(Fila, 8).Value = i.Severidad
        ws.Cells(Fila, 9).Value = i.Observacion

    Next i

End Sub

