# Handlers/slip_handler.py
"""
Slip Handler - จัดการการวิเคราะห์สลิปโอนเงิน
"""

import json
import re
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SlipHandler:
    def __init__(self, model_manager, db_manager, prompt_loader):
        self.model_manager = model_manager
        self.db_manager = db_manager
        self.prompt_loader = prompt_loader
        self.prompt_template = None
        self._load_prompt()

    def _load_prompt(self):
        """โหลด prompt สำหรับวิเคราะห์สลิป"""
        try:
            prompt_path = Path("Workspace/Config/prompts/vision_slip.txt")
            if prompt_path.exists():
                with open(prompt_path, "r", encoding="utf-8") as f:
                    self.prompt_template = f.read()
        except Exception as e:
            logger.error(f"Failed to load slip prompt: {e}")
            self.prompt_template = self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """Prompt เริ่มต้น"""
        return """คุณเป็นผู้เชี่ยวชาญวิเคราะห์สลิปโอนเงินธนาคารไทย
ให้วิเคราะห์และตอบกลับเป็น JSON:
{"amount": <จำนวนเงิน>, "date": "YYYY-MM-DD", "time": "HH:MM", "reference": "...", "from_bank": "...", "to_bank": "...", "to_account": "...", "to_name": "...", "confidence": <0.0-1.0>, "needs_review": true/false}"""

    async def analyze_slip(
        self, image_path: str = None, image_base64: str = None
    ) -> Dict[str, Any]:
        """วิเคราะห์สลิปจากรูปภาพ"""
        try:
            prompt = self.prompt_template

            response = await self.model_manager.generate(
                prompt=prompt,
                model_name="gemini-2.0-flash",
                image_path=image_path,
                image_base64=image_base64,
                json_mode=True,
            )

            if response.get("error"):
                return {"success": False, "error": response.get("message")}

            result = self._parse_slip_response(response["text"])

            logger.info(
                f"Slip analyzed: amount={result.get('amount')}, confidence={result.get('confidence')}"
            )

            return {
                "success": True,
                "data": result,
                "model_used": response.get("model"),
            }

        except Exception as e:
            logger.error(f"Error analyzing slip: {e}")
            return {"success": False, "error": str(e)}

    def _parse_slip_response(self, text: str) -> Dict:
        """แปลง response เป็น JSON"""
        try:
            cleaned = text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            return json.loads(cleaned.strip())

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse slip JSON: {e}")
            return {
                "amount": 0,
                "date": "",
                "time": "",
                "confidence": 0,
                "needs_review": True,
                "review_reason": "Parse error",
            }

    async def confirm_and_save(
        self, slip_data: Dict, user_confirmed: bool = True
    ) -> Dict:
        """ยืนยันและบันทึกข้อมูลสลิป"""
        if not user_confirmed:
            return {"success": False, "message": "รอการยืนยันจากผู้ใช้"}

        if slip_data.get("needs_review"):
            return {
                "success": False,
                "message": "สลิปต้องตรวจสอบด้วยตนเองก่อนบันทึก",
                "data": slip_data,
            }

        try:
            result = self.db_manager.add_transaction(
                date=slip_data.get("date", datetime.now().strftime("%Y-%m-%d")),
                item_name=slip_data.get("to_name", "Unknown"),
                income=slip_data.get("amount", 0),
                note=f"สลิปโอน: {slip_data.get('reference', '')} | จาก: {slip_data.get('from_name', '')}",
                category="รายรับ",
            )

            return {
                "success": True,
                "message": f"บันทึกสำเร็จ! ยอดเงิน {slip_data.get('amount')} บาท",
                "transaction_id": result.get("id"),
                "new_balance": result.get("balance"),
            }

        except Exception as e:
            logger.error(f"Error saving slip: {e}")
            return {"success": False, "error": str(e)}
