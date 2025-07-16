' Create a shortcut to a VBS script
Set objShell = CreateObject("WScript.Shell")
Set objShortcut = objShell.CreateShortcut("{out_dir}\{shortcut_name}.lnk")

' Configure the shortcut properties
objShortcut.TargetPath = "wscript.exe"
objShortcut.Arguments = """{shortcut_source}"""
objShortcut.WorkingDirectory = "{vbs_script_dir}"
objShortcut.Description = "{shortcut_name}"
objShortcut.IconLocation = "C:\Windows\System32\wscript.exe,0"

' Save the shortcut
objShortcut.Save