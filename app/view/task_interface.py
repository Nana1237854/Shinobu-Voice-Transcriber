# coding:utf-8
import os
from PySide6.QtCore import QDateTime, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from qfluentwidgets import BodyLabel, PlainTextEdit, PushButton, setFont

from ..common.interface import Interface
from ..common.setting import LOG_PATH




class TaskInterface(Interface):
    """日志查看界面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("运行日志"))

        self.logTaskView = LogTaskView(self)  # 日志视图
        
        self.__initWidgets()
        
    def __initWidgets(self):
        self.setViewportMargins(0, 80, 0, 10)
        self._initLayout()

    def _initLayout(self):
        self.viewLayout.addWidget(self.logTaskView)

class LogTaskView(QWidget):
    """日志视图"""
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("log")

        self.titleLabel = BodyLabel(self.tr("Task Log"), self)
        self.logContent = PlainTextEdit(self)
        self.clearButton = PushButton(self.tr("Clear Log"), self)

        # 日志文件读取相关
        self.timer = None
        self.last_read_position = 0
        self.file_not_found_message_shown = False
        self.LOG_PATH = LOG_PATH  # 从 setting.py 导入的路径

        self.__initWidgets()
        self.__initLayout()
        self._connectSignalToSlot()
        self._setup_timer()  # 初始化定时器

    def __initWidgets(self):
        self.logContent.setReadOnly(True)
        setFont(self.logContent, 15)
        self.titleLabel.setObjectName("logTitleLabel")

    def __initLayout(self):
        layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()

        button_layout.addWidget(self.titleLabel)
        button_layout.addStretch(1)
        button_layout.addWidget(self.clearButton)

        layout.addLayout(button_layout)
        layout.addWidget(self.logContent)
        self.setLayout(layout)

    def _connectSignalToSlot(self):
        self.clearButton.clicked.connect(self._clear_log_file)

    def _setup_timer(self):
        """设置定时器，每秒读取一次日志文件"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._read_log_file)
        self.timer.start(1000)  # 每秒读取一次
        
        # 初始读取位置
        self.last_read_position = 0
        self.file_not_found_message_shown = False
        
        # 立即读取一次日志
        self._read_log_file()

    def _read_log_file(self):
        """读取日志文件并更新显示（增量读取）"""
        try:
            # 检查文件是否存在
            if not os.path.exists(self.LOG_PATH):
                if not self.file_not_found_message_shown:
                    timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
                    self.logContent.setPlainText(
                        f"[{timestamp}] {self.tr('Error: Log file not found')}: '{self.LOG_PATH}'.\n"
                        f"{self.tr('Waiting for file to be created')}...\n"
                    )
                    self.file_not_found_message_shown = True
                self.last_read_position = 0  # 如果文件消失了，重置读取位置
                return

            # 如果文件之前未找到但现在找到了
            if self.file_not_found_message_shown:
                self.logContent.clear()  # 清除之前的错误信息
                self.file_not_found_message_shown = False
                self.last_read_position = 0  # 从头开始读

            with open(self.LOG_PATH, 'r', encoding='utf-8', errors='replace') as f:
                # 检查文件是否被截断或替换 (例如日志轮转)
                current_file_size = f.seek(0, os.SEEK_END)
                
                if current_file_size < self.last_read_position:
                    # 文件变小了，意味着文件被截断或替换了
                    timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
                    self.logContent.appendPlainText(
                        f"\n[{timestamp}] {self.tr('Log file truncation detected. Reading from beginning')}...\n"
                    )
                    self.last_read_position = 0

                # 从上次读取位置开始读取
                f.seek(self.last_read_position)
                new_content = f.read()
                
                if new_content:
                    # 移除末尾的换行符，appendPlainText 会自动添加
                    self.logContent.appendPlainText(new_content.rstrip())
                    
                    # 自动滚动到底部
                    scrollbar = self.logContent.verticalScrollBar()
                    scrollbar.setValue(scrollbar.maximum())

                # 更新下次读取的起始位置
                self.last_read_position = f.tell()

        except FileNotFoundError:
            if not self.file_not_found_message_shown:
                timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
                self.logContent.setPlainText(
                    f"[{timestamp}] {self.tr('Error: Log file not found on recheck')}: '{self.LOG_PATH}'.\n"
                )
                self.file_not_found_message_shown = True
            self.last_read_position = 0
            
        except IOError as e:
            timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            self.logContent.appendPlainText(f"[{timestamp}] {self.tr('IO error reading log file')}: {e}\n")
            
        except Exception as e:
            timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            self.logContent.appendPlainText(f"[{timestamp}] {self.tr('Unknown error reading log file')}: {e}\n")

    def _clear_log_file(self):
        """清空日志文件和显示"""
        try:
            # 清空显示
            self.logContent.clear()
            
            # 清空日志文件
            if os.path.exists(self.LOG_PATH):
                with open(self.LOG_PATH, 'w', encoding='utf-8') as f:
                    timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
                    f.write(f"[{timestamp}] {self.tr('Log cleared')}\n")
                
                # 重置读取位置
                self.last_read_position = 0
                
                # 立即读取新内容
                self._read_log_file()
        except Exception as e:
            print(f"{self.tr('Error clearing log file')}: {e}")

    def showEvent(self, event):
        """当视图显示时，确保定时器运行并立即读取最新日志"""
        super().showEvent(event)
        if self.timer and not self.timer.isActive():
            self.timer.start(1000)
        self._read_log_file()

    def hideEvent(self, event):
        """当视图隐藏时，可以选择停止定时器以节省资源"""
        super().hideEvent(event)
        # 可选：停止定时器以节省资源
        # if self.timer:
        #     self.timer.stop()

    def closeEvent(self, event):
        """确保在关闭窗口时停止定时器"""
        if self.timer:
            self.timer.stop()
        event.accept()

