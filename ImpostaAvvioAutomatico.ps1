$WshShell = New-Object -ComObject WScript.Shell
$ShortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\BotCalcolo.lnk"
$TargetPath = "c:\Users\angio\Documents\trae_projects\Bot Calcolo\AvviaBot.bat"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = "c:\Users\angio\Documents\trae_projects\Bot Calcolo"
$Shortcut.IconLocation = "shell32.dll,13"
$Shortcut.Save()

Write-Host "✅ Bot aggiunto all'avvio automatico di Windows!" -ForegroundColor Green
Write-Host "Ora il bot si aprirà automaticamente ogni volta che accendi il PC."
pause
