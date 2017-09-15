script = """
[Setup]
AppId={{295B285B-3AA3-444B-8C60-17A61C7531B7}
AppName={#AppName}
AppVersion={#AppVersion}
;AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={pf}\\{#AppName}
DisableProgramGroupPage=yes
LicenseFile={$BuildDir}\\LICENSE
InfoBeforeFile={$BuildDir}\\README.md
OutputDir=Setups\\
OutputBaseFilename=GSF_Parser_{#AppVersion}
SetupIconFile={$BuildDir}\\assets\\logos\\icon_green.ico
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{$BuildDir}\\parser.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{$BuildDir}\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{commonprograms}\\{#AppName}"; Filename: "{app}\\{#AppExeName}"
Name: "{commondesktop}\\{#AppName}"; Filename: "{app}\\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange("{#AppName}", '&', '&&')}}"; Flags: nowait postinstall skipifsilent
"""