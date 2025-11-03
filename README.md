# Shinobu-Voice-Transcriber

<div align="center">

![Logo](app/resource/images/logo.png)

一款基于 Faster-Whisper 的语音转录工具，提供现代化的图形界面和丰富的输出格式支持

[![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.0+-orange.svg)](https://pypi.org/project/PySide6/)

</div>

## ✨ 特性

- 🎯 **高精度识别**：基于 OpenAI Faster-Whisper 模型，支持多种模型大小（base/small/medium/large）
- 🎨 **现代化界面**：使用 QFluentWidgets 构建的 Fluent Design 风格界面，支持亮色/暗色主题
- 🌍 **多语言支持**：支持中文、日语、英语、韩语、俄语、法语等多种语言识别
- 📝 **丰富的输出格式**：
  - 字幕格式：SRT（单/双语）、LRC
  - 文本格式：TXT（单/双语）
  - 表格格式：XLSX（单/双语）
- ⚡ **智能均分**：支持将字幕按时间均分为多份，便于多人协作翻译
- 🎬 **格式兼容**：自动提取音视频文件的音轨，支持常见的音视频格式
- 📊 **任务管理**：内置任务日志查看器，实时查看转录进度和结果
- 🔧 **灵活配置**：可自定义时间戳显示、均分人数等参数

## 📋 系统要求

- **操作系统**：Windows 10/11（推荐）、Linux、macOS
- **Python 版本**：3.11 或更高
- **内存**：至少 4GB RAM（推荐 8GB 或以上，具体取决于所选模型）
- **硬盘空间**：至少 2GB 可用空间（用于模型文件）

## 🚀 快速开始

### 1. 安装依赖

首先克隆本仓库：

```bash
git clone https://github.com/yourusername/Shinobu-Voice-Transcriber.git
cd Shinobu-Voice-Transcriber
```

创建虚拟环境（推荐）：

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

安装 Python 依赖：

```bash
pip install -r requirements.txt
```

### 2. 安装 FFmpeg

本工具需要 FFmpeg 来提取音频。

**Windows 用户**：
- FFmpeg 可执行文件已包含在 `app/tools/` 目录中
- 或者从 [FFmpeg 官网](https://ffmpeg.org/download.html) 下载并添加到系统 PATH

**Linux 用户**：
```bash
sudo apt-get install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg      # CentOS/RHEL
```

**macOS 用户**：
```bash
brew install ffmpeg
```

### 3. 准备 Whisper 模型

首次运行时，程序会自动扫描模型目录。您可以：

**选项 A：自动下载（推荐）**
- 首次运行时，选择模型后程序会自动从 Hugging Face 下载

**选项 B：手动下载**
- 将模型文件放置在 `app/common/models/whisper-faster/` 目录下
- 模型目录结构：
  ```
  app/common/models/whisper-faster/
  └── faster-whisper-medium/
      ├── config.json
      ├── model.bin
      ├── tokenizer.json
      └── vocabulary.txt
  ```

### 4. 运行程序

```bash
python Shinobu-Voice-Transcriber.py
```

## 📖 使用指南

### 基本工作流程

1. **选择输入文件**：点击"选择"按钮，选择要转录的音频或视频文件
2. **配置参数**：
   - **Whisper 模型**：选择识别模型（推荐 medium 平衡精度和速度）
   - **输入语言**：选择源语言
   - **输出格式**：选择需要的输出格式
   - **时间戳**：是否在输出中包含时间戳（仅对 TXT 和 XLSX 格式有效）
   - **均分人数**：如需多人翻译，可设置将字幕按时间均分为几份（0 表示不均分）
3. **开始转录**：点击"听写"按钮开始处理
4. **查看结果**：转录完成后，输出文件将保存在与输入文件相同的目录

### 输出格式说明

| 格式 | 描述 | 用途 |
|------|------|------|
| **原文SRT** | 标准字幕文件，包含时间戳 | 视频字幕、播放器兼容 |
| **双语SRT** | 原文+译文的双语字幕 | 学习、双语视频制作 |
| **原文LRC** | 歌词文件格式 | 音乐播放器同步歌词 |
| **原文TXT** | 纯文本格式 | 文本编辑、阅读 |
| **双语TXT** | 原文+译文纯文本 | 对照阅读、校对 |
| **原文XLSX** | Excel 表格格式 | 翻译工作流、批量编辑 |
| **双语XLSX** | 原文+译文表格 | 翻译管理、团队协作 |

### 模型选择建议

| 模型 | 大小 | 内存需求 | 速度 | 精度 | 推荐场景 |
|------|------|----------|------|------|----------|
| **base** | ~140MB | 1-2GB | ⚡⚡⚡ | ⭐⭐ | 快速预览、资源受限环境 |
| **small** | ~460MB | 2-4GB | ⚡⚡ | ⭐⭐⭐ | 日常使用、平衡性能 |
| **medium** | ~1.5GB | 4-6GB | ⚡ | ⭐⭐⭐⭐ | **推荐**，高精度需求 |
| **large** | ~3GB | 8GB+ | 慢 | ⭐⭐⭐⭐⭐ | 专业级精度要求 |

### 均分功能说明

均分功能可将字幕按时间段平均分配，适合多人协作翻译：

- **设置均分人数**：例如设置为 3，会生成 3 个文件（`_part_1`、`_part_2`、`_part_3`）
- **智能时间划分**：
  - 总时长向上取整为分钟数
  - 如果能被人数整除，则均分
  - 如果不能整除，余数分配给最后一人
- **支持格式**：TXT 和 XLSX 格式

**示例**：
- 视频总长 25 分钟，设置 3 人均分
- 向上取整为 25 分钟，不能被 3 整除
- 分配结果：前 2 人各 8 分钟，最后 1 人 9 分钟

## 🔧 高级配置

### 配置文件

配置文件位于 `AppData/config.json`，包含以下设置：

- **主题设置**：亮色/暗色/自动
- **语言设置**：界面语言（简体中文/繁体中文/英文）
- **DPI 缩放**：界面缩放比例
- **Mica 效果**：Windows 11 毛玻璃效果（仅 Win11）

### 日志文件

程序运行日志保存在 `AppData/log.txt`，包括：
- 应用启动/关闭记录
- 转录任务详细日志
- 错误信息和调试输出

查看日志文件可帮助诊断问题和了解处理进度。

## 📦 打包部署

使用 Nuitka 打包为独立可执行文件：

```bash
python deploy.py
```

打包后的文件位于 `dist/` 目录。

或使用 Inno Setup 创建安装程序：

```bash
# 编辑 installer.iss 文件后
iscc installer.iss
```

## 🛠️ 项目结构

```
Shinobu-Voice-Transcriber/
├── app/
│   ├── common/               # 公共模块
│   │   ├── config.py        # 配置管理
│   │   ├── models/          # Whisper 模型文件
│   │   ├── model_scanner.py # 模型扫描器
│   │   └── ...
│   ├── service/             # 业务服务
│   │   └── transcription_service.py  # 转录核心服务
│   ├── view/                # 界面视图
│   │   ├── main_window.py   # 主窗口
│   │   ├── transcribe_interface.py  # 转录界面
│   │   ├── task_interface.py        # 任务日志界面
│   │   └── setting_interface.py     # 设置界面
│   ├── resource/            # 资源文件
│   │   ├── i18n/           # 国际化翻译
│   │   ├── images/         # 图标、图片
│   │   └── qss/            # 样式表
│   └── tools/              # 工具（ffmpeg、whisper-faster）
├── AppData/                # 应用数据（配置、日志）
├── Shinobu-Voice-Transcriber.py  # 程序入口
├── requirements.txt        # Python 依赖
├── deploy.py              # 部署脚本
├── installer.iss          # 安装程序配置
└── README.md              # 本文件
```

## ❓ 常见问题

### Q: 内存不足错误怎么办？

**A**: 尝试以下方法：
1. 使用更小的模型（base 或 small）
2. 关闭其他占用内存的程序
3. 处理较短的音频片段
4. 升级系统内存

### Q: 模型下载失败？

**A**: 
1. 检查网络连接
2. 可能需要科学上网访问 Hugging Face
3. 可手动下载模型文件放入 `app/common/models/whisper-faster/` 目录

### Q: FFmpeg 错误？

**A**: 
1. 确认 FFmpeg 已正确安装
2. Windows 用户检查 `app/tools/ffmpeg.exe` 是否存在
3. Linux/macOS 用户运行 `ffmpeg -version` 确认

### Q: 支持哪些音视频格式？

**A**: 支持 FFmpeg 能处理的所有格式，常见的包括：
- 音频：MP3, WAV, AAC, FLAC, M4A
- 视频：MP4, AVI, MKV, MOV, FLV

### Q: 双语字幕如何生成？

**A**: 
1. 首先生成原文 SRT
2. 使用翻译工具（如 ChatGPT）翻译 SRT 文件
3. 将翻译后的 SRT 文件作为输入，选择"双语 SRT/TXT/XLSX"格式

### Q: 转录速度慢？

**A**: 
- 转录速度取决于音频长度、模型大小和硬件配置
- Medium 模型：约为实时速度的 1-2 倍（10 分钟音频需 5-10 分钟）
- 使用 GPU 版本可显著提升速度（需要 CUDA 支持）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

开发建议：
1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送到分支：`git push origin feature/AmazingFeature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 GNU General Public License v3.0 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别模型
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - 高效的 Whisper 实现
- [PySide6](https://wiki.qt.io/Qt_for_Python) - Qt Python 绑定
- [QFluentWidgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) - Fluent Design 组件库
- [FFmpeg](https://ffmpeg.org/) - 多媒体处理框架

## 📮 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 [Issue](../../issues)
- 发送邮件（如有）
- 加入讨论（如有论坛/群组）

---

<div align="center">

**如果这个项目对您有帮助，请给它一个 ⭐ Star！**

Made with ❤️ by Shinobu-Voice-Transcriber Team

</div>
