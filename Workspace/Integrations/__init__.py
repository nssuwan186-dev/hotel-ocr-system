# Integrations/__init__.py
"""
Integrations - เชื่อมต่อกับภายนอก
"""

from .telegram_bot import TelegramBot
from .prompt_loader import PromptLoader

__all__ = ["TelegramBot", "PromptLoader"]
