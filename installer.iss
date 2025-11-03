#define MyAppName "Shinobu Voice Transcriber"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "Shinobu Voice Transcriber"
#define MyAppURL "https://github.com/Nana1237854/Shinobu-Voice-Transcriber"
#define MyAppExeName "Shinobu-Voice-Transcriber.exe"

[Setup]
; 基本信息
AppId={{A5B6C7D8-E9F0-1234-5678-90ABCDEF1234}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
InfoBeforeFile=README.md
OutputDir=installer_output
OutputBaseFilename=Shinobu-Voice-Transcriber-Setup-v{#MyAppVersion}
SetupIconFile=app\resource\images\logo.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
; 权限设置
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; 主程序及所有依赖文件
Source: "dist\Shinobu-Voice-Transcriber.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; 许可证和说明文件
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
; 开始菜单快捷方式
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; 桌面快捷方式（可选）
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon
; 快速启动栏快捷方式（可选）
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: quicklaunchicon

[Run]
; 安装完成后运行程序（可选）
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时删除配置文件和日志
Type: filesandordirs; Name: "{userappdata}\{#MyAppName}"
Type: files; Name: "{app}\*.log"

[Code]
var
  DataDirPage: TInputDirWizardPage;

procedure InitializeWizard;
begin
  { 创建自定义页面询问数据目录 }
  DataDirPage := CreateInputDirPage(wpSelectDir,
    '选择数据目录', '请选择存储模型和配置文件的目录',
    '模型文件可能会占用较大空间。建议选择空间充足的磁盘位置。' + #13#10 +
    '如果不确定，可以使用默认位置。',
    False, '');
  DataDirPage.Add('模型数据目录：');
  DataDirPage.Values[0] := ExpandConstant('{userdocs}\{#MyAppName}\Models');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = DataDirPage.ID then
  begin
    { 验证目录是否有效 }
    if not DirExists(DataDirPage.Values[0]) then
    begin
      if MsgBox('目录不存在，是否创建？', mbConfirmation, MB_YESNO) = IDYES then
      begin
        if not CreateDir(DataDirPage.Values[0]) then
        begin
          MsgBox('无法创建目录，请选择其他位置。', mbError, MB_OK);
          Result := False;
        end;
      end
      else
        Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: String;
  ConfigContent: TStringList;
begin
  if CurStep = ssPostInstall then
  begin
    { 创建配置文件，保存数据目录路径 }
    ConfigFile := ExpandConstant('{app}\config.ini');
    ConfigContent := TStringList.Create;
    try
      ConfigContent.Add('[Paths]');
      ConfigContent.Add('DataDir=' + DataDirPage.Values[0]);
      ConfigContent.SaveToFile(ConfigFile);
    finally
      ConfigContent.Free;
    end;
  end;
end;

[CustomMessages]
english.AdditionalIcons=Additional icons:
english.CreateDesktopIcon=Create a &desktop icon
english.CreateQuickLaunchIcon=Create a &Quick Launch icon
english.LaunchProgram=Launch %1
english.UninstallProgram=Uninstall %1

