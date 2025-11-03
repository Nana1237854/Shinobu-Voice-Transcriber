from PySide6.QtCore import Qt, QThread, Signal
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
                self.error.emit("转录失败，未返回结果")
        except Exception as e:
            self.error.emit(str(e))


class TranscribeConfigCard(GroupHeaderCardWidget):
    """听写配置卡片"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("听写设置"))
        self.mediaParser = None

        self.targetFileButton = PushButton(self.tr("选择"))
        self.transcribeModelComboBox = ComboBox()
        self.inputLanguageComboBox = ComboBox()
        self.timeStampButton = SwitchButton(self.tr("关闭"), self)
        self.outputFileTypeComBox = ComboBox()
        self.averageCompactSpinBox = CompactSpinBox()
        self.saveFolderButton = PushButton(self.tr("选择"), self, FluentIcon.FOLDER)
        self.openModelsButton = PushButton(self.tr("打开模型目录"), self, FluentIcon.FOLDER)
        
        self.hintIcon = IconWidget(InfoBarIcon.INFORMATION, self)
        self.hintLabel = BodyLabel(
            self.tr("点击听写按钮开始听写") + ' 👉')
        self.transcribeButton = PrimaryPushButton(
            self.tr("听写"), self, FluentIcon.PLAY_SOLID)
        
        self.toolBarLayout = QHBoxLayout()

        self._initWidgets()

    def _initWidgets(self):
        self.setBorderRadius(8)

        self.targetFileButton.setFixedWidth(120)
        self.transcribeModelComboBox.setFixedWidth(320)
        self.inputLanguageComboBox.setFixedWidth(320)
        
        # 动态加载 Whisper 模型列表
        self._loadWhisperModels()
        
        self.inputLanguageComboBox.addItems(["中文", "日语", "英语", "韩语", "俄语", "法语"])
        self.outputFileTypeComBox.addItems(
            ["原文SRT", "双语SRT", "原文LRC", "原文TXT", 
             "双语TXT", "原文XLSX", "双语XLSX"]
            )
        
        # 更改按钮状态 - 默认关闭
        self.timeStampButton.setChecked(False)
        self.timeStampButton.setOffText(self.tr("关闭"))
        self.timeStampButton.setOnText(self.tr("开启"))

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
            title=self.tr("目标文件"),
            content=self.tr("选择待听写的文件"),
            widget=self.targetFileButton
        )
        self.addGroup(
            icon=FluentIcon.IOT,
            title=self.tr("听写模型"),
            content=self.tr("选择用于听写的模型类别"),
            widget=self.transcribeModelComboBox
        )
        self.addGroup(
            icon=FluentIcon.LANGUAGE,
            title=self.tr("输入语言"),
            content=self.tr("选择输入的语言"),
            widget=self.inputLanguageComboBox
        )
        self.addGroup(
            icon=FluentIcon.UNIT.icon(),
            title=self.tr("时间戳"),
            content=self.tr("是否生成时间戳（仅用于快速定位原句，不保证精确）"),
            widget=self.timeStampButton
        )
        self.addGroup(
            icon=FluentIcon.SAVE,
            title=self.tr("输出文件"),
            content=self.tr("选择输出的文件"),
            widget=self.outputFileTypeComBox
        )
        self.addGroup(
            icon=FluentIcon.CLIPPING_TOOL.icon(),
            title=self.tr("均分音频"),
            content=self.tr("按人数均分音频生成文件（用于字幕组快速分工）\n注：时长向上取整；能整除则均分，否则余数给最后一人"),
            widget=self.averageCompactSpinBox
        )
        self.saveFolderGroup = self.addGroup(
            icon=FluentIcon.FOLDER,
            title=self.tr("保存目录"),
            content=cfg.get(cfg.saveFolder),
            widget=self.saveFolderButton
        )
        self.addGroup(
            icon=FluentIcon.FOLDER_ADD,
            title=self.tr("模型管理"),
            content=self.tr("打开模型文件夹，添加或管理 Whisper 模型"),
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

        self.nameLabel = TitleLabel(self.tr("听写模式"), self)

        self.descriptionLabel = BodyLabel(
            self.tr("下载模式工作流：\n选择听写文件 -> 选择听写模型 -> 选择输入语言 -> 选择输出文件 -> 选择保存目录 -> 点击听写按钮进行听写")
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
            self.tr("选择文件"),
            cfg.get(cfg.saveFolder),
            self.tr("视频/音频文件 (*.mp4 *.mkv *.avi *.mp3 *.wav *.flac);;所有文件 (*.*)")
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
                self.tr("文件已选择"),
                file_name,
                duration=2000,
                position=InfoBarPosition.TOP,
                parent=self
            )

    def _onSaveFolderButtonClicked(self):
        """保存目录按钮点击事件"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            self.tr("选择保存目录"),
            cfg.get(cfg.saveFolder)
        )
        
        if folder_path:
            cfg.set(cfg.saveFolder, folder_path)
            # 更新配置卡中显示的路径
            self.transcribeConfigCard.saveFolderGroup.contentLabel.setText(folder_path)
            
            InfoBar.success(
                self.tr("保存目录已更新"),
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
                self.tr("服务不可用"),
                self.tr("听写服务当前不可用，请确保 ffmpeg 已安装"),
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        # 2. 检查是否选择了文件
        if not self.selectedFilePath:
            InfoBar.warning(
                self.tr("未选择文件"),
                self.tr("请先选择要听写的文件"),
                duration=2000,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        # 3. 检查是否已有任务在运行
        if self.worker and self.worker.isRunning():
            InfoBar.warning(
                self.tr("任务进行中"),
                self.tr("当前有任务正在执行，请等待完成"),
                duration=2000,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        # 4. 获取配置参数
        # 语言映射
        language_map = {
            "中文": "zh",
            "日语": "ja",
            "英语": "en",
            "韩语": "ko",
            "俄语": "ru",
            "法语": "fr"
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
        
        print(f"[听写任务] 包含时间戳: {'是' if include_timestamp else '否'}")
        
        # 6. 获取均分人数设置
        split_parts = self.transcribeConfigCard.averageCompactSpinBox.value()
        
        print(f"[听写任务] 均分人数: {split_parts if split_parts > 0 else '不均分'}")
        
        # 7. 创建并启动工作线程
        self.worker = TranscriptionWorker(
            input_path=self.selectedFilePath,
            whisper_model=whisper_model,
            language=language,
            output_format=output_format,
            include_timestamp=include_timestamp,
            split_parts=split_parts
        )
        
        # 连接信号
        self.worker.finished.connect(self._onTranscriptionFinished)
        self.worker.error.connect(self._onTranscriptionError)
        
        # 禁用听写按钮，防止重复点击
        self.transcribeConfigCard.transcribeButton.setEnabled(False)
        self.transcribeConfigCard.transcribeButton.setText(self.tr("听写中..."))
        
        # 启动线程
        self.worker.start()
        
        InfoBar.info(
            self.tr("任务已开始"),
            self.tr("听写任务已开始执行，请查看运行日志了解进度"),
            duration=3000,
            position=InfoBarPosition.TOP,
            parent=self
        )

    def _onTranscriptionFinished(self, result: dict):
        """转录完成回调"""
        # 恢复听写按钮
        self.transcribeConfigCard.transcribeButton.setEnabled(True)
        self.transcribeConfigCard.transcribeButton.setText(self.tr("听写"))
        
        # 显示成功提示
        from pathlib import Path
        output_path = result.get('output_path', '')
        file_name = Path(output_path).name if output_path else "未知文件"
        
        InfoBar.success(
            self.tr("听写完成"),
            self.tr(f"文件已成功转录: {file_name}"),
            duration=5000,
            position=InfoBarPosition.TOP,
            parent=self
        )
        
        # 重置文件选择
        self.selectedFilePath = None
        self.transcribeConfigCard.targetFileButton.setText(self.tr("选择"))
        
        # 重置配置卡中显示的路径
        self.transcribeConfigCard.targetFileGroup.contentLabel.setText(self.tr("选择待听写的文件"))
        
        print(f"[转录完成] 输出文件: {output_path}")
        print(f"[转录完成] SRT文件: {result.get('srt_path', 'N/A')}")

    def _onTranscriptionError(self, error_msg: str):
        """转录错误回调"""
        # 恢复听写按钮
        self.transcribeConfigCard.transcribeButton.setEnabled(True)
        self.transcribeConfigCard.transcribeButton.setText(self.tr("听写"))
        
        # 显示错误提示
        InfoBar.error(
            self.tr("听写失败"),
            self.tr(f"转录过程出错: {error_msg}"),
            duration=8000,
            position=InfoBarPosition.TOP,
            parent=self
        )
        
        print(f"[转录错误] {error_msg}")

    def _onTimeStampSwitchChanged(self, checked: bool):
        """时间戳开关状态改变事件"""
        status_text = "已开启" if checked else "已关闭"
        print(f"[配置] 时间戳设置: {status_text}")
    
    def _onAverageSpinBoxChanged(self, value: int):
        """均分人数变化事件"""
        if value > 0:
            print(f"[配置] 均分人数设置为: {value} 人")
        else:
            print(f"[配置] 均分功能已关闭")
    
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
                self.tr(f"无法打开目录: {str(e)}"),
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
                    self.tr("文件已添加"),
                    file_name,
                    duration=2000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
            else:
                InfoBar.warning(
                    self.tr("不支持的文件格式"),
                    self.tr("请拖入视频或音频文件"),
                    duration=2000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
        
        event.acceptProposedAction()