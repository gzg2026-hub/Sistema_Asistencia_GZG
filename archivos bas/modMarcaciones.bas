Attribute VB_Name = "modMarcaciones"
Option Explicit

Private Const MARCA_ENTRADA As String = "Registro de entrada"
Private Const MARCA_SALIDA As String = "Registrar salida"
Private Const MARCA_HE_INI As String = "Inicio de horas extra"
Private Const MARCA_HE_FIN As String = "Fin de horas extra"

'==========================================================
' PROCESAR ENTRADAS Y SALIDAS
'==========================================================
Public Sub ProcesarMarcacion(ByRef M As clsMarcacionDia, _
                             ByVal Hora As Date, _
                             ByVal Tipo As String)

    Select Case Tipo

        Case MARCA_ENTRADA

            If Not M.TieneEntrada Then

                M.Entrada = Hora
                M.TieneEntrada = True

            Else

                AgregarIncidencia M, _
                    "Entrada duplicada (" & Format(Hora, "hh:mm") & ")", _
                    Hora

                If Hora < M.Entrada Then
                    M.Entrada = Hora
                End If

            End If

        Case MARCA_SALIDA

            If Not M.TieneSalida Then

                M.Salida = Hora
                M.TieneSalida = True

            Else

                AgregarIncidencia M, _
                    "Salida duplicada (" & Format(Hora, "hh:mm") & ")", _
                    Hora

                If Hora > M.Salida Then
                    M.Salida = Hora
                End If

            End If

        Case MARCA_HE_INI
            'Se procesa posteriormente

        Case MARCA_HE_FIN
            'Se procesa posteriormente

    End Select

End Sub

'==========================================================
' DETECTAR BLOQUES DE HORAS EXTRA
'==========================================================
Public Sub DetectarBloquesHE(ByRef M As clsMarcacionDia)

    Dim i As Long
    Dim InicioPendiente As Date

    Dim X As clsMarcacion
    Dim B As clsBloqueHE

    Set M.BloquesHE = New Collection

    InicioPendiente = 0

    For i = 1 To M.Marcaciones.Count

        Set X = M.Marcaciones(i)

        Select Case X.Tipo

            Case MARCA_HE_INI

                If Not M.TieneSalida Then

                    AgregarIncidencia M, _
                        "Inicio H.E. sin salida (" & _
                        Format(X.Hora, "hh:mm") & ")", _
                        X.Hora

                ElseIf X.Hora <= M.Salida Then

                    AgregarIncidencia M, _
                        "Inicio H.E. antes de la salida (" & _
                        Format(X.Hora, "hh:mm") & ")", _
                        X.Hora

                ElseIf InicioPendiente = 0 Then

                    InicioPendiente = X.Hora

                Else

                    AgregarIncidencia M, _
                        "Inicio H.E. duplicado (" & _
                        Format(X.Hora, "hh:mm") & ")", _
                        X.Hora

                End If

            Case MARCA_HE_FIN

                If InicioPendiente <> 0 Then

                    Set B = New clsBloqueHE

                    B.Inicio = InicioPendiente
                    B.Fin = X.Hora

                    If X.Hora < InicioPendiente Then
                        B.Duracion = (X.Hora + 1) - InicioPendiente
                    Else
                        B.Duracion = X.Hora - InicioPendiente
                    End If

                    If B.Duracion <= 0 Then

                        AgregarIncidencia M, _
                            "Bloque H.E. inválido (" & _
                            Format(B.Inicio, "hh:mm") & _
                            " - " & _
                            Format(B.Fin, "hh:mm") & ")", _
                            B.Fin

                    Else

                        M.BloquesHE.Add B

                    End If

                    InicioPendiente = 0

                Else

                    AgregarIncidencia M, _
                        "Fin H.E. sin inicio (" & _
                        Format(X.Hora, "hh:mm") & ")", _
                        X.Hora

                End If

        End Select

    Next i

    If InicioPendiente <> 0 Then

        AgregarIncidencia M, _
            "Inicio H.E. sin fin (" & _
            Format(InicioPendiente, "hh:mm") & ")", _
            InicioPendiente

    End If

End Sub

'==========================================================
' CARGAR TODAS LAS MARCACIONES DEL DÍA
'==========================================================
Public Sub CargarMarcaciones(ByRef M As clsMarcacionDia, _
                             ByVal wsMar As Worksheet)

    Dim f As Variant
    Dim X As clsMarcacion

    Set M.Marcaciones = New Collection

    For Each f In M.Filas

        Set X = New clsMarcacion

        X.Fila = CLng(f)
        X.Hora = wsMar.Cells(f, COL_MAR_HORA).Value
        X.Tipo = Trim(wsMar.Cells(f, COL_MAR_TIPO).Value)

        M.Marcaciones.Add X

    Next f

End Sub

