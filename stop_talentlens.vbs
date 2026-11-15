Option Explicit
Dim shell, fso, root, probe, command
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
probe = shell.Run("cmd /c py -3 -c ""import sys""", 0, True)
If probe = 0 Then
  command = "py -3 """ & root & "\stop.py"""
Else
  command = "python """ & root & "\stop.py"""
End If
shell.CurrentDirectory = root
shell.Run "cmd /c " & command, 0, True
