# Core/router.py
"""
Task Router - ตัดสินใจเลือก handler ตาม intent
"""

import re
import yaml
from typing import Dict, Optional, List, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TaskRouter:
    def __init__(self, config_path: str = "Workspace/Config/routing_rules.yaml"):
        self.config_path = config_path
        self.intent_patterns = {}
        self.manual_overrides = {}
        self.load_config()

    def load_config(self):
        """โหลดการตั้งค่า routing"""
        try:
            config_path = Path(self.config_path)
            if not config_path.exists():
                logger.warning(f"Routing config not found: {self.config_path}")
                self._set_defaults()
                return

            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            patterns = config.get("intent_detection", {}).get("patterns", {})
            for intent, data in patterns.items():
                self.intent_patterns[intent] = data

            self.manual_overrides = config.get("manual_overrides", {})

        except Exception as e:
            logger.error(f"Failed to load routing config: {e}")
            self._set_defaults()

    def _set_defaults(self):
        """ตั้งค่าเริ่มต้น"""
        self.intent_patterns = {
            "slip_upload": {
                "keywords": ["สลิป", "โอนเงิน", "transfer", "slip", "แนบรูป"],
                "requires_vision": True,
            },
            "balance_query": {
                "keywords": ["ยอด", "สรุป", "เท่าไร", "balance"],
                "requires_sql": True,
            },
            "room_query": {
                "keywords": ["ห้อง", "ว่าง", "จอง", "เช็คอิน"],
                "requires_sql": True,
            },
            "customer_query": {
                "keywords": ["ลูกค้า", "ค้นหา", "เบอร์"],
                "requires_sql": True,
            },
            "report_request": {
                "keywords": ["รายงาน", "excel", "รายเดือน"],
                "requires_generation": True,
            },
        }
        self.manual_overrides = {}

    def detect_intent(self, user_message: str) -> Tuple[str, Dict]:
        """ตรวจจับ intent จากข้อความ"""
        message_lower = user_message.lower().strip()

        # ตรวจ system command ก่อน
        for cmd, config in self.manual_overrides.items():
            if message_lower.startswith(cmd):
                return "system_command", {"command": cmd, "config": config}

        # ตรวจ keyword patterns
        best_intent = "general_chat"
        best_score = 0
        best_config = {}

        for intent, config in self.intent_patterns.items():
            score = 0
            keywords = config.get("keywords", [])

            for keyword in keywords:
                if keyword.lower() in message_lower:
                    score += config.get("priority", 1)

            if score > best_score:
                best_score = score
                best_intent = intent
                best_config = config

        logger.info(f"Detected intent: {best_intent} (score: {best_score})")
        return best_intent, best_config

    def get_handler_for_intent(self, intent: str) -> str:
        """map intent ไปยัง handler"""
        handler_map = {
            "slip_upload": "SlipHandler",
            "balance_query": "QueryHandler",
            "room_query": "QueryHandler",
            "customer_query": "QueryHandler",
            "report_request": "ReportHandler",
            "system_command": "SystemHandler",
            "general_chat": "GeneralHandler",
        }
        return handler_map.get(intent, "GeneralHandler")

    def should_use_vision(self, config: Dict) -> bool:
        """ตรวจสอบว่าต้องใช้ vision หรือไม่"""
        return config.get("requires_vision", False)

    def should_use_sql(self, config: Dict) -> bool:
        """ตรวจสอบว่าต้องใช้ SQL หรือไม่"""
        return config.get("requires_sql", False)

    def is_cacheable(self, config: Dict) -> bool:
        """ตรวจสอบว่าสามารถ cache ได้หรือไม่"""
        return config.get("cacheable", False)

    def get_privacy_level(self, config: Dict) -> str:
        """ดึงระดับความเป็นส่วนตัว"""
        return config.get("privacy_level", "normal")

    def parse_command(self, user_message: str) -> Optional[Dict]:
        """แยกวิเคราะห์คำสั่งพิเศษ"""
        message_lower = user_message.lower().strip()

        if message_lower.startswith("/"):
            parts = message_lower.split()
            cmd = parts[0]

            if cmd in self.manual_overrides:
                return {"command": cmd, "config": self.manual_overrides[cmd]}

        return None
