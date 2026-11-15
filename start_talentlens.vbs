Option Explicit
Dim shell, fso, root, probe, rc, pyCommand, scriptPath
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
scriptPath = Chr(34) & root & "\launcher.py" & Chr(34)
probe = shell.Run("cmd /c py -3 -c ""import sys""", 0, True)
If probe = 0 Then
  pyCommand = "py -3 " & scriptPath
Else
  probe = shell.Run("cmd /c python -c ""import sys""", 0, True)
  If probe = 0 Then
    pyCommand = "python " & scriptPath
  Else
    MsgBox "Python 3.10 or newer is required. Install Python from python.org and enable 'Add Python to PATH'.", vbExclamation, "TalentLens setup"
    WScript.Quit 1
  End If
End If
shell.CurrentDirectory = root
shell.Run "cmd /c " & pyCommand, 0, False
