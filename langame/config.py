from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

env = os.getenv("DJANGO_ENV", "debug")
env_file = BASE_DIR / f".env.{env}"

# 不覆盖已有环境变量（Docker env_file / environment 注入的优先）
load_dotenv(env_file, override=False)
