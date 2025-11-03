# coding: utf-8
from enum import Enum

from qfluentwidgets import FluentIconBase, getIconColor, Theme, FluentIcon


class Icon(FluentIconBase, Enum):

    # TODO: Add your icons here

    HEADPHONE = "Headphone"
    TASK = "Task"
    SETTINGS = "Settings"
    SETTINGS_FILLED = "SettingsFilled"

    def path(self, theme=Theme.AUTO):
        # 自定义SVG图标
        if self.value in ["Settings", "SettingsFilled"]:
            return f":/app/images/icons/{self.value}_{getIconColor(theme)}.svg"
        
        # 映射到FluentIcon
        icon_map = {
            "Task": FluentIcon.CHECKBOX,
            "CloudDownload": FluentIcon.CLOUD_DOWNLOAD,
            "Select": FluentIcon.ACCEPT,
            "Headphone": FluentIcon.HEADPHONE,
            "Language": FluentIcon.LANGUAGE,
            "Tools": FluentIcon.ADD_TO,
        }
        
        if self.value in icon_map:
            return icon_map[self.value].path(theme)
        
        return ""