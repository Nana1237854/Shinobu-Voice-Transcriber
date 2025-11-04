from PySide6.QtCore import Qt, QThread, Signal, QCoreApplication
from PySide6.QtGui import QDropEvent, QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QHBoxLayout

from qfluentwidgets import (
    ScrollArea, InfoBar, InfoBarPosition, GroupHeaderCardWidget,
    PushButton, PrimaryPushButton, ComboBox, FluentIcon, InfoBarIcon,
    IconWidget, BodyLabel, SimpleCardWidget, ImageLabel, TitleLabel, PillPushButton, setFont, SwitchButton, CompactSpinBox
)

from ..service.transcription_service import transcriptionService, WhisperEngine, OutputFormat
from ..common.signal_bus import signalBus
from ..common.config import cfg


class TranscriptionWorker(QThread):
    """转录工作线程"""
    finished = Signal(dict)  # 完成信号，传递结果字典
    error = Signal(str)      # 错误信号，传递错误消息
    
    def __init__(self, input_path: str, **kwargs):
        super().__init__()
        self.input_path = input_path
        self.kwargs = kwargs
    
    def run(self):
        """在线程中执行转录"""
        try:
            result = transcriptionService.transcribe(self.input_path, **self.kwargs)
            if result:
                self.finished.emit(result)
            else:
                self.error.emit(QCoreApplication.translate("TranscriptionWorker", "Transcription failed, no result returned"))
        except Exception as e:
            self.error.emit(str(e))


class TranscribeConfigCard(GroupHeaderCardWidget):
    """听写配置卡片"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Transcribe Settings"))
        self.mediaParser = None

        self.targetFileButton = PushButton(self.tr("Select"))
        self.transcribeModelComboBox = ComboBox()
        self.inputLanguageComboBox = ComboBox()
        self.timeStampButton = SwitchButton(self.tr("Close"), self)
        self.outputFileTypeComBox = ComboBox()
        self.averageCompactSpinBox = CompactSpinBox()
        self.saveFolderButton = PushButton(self.tr("Select"), self, FluentIcon.FOLDER)
        self.openModelsButton = PushButton(self.tr("Open Model Directory"), self, FluentIcon.FOLDER)
        
        self.hintIcon = IconWidget(InfoBarIcon.INFORMATION, self)
        self.hintLabel = BodyLabel(
            self.tr("Click the transcribe button to start transcribing") + ' 👉')
        self.transcribeButton = PrimaryPushButton(
            self.tr("Transcribe"), self, FluentIcon.PLAY_SOLID)
        
        self.toolBarLayout = QHBoxLayout()

        self._initWidgets()

    def _initWidgets(self):
        self.setBorderRadius(8)

        self.targetFileButton.setFixedWidth(120)
        self.transcribeModelComboBox.setFixedWidth(320)
        self.inputLanguageComboBox.setFixedWidth(320)
        
        # 动态加载 Whisper 模型列表
        self._loadWhisperModels()
        
        self.inputLanguageComboBox.addItems([
            self.tr("Chinese"), self.tr("Japanese"), self.tr("English"), 
            self.tr("Korean"), self.tr("Russian"), self.tr("French")
        ])
        self.outputFileTypeComBox.addItems([
            self.tr("Original SRT"), self.tr("Bilingual SRT"), self.tr("Original LRC"), 
            self.tr("Original TXT"), self.tr("Bilingual TXT"), self.tr("Original XLSX"), 
            self.tr("Bilingual XLSX")
        ])
        
        # 更改按钮状态 - 默认关闭
        self.timeStampButton.setChecked(False)
        self.timeStampButton.setOffText(self.tr("Close"))
        self.timeStampButton.setOnText(self.tr("Open"))

        self.averageCompactSpinBox.setRange(0, 10)
        self.averageCompactSpinBox.setValue(0)
        
        self.openModelsButton.setFixedWidth(160)

        self._initLayout()
    
    def _loadWhisperModels(self):
        """加载可用的 Whisper 模型到下拉菜单"""
        
        # 获取可用模型列表
        available_models = transcriptionService.get_available_models()
        
        # 添加基础选项
        model_items = []
        
        # 如果有扫描到的模型，添加到列表
        if available_models:
            print(f"[UI] 加载 {len(available_models)} 个可用模型到下拉菜单")
            for model in available_models:
                # 生成用户友好的显示名称
                if model.startswith('faster-whisper-'):
                    display_name = f"Faster-Whisper ({model[15:]})"
                else:
                    display_name = model
                model_items.append(display_name)
        
        # 如果没有扫描到模型，添加默认选项
        if not model_items:
            model_items = ["whisper", "whisper-faster(仅限N卡)"]
            print("[UI] 未扫描到模型，使用默认选项")
        
        self.transcribeModelComboBox.addItems(model_items)
        
        # 保存模型映射关系（显示名称 -> 实际模型名）
        self._model_name_map = {}
        if available_models:
            for model, display in zip(available_models, model_items):
                self._model_name_map[display] = model
    
    def getSelectedModel(self) -> str:
        """
        获取用户选择的模型名称（实际模型名，非显示名）
        
        Returns:
            模型名称
        """
        display_name = self.transcribeModelComboBox.currentText()
        
        # 如果有映射关系，返回实际模型名
        if hasattr(self, '_model_name_map') and display_name in self._model_name_map:
            return self._model_name_map[display_name]
        
        # 否则返回显示名
        return display_name

    
    def _initLayout(self):
        # 添加小组件在卡片中
        self.targetFileGroup = self.addGroup(
            icon=FluentIcon.DOCUMENT,
            title=self.tr("Target File"),
            content=self.tr("Select the file to transcribe"),
            widget=self.targetFileButton
        )
        self.addGroup(
            icon=FluentIcon.IOT,
            title=self.tr("Transcribe Model"),
            content=self.tr("Select the model category for transcribing"),
            widget=self.transcribeModelComboBox
        )
        self.addGroup(
            icon=FluentIcon.LANGUAGE,
            title=self.tr("Input Language"),
            content=self.tr("Select the input language"),
            widget=self.inputLanguageComboBox
        )
        self.addGroup(
            icon=FluentIcon.UNIT.icon(),
            title=self.tr("Timestamp"),
            content=self.tr("Generate timestamp (only used for quick location of original sentence, not guaranteed to be accurate)"),
            widget=self.timeStampButton
        )
        self.addGroup(
            icon=FluentIcon.SAVE,
            title=self.tr("Output File"),
            content=self.tr("Select the output file"),
            widget=self.outputFileTypeComBox
        )
        self.addGroup(
            icon=FluentIcon.CLIPPING_TOOL.icon(),
            title=self.tr("Split Audio"),
            content=self.tr("Split audio by number of people (used for subtitle group quick分工)\nNote: Duration is rounded up; if divisible, split evenly, otherwise the remainder is given to the last person"),
            widget=self.averageCompactSpinBox
        )
        self.saveFolderGroup = self.addGroup(
            icon=FluentIcon.FOLDER,
            title=self.tr("Save Folder"),
            content=cfg.get(cfg.saveFolder),
            widget=self.saveFolderButton
        )
        self.addGroup(
            icon=FluentIcon.FOLDER_ADD,
            title=self.tr("Model Management"),
            content=self.tr("Open the model folder, add or manage Whisper models"),
            widget=self.openModelsButton
        )
        

        # 设置底部工具栏布局
        self.toolBarLayout.setContentsMargins(24, 15, 24, 20)
        self.toolBarLayout.setSpacing(10)
        self.toolBarLayout.addWidget(
            self.hintIcon, 0, Qt.AlignmentFlag.AlignLeft)
        self.toolBarLayout.addWidget(
            self.hintLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.toolBarLayout.addStretch(1)
        self.toolBarLayout.addWidget(
            self.transcribeButton, 0, Qt.AlignmentFlag.AlignRight)
        self.toolBarLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.vBoxLayout.addLayout(self.toolBarLayout)

class TranscribeModeInfoCard(SimpleCardWidget):
    """听写模式信息卡片"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBorderRadius(8)

        self.iconLabel = ImageLabel(QIcon("app/resource/images/logo.png").pixmap(100, 100), self)

        self.nameLabel = TitleLabel(self.tr("Transcribe Mode"), self)

        self.descriptionLabel = BodyLabel(
            self.tr("Transcribe mode workflow:\nSelect transcribe file -> Select transcribe model -> Select input language -> Select output file -> Select save folder -> Click the transcribe button to transcribe")
        )

        self.tagWhisperButton = PillPushButton(self.tr("whisper"), self)
        self.tagWhisperfasterButton = PillPushButton(self.tr("whisper-faster"), self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        self.topLayout = QHBoxLayout()
        self.tagsLayout = QHBoxLayout()
        self.statisticsLayout = QHBoxLayout()
        self.buttonLayout = QHBoxLayout()

        self.__initWidgets()
    
    def __initWidgets(self):
        self.iconLabel.setBorderRadius(8, 8, 8, 8)
        self.iconLabel.scaledToWidth(80)

        self.descriptionLabel.setWordWrap(True)     # 自动换行

        self.tagWhisperButton.setCheckable(False)
        setFont(self.tagWhisperButton, 12)
        self.tagWhisperButton.setFixedSize(80, 32)

        self.tagWhisperfasterButton.setCheckable(False)
        setFont(self.tagWhisperfasterButton, 12)
        self.tagWhisperfasterButton.setFixedSize(120, 32)

        self.nameLabel.setObjectName("nameLabel")
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.initLayout()

    def initLayout(self):
        # 主水平布局：图标在左，内容在右
        self.hBoxLayout.setSpacing(20)
        self.hBoxLayout.setContentsMargins(24, 20, 24, 20)
        self.hBoxLayout.addWidget(self.iconLabel)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        # 右侧垂直布局
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)

        # 顶部布局：标题
        self.vBoxLayout.addLayout(self.topLayout)
        self.topLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.addWidget(self.nameLabel)
        self.topLayout.addStretch(1)  # 添加弹性空间

        # 描述文本
        self.vBoxLayout.addSpacing(8)
        self.vBoxLayout.addWidget(self.descriptionLabel)

        # 标签按钮布局
        self.vBoxLayout.addSpacing(16)
        self.vBoxLayout.addLayout(self.tagsLayout)
        self.tagsLayout.setContentsMargins(0, 0, 0, 0)
        self.tagsLayout.setSpacing(8)
        
        # 添加所有标签按钮
        self.tagsLayout.addWidget(self.tagWhisperButton)
        self.tagsLayout.addWidget(self.tagWhisperfasterButton)
        self.tagsLayout.addStretch(1)  # 添加弹性空间使标签左对齐

class TranscribeInterface(ScrollArea):
    """听写界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = QWidget(self)
        self.loadProgressInfoBar = None
        self.installProgressInfoBar = None
        
        # 当前选择的文件路径
        self.selectedFilePath = None
        
        # 转录工作线程
        self.worker = None

        # 初始化卡片组件
        self.transcribeModeInfoCard = TranscribeModeInfoCard(self.view)
        self.transcribeConfigCard = TranscribeConfigCard(self.view)
        
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()

    def __initWidget(self):
        self.setWidget(self.view)
        self.setAcceptDrops(True)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.vBoxLayout.setSpacing(10)
        self.vBoxLayout.setContentsMargins(0, 0, 10, 10)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(
            self.transcribeModeInfoCard, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(
            self.transcribeConfigCard, 0, Qt.AlignmentFlag.AlignTop)
        
        self.resize(780, 800)
        self.setObjectName("transcribeInterface")
        self.enableTransparentBackground()

        self._connectSignalToSlot()

    def _onSelectFileButtonClicked(self):
        """选择文件按钮点击事件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select File"),
            cfg.get(cfg.saveFolder),
            self.tr("Video/Audio Files (*.mp4 *.mkv *.avi *.mp3 *.wav *.flac);;All Files (*.*)")
        )
        
        if file_path:
            self.selectedFilePath = file_path
            # 更新按钮文本显示文件名
            from pathlib import Path
            file_name = Path(file_path).name
            # 截断过长的文件名
            if len(file_name) > 15:
                display_name = file_name[:12] + "..."
            else:
                display_name = file_name
            
            self.transcribeConfigCard.targetFileButton.setText(display_name)
            
            # 更新配置卡中显示的文件名
            self.transcribeConfigCard.targetFileGroup.contentLabel.setText(file_name)
            
            InfoBar.success(
                self.tr("File Selected"),
                file_name,
                duration=2000,
                position=InfoBarPosition.TOP,
                parent=self
            )

    def _onSaveFolderButtonClicked(self):
        """保存目录按钮点击事件"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Save Folder"),
            cfg.get(cfg.saveFolder)
        )
        
        if folder_path:
            cfg.set(cfg.saveFolder, folder_path)
            # 更新配置卡中显示的路径
            self.transcribeConfigCard.saveFolderGroup.contentLabel.setText(folder_path)
            
            InfoBar.success(
                self.tr("Save Folder Updated"),
                folder_path,
                duration=2000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def _onTranscribeButtonClicked(self):
        """听写按钮点击事件"""
        # 1. 检查服务是否可用
        if not transcriptionService.isAvailable():
            InfoBar.error(
                self.tr("Service Unavailable"),
                self.tr("Transcribe service is currently unavailable, please ensure ffmpeg is installed"),
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        # 2. 检查是否选择了文件
        if not self.selectedFilePath:
            InfoBar.warning(
                self.tr("No File Selected"),
                self.tr("Please select the file to transcribe"),
                duration=2000,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        # 3. 检查是否已有任务在运行
        if self.worker and self.worker.isRunning():
            InfoBar.warning(
                self.tr("Task Running"),
                self.tr("There is a task running, please wait for it to complete"),
                duration=2000,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        # 4. 获取配置参数
        # 语言映射
        language_map = {
            self.tr("Chinese"): "zh",
            self.tr("Japanese"): "ja",
            self.tr("English"): "en",
            self.tr("Korean"): "ko",
            self.tr("Russian"): "ru",
            self.tr("French"): "fr"
        }
        
        # 获取选择的值
        whisper_model = self.transcribeConfigCard.getSelectedModel()
        language_text = self.transcribeConfigCard.inputLanguageComboBox.currentText()
        output_format = self.transcribeConfigCard.outputFileTypeComBox.currentText()
        
        language = language_map.get(language_text, "ja")
        
        print(f"[听写任务] 选择的模型: {whisper_model}")
        print(f"[听写任务] 输入语言: {language}")
        print(f"[听写任务] 输出格式: {output_format}")
        
        # 5. 获取时间戳设置
        include_timestamp = self.transcribeConfigCard.timeStampButton.isChecked()
        
        status = self.tr('Yes') if include_timestamp else self.tr('No')
        print(f"[听写任务] 包含时间戳: {status}")
        
        # 6. 获取均分人数设置
        split_parts = self.transcribeConfigCard.averageCompactSpinBox.value()
        
        split_info = str(split_parts) if split_parts > 0 else self.tr('No splitting')
        print(f"[听写任务] 均分人数: {split_info}")
        
        # 7. 获取保存目录
        save_folder = cfg.get(cfg.saveFolder)
        print(f"[听写任务] 保存目录: {save_folder}")
        
        # 8. 创建并启动工作线程
        self.worker = TranscriptionWorker(
            input_path=self.selectedFilePath,
            whisper_model=whisper_model,
            language=language,
            output_format=output_format,
            include_timestamp=include_timestamp,
            split_parts=split_parts,
            save_folder=save_folder
        )
        
        # 连接信号
        self.worker.finished.connect(self._onTranscriptionFinished)
        self.worker.error.connect(self._onTranscriptionError)
        
        # 禁用听写按钮，防止重复点击
        self.transcribeConfigCard.transcribeButton.setEnabled(False)
        self.transcribeConfigCard.transcribeButton.setText(self.tr("Transcribing..."))
        
        # 启动线程
        self.worker.start()
        
        InfoBar.info(
            self.tr("Task Started"),
            self.tr("Transcribe task has started, please check the log for progress"),
            duration=3000,
            position=InfoBarPosition.TOP,
            parent=self
        )

    def _onTranscriptionFinished(self, result: dict):
        """转录完成回调"""
        # 恢复听写按钮
        self.transcribeConfigCard.transcribeButton.setEnabled(True)
        self.transcribeConfigCard.transcribeButton.setText(self.tr("Transcribe"))
        
        # 显示成功提示
        from pathlib import Path
        output_path = result.get('output_path', '')
        file_name = Path(output_path).name if output_path else self.tr("Unknown file")
        
        InfoBar.success(
            self.tr("听写完成"),
            self.tr("文件已成功转录: {file_name}").format(file_name=file_name),
            duration=5000,
            position=InfoBarPosition.TOP,
            parent=self
        )
        
        # 重置文件选择
        self.selectedFilePath = None
        self.transcribeConfigCard.targetFileButton.setText(self.tr("Select"))
        
        # 重置配置卡中显示的路径
        self.transcribeConfigCard.targetFileGroup.contentLabel.setText(self.tr("Select the file to transcribe"))
        
        print(f"[转录完成] 输出文件: {output_path}")
        print(f"[转录完成] SRT文件: {result.get('srt_path', 'N/A')}")

    def _onTranscriptionError(self, error_msg: str):
        """转录错误回调"""
        # 恢复听写按钮
        self.transcribeConfigCard.transcribeButton.setEnabled(True)
        self.transcribeConfigCard.transcribeButton.setText(self.tr("Transcribe"))
        
        # 显示错误提示
        InfoBar.error(
            self.tr("Transcribe Failed"),
            self.tr("Transcribe process error: {error_msg}").format(error_msg=error_msg),
            duration=8000,
            position=InfoBarPosition.TOP,
            parent=self
        )
        
        print(f"[转录错误] {error_msg}")

    def _onTimeStampSwitchChanged(self, checked: bool):
        """时间戳开关状态改变事件"""
        status_text = self.tr("Enabled") if checked else self.tr("Disabled")
        print(f"[配置] 时间戳设置: {status_text}")
    
    def _onAverageSpinBoxChanged(self, value: int):
        """均分人数变化事件"""
        if value > 0:
            print(self.tr("[Config] Split parts set to: {value} people").format(value=value))
        else:
            print(self.tr("[Config] Split function disabled"))
    
    def _onOpenModelsButtonClicked(self):
        """打开模型目录按钮点击事件"""
        import os
        import sys
        from pathlib import Path
        
        # 获取模型目录路径（使用与 model_scanner 相同的逻辑）
        if getattr(sys, 'frozen', False):
            # 打包后的程序
            app_dir = Path(sys.executable).parent
            models_dir = app_dir / 'app' / 'common' / 'models' / 'whisper-faster'
        else:
            # 开发环境
            app_dir = Path(__file__).parent.parent
            models_dir = app_dir / 'common' / 'models' / 'whisper-faster'
        
        # 确保目录存在
        if not models_dir.exists():
            models_dir.mkdir(parents=True, exist_ok=True)
            print(f"[模型管理] 创建模型目录: {models_dir}")
        
        # 打开目录
        try:
            if sys.platform == 'win32':
                os.startfile(str(models_dir))
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{models_dir}"')
            else:  # Linux
                os.system(f'xdg-open "{models_dir}"')
            
            print(f"[模型管理] 打开目录: {models_dir}")
            
            InfoBar.success(
                self.tr("已打开模型目录"),
                str(models_dir),
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
        except Exception as e:
            print(f"[模型管理] 打开目录失败: {e}")
            InfoBar.error(
                self.tr("打开失败"),
                self.tr("无法打开目录: {error}").format(error=str(e)),
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def _connectSignalToSlot(self):
        """连接信号与槽"""
        # 连接配置卡片的按钮信号
        self.transcribeConfigCard.targetFileButton.clicked.connect(
            self._onSelectFileButtonClicked
        )
        self.transcribeConfigCard.saveFolderButton.clicked.connect(
            self._onSaveFolderButtonClicked
        )
        self.transcribeConfigCard.transcribeButton.clicked.connect(
            self._onTranscribeButtonClicked
        )
        
        # 连接时间戳开关信号
        self.transcribeConfigCard.timeStampButton.checkedChanged.connect(
            self._onTimeStampSwitchChanged
        )
        
        # 连接均分人数调节器信号
        self.transcribeConfigCard.averageCompactSpinBox.valueChanged.connect(
            self._onAverageSpinBoxChanged
        )
        
        # 连接打开模型目录按钮信号
        self.transcribeConfigCard.openModelsButton.clicked.connect(
            self._onOpenModelsButtonClicked
        )
        
        # 注意：使用 QThread 异步执行，信号在创建 worker 时动态连接

    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        """拖拽释放事件"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            # 检查文件扩展名
            from pathlib import Path
            valid_extensions = ['.mp4', '.mkv', '.avi', '.mp3', '.wav', '.flac', '.srt']
            if Path(file_path).suffix.lower() in valid_extensions:
                self.selectedFilePath = file_path
                file_name = Path(file_path).name
                
                # 更新按钮显示
                if len(file_name) > 15:
                    display_name = file_name[:12] + "..."
                else:
                    display_name = file_name
                
                self.transcribeConfigCard.targetFileButton.setText(display_name)
                
                # 更新配置卡中显示的文件名
                self.transcribeConfigCard.targetFileGroup.contentLabel.setText(file_name)
                
                InfoBar.success(
                    self.tr("File Added"),
                    file_name,
                    duration=2000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
            else:
                InfoBar.warning(
                    self.tr("Unsupported File Format"),
                    self.tr("Please drag in video or audio files"),
                    duration=2000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
        
        event.acceptProposedAction()