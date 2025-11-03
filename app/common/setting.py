# coding: utf-8
from pathlib import Path

# change DEBUG to False if you want to compile the code to exe
DEBUG = "__compiled__" not in globals()


YEAR = 2025
AUTHOR = "Nana1237854"
VERSION = "v1.1.0"
APP_NAME = "Shinobu Voice Transcriber"
HELP_URL = "https://github.com/Nana1237854/Shinobu-Voice-Transcriber"
REPO_URL = "https://github.com/Nana1237854/Shinobu-Voice-Transcriber"
FEEDBACK_URL = "https://github.com/Nana1237854/Shinobu-Voice-Transcriber/issues"
DOC_URL = "https://github.com/Nana1237854/Shinobu-Voice-Transcriber/blob/main/README.md"

CONFIG_FOLDER = Path('AppData').absolute()
CONFIG_FILE = CONFIG_FOLDER / "config.json"

LOG_PATH = CONFIG_FOLDER / "log.txt"
