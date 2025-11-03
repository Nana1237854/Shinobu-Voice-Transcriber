# coding:utf-8
import os
import shutil
import zipfile
from pathlib import Path
from PySide6.QtCore import QThread, Signal
import urllib.request
import urllib.error

try:
    import py7zr
    HAS_7Z_SUPPORT = True
except ImportError:
    HAS_7Z_SUPPORT = False


class DownloadThread(QThread):
    """Download thread for downloading files"""
    
    progressChanged = Signal(int)
    finished = Signal(bool, str)
    
    def __init__(self, url, save_path, extract_to=None, post_process=None, parent=None):
        super().__init__(parent)
        self.url = url
        self.save_path = save_path
        self.extract_to = extract_to
        self.post_process = post_process
        self._is_cancelled = False
        
    def run(self):
        try:
            # Download file
            def reporthook(block_num, block_size, total_size):
                if self._is_cancelled:
                    raise Exception("下载已取消")
                if total_size > 0:
                    progress = min(int(block_num * block_size * 100 / total_size), 100)
                    self.progressChanged.emit(progress)
            
            urllib.request.urlretrieve(self.url, self.save_path, reporthook)
            
            # Extract if needed
            if self.extract_to:
                self.progressChanged.emit(0)
                if self.save_path.endswith('.zip'):
                    with zipfile.ZipFile(self.save_path, 'r') as zip_ref:
                        zip_ref.extractall(self.extract_to)
                elif self.save_path.endswith('.7z'):
                    if HAS_7Z_SUPPORT:
                        with py7zr.SevenZipFile(self.save_path, mode='r') as z:
                            z.extractall(path=self.extract_to)
                    else:
                        raise Exception("7z 支持不可用。请安装 py7zr 包。")
                
                # Post-process if needed
                if self.post_process:
                    self.post_process(self.extract_to)
                
                # Remove archive file after extraction
                os.remove(self.save_path)
                
            self.finished.emit(True, "下载成功")
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def cancel(self):
        self._is_cancelled = True


class DownloadService:
    """Service for managing downloads"""
    
    # FFmpeg download URL (Windows 64-bit)
    FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    # Whisper-Faster-XXL download URL
    # Note: This may need to be updated based on the actual release assets
    # Users should check https://github.com/Purfview/whisper-standalone-win/releases/tag/Faster-Whisper-XXL
    # for the latest version and correct download link
    WHISPER_XXL_URL = "https://github.com/Purfview/whisper-standalone-win/releases/download/Faster-Whisper-XXL/Faster-Whisper-XXL_r245.1_windows.7z"
    
    def __init__(self):
        self.tools_dir = Path(__file__).parent.parent / "tools"
        self.tools_dir.mkdir(exist_ok=True)
        
    def check_ffmpeg_exists(self):
        """Check if ffmpeg.exe exists"""
        ffmpeg_path = self.tools_dir / "ffmpeg.exe"
        return ffmpeg_path.exists()
    
    def check_whisper_faster_exists(self):
        """Check if whisper-faster.exe and _xxl_data exist"""
        whisper_path = self.tools_dir / "whisper-faster.exe"
        xxl_data_path = self.tools_dir / "_xxl_data"
        return whisper_path.exists() and xxl_data_path.exists()
    
    def get_ffmpeg_path(self):
        """Get ffmpeg.exe path"""
        return self.tools_dir / "ffmpeg.exe"
    
    def get_whisper_faster_path(self):
        """Get whisper-faster.exe path"""
        return self.tools_dir / "whisper-faster.exe"
    
    def _process_ffmpeg_extraction(self, extract_dir):
        """Post-process FFmpeg extraction to move ffmpeg.exe to tools directory"""
        extract_path = Path(extract_dir)
        
        # Find ffmpeg.exe in extracted files
        ffmpeg_exe = None
        for root, dirs, files in os.walk(extract_path):
            if 'ffmpeg.exe' in files:
                ffmpeg_exe = Path(root) / 'ffmpeg.exe'
                break
        
        if ffmpeg_exe:
            target_path = self.tools_dir / "ffmpeg.exe"
            # Move ffmpeg.exe to tools directory
            shutil.copy2(ffmpeg_exe, target_path)
            
            # Clean up extracted folder
            for item in extract_path.iterdir():
                if item.is_dir() and item.name.startswith('ffmpeg-'):
                    shutil.rmtree(item)
    
    def _process_whisper_extraction(self, extract_dir):
        """Post-process Whisper-Faster-XXL extraction"""
        extract_path = Path(extract_dir)
        
        # Find the extracted folder (usually named something like 'Faster-Whisper-XXL')
        for item in extract_path.iterdir():
            if item.is_dir() and 'whisper' in item.name.lower():
                # Look for faster-whisper-xxl.exe or similar
                for file in item.iterdir():
                    if file.name.endswith('.exe') and 'whisper' in file.name.lower():
                        # Rename to whisper-faster.exe
                        target_exe = self.tools_dir / "whisper-faster.exe"
                        shutil.copy2(file, target_exe)
                    elif file.is_dir() and file.name == '_xxl_data':
                        # Replace _xxl_data folder
                        target_data = self.tools_dir / "_xxl_data"
                        if target_data.exists():
                            shutil.rmtree(target_data)
                        shutil.copytree(file, target_data)
                
                # Clean up extracted folder
                shutil.rmtree(item)
                break
    
    def create_ffmpeg_download_thread(self):
        """Create download thread for ffmpeg"""
        temp_zip = self.tools_dir / "ffmpeg_temp.zip"
        return DownloadThread(
            self.FFMPEG_URL,
            str(temp_zip),
            str(self.tools_dir),
            self._process_ffmpeg_extraction
        )
    
    def create_whisper_download_thread(self):
        """Create download thread for whisper-faster-xxl"""
        temp_file = self.tools_dir / "whisper_temp.7z"
        return DownloadThread(
            self.WHISPER_XXL_URL,
            str(temp_file),
            str(self.tools_dir),
            self._process_whisper_extraction
        )


# Global download service instance
downloadService = DownloadService()

