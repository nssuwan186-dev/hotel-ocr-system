# Integrations/prompt_loader.py
"""
Prompt Loader - โหลด prompt templates
"""

import os
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PromptLoader:
    def __init__(self, prompts_dir: str = "Workspace/Config/prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompts: Dict[str, str] = {}
        self.system_dir = Path("Workspace/Config/system")
        self.load_all_prompts()

    def load_all_prompts(self):
        """โหลด prompts ทั้งหมด"""
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory not found: {self.prompts_dir}")
            return

        for file_path in self.prompts_dir.glob("*.txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    prompt_name = file_path.stem
                    self.prompts[prompt_name] = f.read()
                logger.info(f"Loaded prompt: {prompt_name}")
            except Exception as e:
                logger.error(f"Error loading prompt {file_path.name}: {e}")

    def get_prompt(self, name: str) -> Optional[str]:
        """ดึง prompt ตามชื่อ"""
        return self.prompts.get(name)

    def load_prompt(self, name: str) -> str:
        """ดึง prompt หรือ return default"""
        prompt = self.get_prompt(name)
        if prompt:
            return prompt
        logger.warning(f"Prompt not found: {name}")
        return self._get_default_prompt(name)

    def _get_default_prompt(self, name: str) -> str:
        """Prompt เริ่มต้นถ้าไม่มี"""
        defaults = {
            "vision_slip": "วิเคราะห์สลิปและตอบกลับเป็น JSON",
            "sql_generator": "สร้าง SQL query จากคำขอ",
            "analysis_deep": "วิเคราะห์ข้อมูลธุรกิจ",
            "customer_crm": "วิเคราะห์ข้อมูลลูกค้า",
            "fallback_local": "ตอบคำถามในโหมดออฟไลน์",
        }
        return defaults.get(name, "ตอบคำถามเป็นภาษาไทย")

    def get_system_prompt(self, name: str = "soul_core") -> str:
        """โหลด system prompt"""
        system_path = self.system_dir / f"{name}.txt"

        if system_path.exists():
            try:
                with open(system_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error loading system prompt: {e}")

        return self._get_default_system_prompt()

    def _get_default_system_prompt(self) -> str:
        """System prompt เริ่มต้น"""
        return """คุณคือ U'mi ผู้ช่วยบัญชีหอพัก
- ตอบเป็นภาษาไทย
- ใช้ภาษาที่เป็นกันเองแต่ professional
- ยอดเงินใส่ comma (เช่น 3,500 บาท)
- ใช้ emoji ช่วยสื่อความหมาย"""

    def fill_prompt(self, prompt_name: str, **kwargs) -> str:
        """เติมข้อมูลลงใน prompt"""
        prompt = self.load_prompt(prompt_name)

        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"
            prompt = prompt.replace(placeholder, str(value))

        return prompt

    def list_prompts(self) -> list:
        """รายชื่อ prompts ที่มี"""
        return list(self.prompts.keys())

    def reload(self):
        """โหลด prompts ใหม่"""
        self.prompts = {}
        self.load_all_prompts()
