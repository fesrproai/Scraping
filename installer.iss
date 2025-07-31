[Setup]
AppName=DescuentosCL
AppVersion=1.0
AppPublisher=DescuentosCL Team
AppPublisherURL=https://github.com/descuentoscl
AppSupportURL=https://github.com/descuentoscl/issues
AppUpdatesURL=https://github.com/descuentoscl/releases
DefaultDirName={autopf}\DescuentosCL
DefaultGroupName=DescuentosCL
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer
OutputBaseFilename=DescuentosCL_Setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\DescuentosCL.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "scrapers\*"; DestDir: "{app}\scrapers"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "core\*"; DestDir: "{app}\core"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "database\*"; DestDir: "{app}\database"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "scheduler\*"; DestDir: "{app}\scheduler"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "api\*"; DestDir: "{app}\api"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "utils\*"; DestDir: "{app}\utils"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "frontend\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: ".env.example"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "INSTALACION.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "DescuentosCL.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\DescuentosCL"; Filename: "{app}\DescuentosCL.exe"
Name: "{group}\{cm:UninstallProgram,DescuentosCL}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\DescuentosCL"; Filename: "{app}\DescuentosCL.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\DescuentosCL"; Filename: "{app}\DescuentosCL.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\DescuentosCL.exe"; Description: "{cm:LaunchProgram,DescuentosCL}"; Flags: nowait postinstall skipifsilent
Filename: "{app}\DescuentosCL.bat"; Description: "Abrir menú principal"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  // Verificar si Python está instalado
  if not DirExists(ExpandConstant('{pf}\Python*')) and not DirExists(ExpandConstant('{localappdata}\Programs\Python\Python*')) then
  begin
    MsgBox('Python no está instalado. Por favor instala Python 3.8+ desde https://www.python.org/downloads/', mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Crear archivo .env si no existe
    if not FileExists(ExpandConstant('{app}\.env')) then
    begin
      FileCopy(ExpandConstant('{app}\.env.example'), ExpandConstant('{app}\.env'), False);
    end;
  end;
end; 