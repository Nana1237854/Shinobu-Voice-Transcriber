# coding:utf-8
from qfluentwidgets import (SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, PushSettingCard,
                            HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, CustomColorSettingCard,
                            setTheme, setThemeColor, isDarkTheme, setFont, PushButton,
                            IndeterminateProgressBar, SettingCard)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import SettingCardGroup as CardGroup
from qfluentwidgets import InfoBar
from PySide6.QtCore import Qt, Signal, QUrl, QStandardPaths, QThread
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import QWidget, QLabel, QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox

from ..common.config import cfg, isWin11
from ..common.setting import HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR
from ..common.signal_bus import signalBus
from ..common.style_sheet import StyleSheet
from ..service.download_service import downloadService
from ..service.version_service import versionService


class VersionCheckThread(QThread):
    """版本检查线程"""
    finished = Signal(bool, dict)  # (has_new_version, update_info)
    error = Signal(str)
    
    def run(self):
        """在线程中执行版本检查"""
        try:
            has_new = versionService.hasNewVersion()
            if has_new:
                info = versionService.getUpdateInfo()
            else:
                info = {
                    'version': versionService.currentVersion,
                    'name': VERSION,
                    'body': '',
                    'html_url': HELP_URL
                }
            self.finished.emit(has_new, info)
        except Exception as e:
            self.error.emit(str(e))


class SettingCardGroup(CardGroup):

   def __init__(self, title: str, parent=None):
       super().__init__(title, parent)
       setFont(self.titleLabel, 14, QFont.Weight.DemiBold)


class DownloadSettingCard(SettingCard):
    """带下载按钮和进度条的设置卡片"""
    
    clicked = Signal()
    
    def __init__(self, icon, title, content, parent=None):
        super().__init__(icon, title, content, parent)
        
        # 创建按钮
        self.button = PushButton(self.tr('Download'), self)
        self.button.setFixedWidth(120)
        self.button.clicked.connect(self.clicked)
        
        # 创建进度条
        self.progressBar = IndeterminateProgressBar(self)
        self.progressBar.setFixedHeight(3)
        self.progressBar.hide()
        self.progressBar.stop()
        
        # 添加按钮到水平布局
        self.hBoxLayout.addWidget(self.button, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        
        # 获取卡片的主布局（vBoxLayout）并添加进度条
        # SettingCard 的结构是 vBoxLayout 包含 hBoxLayout
        # 我们需要在 hBoxLayout 下方添加进度条
        if hasattr(self, 'vBoxLayout'):
            self.vBoxLayout.addWidget(self.progressBar)
    
    def setDownloading(self, isDownloading: bool):
        """设置下载状态"""
        if isDownloading:
            self.button.setText(self.tr('Downloading...'))
            self.button.setEnabled(False)
            self.progressBar.show()
            self.progressBar.start()
        else:
            self.button.setEnabled(True)
            self.progressBar.stop()
            self.progressBar.hide()
    
    def setInstalled(self):
        """标记为已安装"""
        self.button.setText(self.tr('Installed'))
        self.button.setEnabled(False)
        self.progressBar.hide()
        self.progressBar.stop()
    
    def setDownloadable(self):
        """标记为可下载"""
        self.button.setText(self.tr('Download'))
        self.button.setEnabled(True)
        self.progressBar.hide()
        self.progressBar.stop()



class SettingInterface(ScrollArea):
    """ Setting interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        
        # download threads
        self.ffmpegDownloadThread = None
        self.whisperDownloadThread = None
        
        # version check thread
        self.versionCheckThread = None

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # personalization
        self.personalGroup = SettingCardGroup(
            self.tr('Personalization'), self.scrollWidget)
        self.micaCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr('Mica effect'),
            self.tr('Apply semi transparent to windows and surfaces'),
            cfg.micaEnabled,
            self.personalGroup
        )
        self.themeCard = ComboBoxSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        self.zoomCard = ComboBoxSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )

        # download dependencies
        self.downloadGroup = SettingCardGroup(
            self.tr('Download Dependencies'), self.scrollWidget)
        self.downloadFFmpegCard = DownloadSettingCard(
            FIF.DOWNLOAD,
            'FFmpeg',
            self.tr('Download FFmpeg for audio/video processing'),
            self.downloadGroup
        )
        self.downloadWhisperCard = DownloadSettingCard(
            FIF.DOWNLOAD,
            'Whisper-Faster-XXL',
            self.tr('Download Whisper-Faster-XXL for speech transcription'),
            self.downloadGroup
        )

        # update software
        self.updateSoftwareGroup = SettingCardGroup(
            self.tr("Software update"), self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            self.tr('Check for updates when the application starts'),
            self.tr('The new version will be more stable and have more features'),
            configItem=cfg.checkUpdateAtStartUp,
            parent=self.updateSoftwareGroup
        )
        self.checkUpdateCard = PrimaryPushSettingCard(
            self.tr('Check for updates'),
            FIF.UPDATE,
            self.tr('Check for updates'),
            self.tr('Current version: ') + VERSION,
            self.updateSoftwareGroup
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.helpCard = HyperlinkCard(
            HELP_URL,
            self.tr('Open help page'),
            FIF.HELP,
            self.tr('Help'),
            self.tr(
                'Discover new features and learn useful tips about Shinobu-Voice-Transcriber'),
            self.aboutGroup
        )
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('Provide feedback'),
            FIF.FEEDBACK,
            self.tr('Provide feedback'),
            self.tr('Help us improve Shinobu-Voice-Transcriber by providing feedback'),
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('About'),
            "app/resource/images/logo.ico",
            self.tr('About'),
            '© ' + self.tr('Copyright') + f" {YEAR}, {AUTHOR}. " +
            self.tr('Version') + " " + VERSION,
            self.aboutGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 100, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        # initialize style sheet
        setFont(self.settingLabel, 23, QFont.Weight.DemiBold)
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)
        self.scrollWidget.setStyleSheet("QWidget{background:transparent}")

        self.micaCard.setEnabled(isWin11())

        # initialize download cards status
        self._updateDownloadCardsStatus()

        # initialize layout
        self.__initLayout()
        self._connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(36, 50)

        self.personalGroup.addSettingCard(self.micaCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.downloadGroup.addSettingCard(self.downloadFFmpegCard)
        self.downloadGroup.addSettingCard(self.downloadWhisperCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)
        self.updateSoftwareGroup.addSettingCard(self.checkUpdateCard)

        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.downloadGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def _showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.success(
            self.tr('Updated successfully'),
            self.tr('Configuration takes effect after restart'),
            duration=1500,
            parent=self
        )

    def _connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self._showRestartTooltip)

        # personalization
        cfg.themeChanged.connect(setTheme)
        self.micaCard.checkedChanged.connect(signalBus.micaEnableChanged)

        # download
        self.downloadFFmpegCard.clicked.connect(self._onDownloadFFmpegClicked)
        self.downloadWhisperCard.clicked.connect(self._onDownloadWhisperClicked)

        # check update
        self.checkUpdateCard.clicked.connect(self._onCheckUpdateClicked)

        # about
        self.aboutCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(HELP_URL)))
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))

    def _updateDownloadCardsStatus(self):
        """ Update download cards button text and status """
        # Update FFmpeg card
        if downloadService.check_ffmpeg_exists():
            self.downloadFFmpegCard.setInstalled()
        else:
            self.downloadFFmpegCard.setDownloadable()
        
        # Update Whisper-Faster card
        if downloadService.check_whisper_faster_exists():
            self.downloadWhisperCard.setInstalled()
        else:
            self.downloadWhisperCard.setDownloadable()

    def _onDownloadFFmpegClicked(self):
        """ Handle FFmpeg download button click """
        if self.ffmpegDownloadThread and self.ffmpegDownloadThread.isRunning():
            return
        
        self.downloadFFmpegCard.setDownloading(True)
        
        InfoBar.info(
            self.tr('Download started'),
            self.tr('Downloading FFmpeg, please wait...'),
            duration=2000,
            parent=self
        )
        
        self.ffmpegDownloadThread = downloadService.create_ffmpeg_download_thread()
        self.ffmpegDownloadThread.finished.connect(self._onFFmpegDownloadFinished)
        self.ffmpegDownloadThread.start()

    def _onDownloadWhisperClicked(self):
        """ Handle Whisper-Faster download button click """
        if self.whisperDownloadThread and self.whisperDownloadThread.isRunning():
            return
        
        self.downloadWhisperCard.setDownloading(True)
        
        InfoBar.info(
            self.tr('Download started'),
            self.tr('Downloading Whisper-Faster-XXL, please wait...'),
            duration=2000,
            parent=self
        )
        
        self.whisperDownloadThread = downloadService.create_whisper_download_thread()
        self.whisperDownloadThread.finished.connect(self._onWhisperDownloadFinished)
        self.whisperDownloadThread.start()

    def _onFFmpegDownloadFinished(self, success, message):
        """ Handle FFmpeg download finished """
        self.downloadFFmpegCard.setDownloading(False)
        
        if success:
            InfoBar.success(
                self.tr('Download completed'),
                self.tr('FFmpeg has been successfully downloaded and installed'),
                duration=3000,
                parent=self
            )
        else:
            InfoBar.error(
                self.tr('Download failed'),
                self.tr('Failed to download FFmpeg: ') + message,
                duration=5000,
                parent=self
            )
        
        self._updateDownloadCardsStatus()

    def _onWhisperDownloadFinished(self, success, message):
        """ Handle Whisper-Faster download finished """
        self.downloadWhisperCard.setDownloading(False)
        
        if success:
            InfoBar.success(
                self.tr('Download completed'),
                self.tr('Whisper-Faster-XXL has been successfully downloaded and installed'),
                duration=3000,
                parent=self
            )
        else:
            InfoBar.error(
                self.tr('Download failed'),
                self.tr('Failed to download Whisper-Faster-XXL: ') + message,
                duration=5000,
                parent=self
            )
        
        self._updateDownloadCardsStatus()

    def _onCheckUpdateClicked(self):
        """检查更新按钮点击事件"""
        # 检查是否已有版本检查线程在运行
        if self.versionCheckThread and self.versionCheckThread.isRunning():
            InfoBar.warning(
                self.tr('Checking in progress'),
                self.tr('Version check is in progress, please wait...'),
                duration=2000,
                parent=self
            )
            return
        
        # 显示检查中提示
        InfoBar.info(
            self.tr('Checking for updates'),
            self.tr('Please wait...'),
            duration=2000,
            parent=self
        )
        
        # 创建并启动版本检查线程
        self.versionCheckThread = VersionCheckThread()
        self.versionCheckThread.finished.connect(self._onVersionCheckFinished)
        self.versionCheckThread.error.connect(self._onVersionCheckError)
        self.versionCheckThread.start()

    def _onVersionCheckFinished(self, has_new_version: bool, info: dict):
        """版本检查完成回调"""
        if has_new_version:
            # 有新版本
            version = info.get('version', 'Unknown')
            body = info.get('body', '')
            html_url = info.get('html_url', '')
            
            InfoBar.success(
                self.tr('New version found!'),
                self.tr('Version {version} has been released').format(version=f"v{version}"),
                duration=5000,
                parent=self
            )
            
            # 构建消息内容
            message = self.tr('New version {version} found\n\n').format(version=f"v{version}")
            if body:
                # 限制更新说明长度
                body_preview = body[:200]
                if len(body) > 200:
                    body_preview += "..."
                message += self.tr('Release notes:\n{notes}\n\n').format(notes=body_preview)
            message += self.tr('Do you want to go to the download page?')
            
            # 询问是否跳转到下载页面
            reply = QMessageBox.question(
                self,
                self.tr('New version found'),
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl(html_url))
        else:
            # 已是最新版本
            InfoBar.success(
                self.tr('Already up to date'),
                self.tr('Current version {version} is the latest').format(version=f"v{versionService.currentVersion}"),
                duration=3000,
                parent=self
            )

    def _onVersionCheckError(self, error_message: str):
        """版本检查错误回调"""
        InfoBar.error(
            self.tr('Update check failed'),
            self.tr('Unable to connect to update server: ') + error_message,
            duration=5000,
            parent=self
        )
