"""Muhit o'zgaruvchilari (.env fayl) — maxfiy sozlamalar kodda emas, alohida faylda saqlanadi.

.env fayl git'ga qo'shilmaydi (.gitignore). Namuna: .env.example
"""
import os
from pathlib import Path


def load_env_file(path: Path):
    """KEY=VALUE qatorlarini os.environ ga yuklaydi (agar o'zgaruvchi allaqachon bo'lmasa)."""
    if not path.exists():
        return
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env(name, default=''):
    return os.environ.get(name, default)


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def env_int(name, default=0):
    value = os.environ.get(name)
    return int(value) if value not in (None, '') else default


def env_list(name, default=None):
    value = os.environ.get(name)
    if not value:
        return list(default or [])
    return [item.strip() for item in value.split(',') if item.strip()]
