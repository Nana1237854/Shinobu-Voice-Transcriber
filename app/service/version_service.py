# coding:utf-8
import re
import requests

from PySide6.QtCore import QVersionNumber

from ..common.setting import VERSION


class VersionService:
    """版本更新服务"""

    def __init__(self):
        self.currentVersion = VERSION.lstrip('v')  # 移除 'v' 前缀
        self.lastestVersion = self.currentVersion
        self.versionPattern = re.compile(r'v?(\d+)\.(\d+)\.(\d+)')

    def getLatestVersion(self) -> str:
        """
        获取最新版本号
        
        Returns:
            最新版本号（如 "1.1.0"），失败时返回当前版本
        """
        try:
            # 使用 GitHub API 获取最新 release
            url = "https://api.github.com/repos/Nana1237854/Shinobu-Voice-Transcriber/releases/latest"
            
            headers = {
                "Accept": "application/vnd.github+json",
                "User-Agent": "Shinobu-Voice-Transcriber"
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # 解析 JSON 响应
            data = response.json()
            tag_name = data.get('tag_name', '')  # 如 "v1.1.0"
            
            # 提取版本号
            match = self.versionPattern.search(tag_name)
            if match:
                # 返回不带 'v' 的版本号
                version = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
                self.lastestVersion = version
                return version
            
            return self.currentVersion
            
        except requests.RequestException as e:
            print(f"[版本检查] 网络错误: {e}")
            return self.currentVersion
        except Exception as e:
            print(f"[版本检查] 错误: {e}")
            return self.currentVersion

    def hasNewVersion(self) -> bool:
        """
        检查是否有新版本
        
        Returns:
            如果有新版本返回 True，否则返回 False
        """
        try:
            latest = self.getLatestVersion()
            
            # 使用 QVersionNumber 比较版本
            latestVersion = QVersionNumber.fromString(latest)
            currentVersion = QVersionNumber.fromString(self.currentVersion)
            
            has_new = latestVersion > currentVersion
            
            if has_new:
                print(f"[版本检查] 发现新版本: {latest} (当前: {self.currentVersion})")
            else:
                print(f"[版本检查] 已是最新版本: {self.currentVersion}")
            
            return has_new
            
        except Exception as e:
            print(f"[版本检查] 比较版本时出错: {e}")
            return False

    def getUpdateInfo(self) -> dict:
        """
        获取更新信息
        
        Returns:
            包含版本信息、更新说明和下载链接的字典
        """
        try:
            url = "https://api.github.com/repos/Nana1237854/Shinobu-Voice-Transcriber/releases/latest"
            
            headers = {
                "Accept": "application/vnd.github+json",
                "User-Agent": "Shinobu-Voice-Transcriber"
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            
            return {
                'version': data.get('tag_name', 'Unknown').lstrip('v'),
                'name': data.get('name', ''),
                'body': data.get('body', ''),  # 更新说明
                'html_url': data.get('html_url', ''),  # Release 页面
                'published_at': data.get('published_at', ''),
                'assets': [
                    {
                        'name': asset.get('name', ''),
                        'size': asset.get('size', 0),
                        'download_url': asset.get('browser_download_url', '')
                    }
                    for asset in data.get('assets', [])
                ]
            }
            
        except Exception as e:
            print(f"[版本检查] 获取更新信息失败: {e}")
            return {
                'version': self.currentVersion,
                'name': VERSION,
                'body': '',
                'html_url': 'https://github.com/Nana1237854/Shinobu-Voice-Transcriber/releases',
                'published_at': '',
                'assets': []
            }


# 全局版本服务实例
versionService = VersionService()

