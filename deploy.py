import os
from pathlib import Path

print("="*80)
print("Shinobu-Voice-Transcriber - Nuitka 文件夹模式打包")
print("="*80)

# ==================== Nuitka 配置 ====================

# 设置 Nuitka 缓存目录到 E 盘（避免 C 盘空间不足）
cache_dir = Path("E:/Nuitka_Cache")
cache_dir.mkdir(parents=True, exist_ok=True)
os.environ['NUITKA_CACHE_DIR'] = str(cache_dir)

print(f"\n[配置] Nuitka 缓存目录: {cache_dir}")
print(f"[配置] 这将避免占用 C 盘空间\n")

# https://blog.csdn.net/qq_25262697/article/details/129302819
# https://www.cnblogs.com/happylee666/articles/16158458.html
args = [
    'nuitka',
    '--standalone',                          
    '--windows-disable-console',           # 禁用控制台窗口（GUI程序）
    '--follow-import-to=app',
    '--plugin-enable=pyside6',
    '--include-qt-plugins=sensible,styles',
    '--mingw64',                           # 使用 MinGW64
    '--assume-yes-for-downloads',          # 自动确认下载
    '--show-memory',
    '--show-progress',
    '--windows-icon-from-ico=app/resource/images/logo.ico',
    '--include-module=app',
    '--nofollow-import-to=pywin',
    '--windows-file-version=1.1.0.0',
    '--windows-product-version=1.1.0.0',
    '--windows-company-name="Shinobu Voice Transcriber"',
    '--windows-product-name="Shinobu Voice Transcriber"',
    '--windows-file-description="语音转录工具 - Shinobu Voice Transcriber"',
    # 包含资源文件
    '--include-data-dir=app/resource=app/resource',
    '--include-data-dir=app/tools=app/tools',
    # 输出设置
    '--output-dir=dist',
    'Shinobu-Voice-Transcriber.py',
] 

print("[开始] 运行 Nuitka 编译...")
print(f"[命令] {' '.join(args)}\n")

result = os.system(' '.join(args))

if result != 0:
    print(f"\n{'='*80}")
    print(f"[错误] Nuitka 编译失败，返回码: {result}")
    print(f"{'='*80}")
    exit(1)

print(f"\n{'='*80}")
print("[成功] Nuitka 编译完成！")
print(f"[输出目录] dist/Shinobu-Voice-Transcriber.dist/")
print(f"[可执行文件] dist/Shinobu-Voice-Transcriber.dist/Shinobu-Voice-Transcriber.exe")
print(f"{'='*80}")
print("\n提示：将整个 Shinobu-Voice-Transcriber.dist 文件夹复制给用户使用")