Attribute VB_Name = "modImportacion"
Option Explicit

Public Sub Importar_HikCentral()

    Dim Archivo As Variant
    Dim wbOrigen As Workbook
    Dim wsOrigen As Worksheet
    Dim wsDestino As Worksheet
    Dim UltFila As Long
    Dim UltCol As Long

    On Error GoTo ErrorHandler

    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.DisplayAlerts = False

    Archivo = Application.GetOpenFilename( _
        "Archivos Excel (*.xlsx),*.xlsx", _
        , "Seleccione el reporte de HikCentral")

    If Archivo = False Then GoTo Salir

    Set wbOrigen = Workbooks.Open(Archivo)
    Set wsOrigen = wbOrigen.Sheets(1)

    Set wsDestino = ThisWorkbook.Sheets("03_MARCACIONES")

    'Limpiar únicamente el contenido
    wsDestino.Cells.ClearContents

    'Obtener última fila y última columna
    UltFila = wsOrigen.Cells(wsOrigen.Rows.Count, 1).End(xlUp).Row
    UltCol = wsOrigen.Cells(8, wsOrigen.Columns.Count).End(xlToLeft).Column

    'Copiar datos desde la fila 8
    wsOrigen.Range( _
        wsOrigen.Cells(8, 1), _
        wsOrigen.Cells(UltFila, UltCol) _
    ).Copy

    wsDestino.Range("A1").PasteSpecial Paste:=xlPasteValues

    Application.CutCopyMode = False

    MsgBox "Importación finalizada correctamente.", vbInformation

Salir:

    On Error Resume Next

    If Not wbOrigen Is Nothing Then
        wbOrigen.Close SaveChanges:=False
    End If

    Application.CutCopyMode = False
    Application.ScreenUpdating = True
    Application.EnableEvents = True
    Application.DisplayAlerts = True

    Exit Sub

ErrorHandler:

    MsgBox "Error durante la importación:" & vbCrLf & _
           Err.Number & " - " & Err.Description, vbCritical

    Resume Salir

End Sub

