VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "clsIncidencia"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = False
Option Explicit

'=========================================
' DATOS DE UNA INCIDENCIA
'=========================================
Public Fecha As Date
Public DNI As String

Public Tipo As String
Public Descripcion As String

Public Hora As Date

Public Severidad As String
Public Observacion As String
