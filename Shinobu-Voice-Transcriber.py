# coding:utf-8
import os
import sys
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, QTranslator
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator

from app.common.config import cfg
from app.common.setting import CONFIG_FOLDER, LOG_PATH
from app.view.main_window import MainWindow


def init_app_data():
    """初始化应用数据目录和文件"""
    # 创建 AppData 目录
    CONFIG_FOLDER.mkdir(parents=True, exist_ok=True)
    print(f"[初始化] AppData 目录: {CONFIG_FOLDER}")
    
    # 创建日志文件（如果不存在）
    if not LOG_PATH.exists():
        with open(LOG_PATH, 'w', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] 应用启动 - 日志文件已创建\n")
        print(f"[初始化] 日志文件: {LOG_PATH}")
    
    # 重定向标准输出到日志文件
    log_file = open(LOG_PATH, 'a', encoding='utf-8', buffering=1)
    sys.stdout = log_file
    sys.stderr = log_file
    
    # 写入启动日志
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n{'='*80}")
    print(f"[{timestamp}] 应用启动")
    print(f"{'='*80}\n")
    sys.stdout.flush()


# 初始化应用数据（创建目录和日志文件）
init_app_data()

# enable dpi scale
if cfg.get(cfg.dpiScale) != "Auto":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

# create application
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

# internationalization
from app.common.config import Language

locale = cfg.get(cfg.language).value
fluentTranslator = FluentTranslator(locale)
appTranslator = QTranslator()

# 根据语言加载对应的翻译文件
language_setting = cfg.get(cfg.language)
if language_setting == Language.CHINESE_SIMPLIFIED:
    appTranslator.load("app/resource/i18n/app.zh_CN.qm")
    print("[国际化] 加载简体中文翻译")
elif language_setting == Language.CHINESE_TRADITIONAL:
    appTranslator.load("app/resource/i18n/app.zh_HK.qm")
    print("[国际化] 加载繁体中文翻译")
else:
    # AUTO 或 ENGLISH 默认使用英文（源语言）
    print("[国际化] 使用默认语言（English）")

app.installTranslator(fluentTranslator)
app.installTranslator(appTranslator)

# create main window
w = MainWindow()
w.show()

app.exec()
