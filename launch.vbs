' PyLab launcher (project copy, ASCII only for WSH compatibility).
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
projectDir = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = projectDir
cmd = """" & projectDir & "\launch.bat"" --silent"
rc = shell.Run(cmd, 0, True)
If rc <> 0 Then
    MsgBox "PyLab failed to start. See data\server.log", 16, "PyLab"
End If
