# Core/security_filter.py
"""
Security Filter - กรองข้อมูลที่ sensitive และ dangerous
"""

import re
import os
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class SecurityFilter:
    def __init__(self):
        self.dangerous_patterns = [
            r"drop\s+table",
            r"drop\s+database",
            r"delete\s+from",
            r"truncate\s+table",
            r"alter\s+table",
            r"--",
            r";\s*drop",
            r"exec\s*\(",
            r"execute\s*\(",
            r"sp_executesql",
            r"shutdown\s+with",
        ]

        self.sensitive_keywords = [
            "api_key",
            "apikey",
            "password",
            "secret",
            "token",
            "credit_card",
            "cvv",
            "ssn",
            "social_security",
        ]

        self.dangerous_sql_keywords = [
            "DROP",
            "DELETE",
            "TRUNCATE",
            "ALTER",
            "CREATE",
            "INSERT",
            "UPDATE",
            "EXEC",
            "EXECUTE",
        ]

    def is_safe_sql(self, sql: str) -> Tuple[bool, str]:
        """ตรวจสอบความปลอดภัยของ SQL"""
        sql_upper = sql.upper()

        for pattern in self.dangerous_patterns:
            if re.search(pattern, sql_upper, re.IGNORECASE):
                return False, f"Dangerous pattern detected: {pattern}"

        dangerous_count = sum(
            1 for kw in self.dangerous_sql_keywords if kw in sql_upper
        )

        if dangerous_count > 0:
            if "SELECT" not in sql_upper:
                return False, "Only SELECT queries are allowed for security"

        return True, "OK"

    def mask_sensitive_data(self, data: str, data_type: str = "phone") -> str:
        """ซ่อนข้อมูลที่ sensitive"""
        if data_type == "phone":
            if len(data) >= 10:
                return data[:3] + "XXX" + data[-4:]
            return "XXX-XXX-XXXX"

        elif data_type == "id_card":
            if len(data) >= 8:
                return data[:4] + "XXXX" + data[-4:]
            return "XXXX-XXXX"

        return "***"

    def contains_sensitive_info(self, text: str) -> bool:
        """ตรวจสอบว่าข้อความมีข้อมูล sensitive หรือไม่"""
        text_lower = text.lower()

        for keyword in self.sensitive_keywords:
            if keyword in text_lower:
                logger.warning(f"Sensitive keyword detected: {keyword}")
                return True

        return False

    def sanitize_prompt(self, prompt: str) -> str:
        """ทำความสะอาด prompt"""
        sanitized = prompt

        for keyword in self.sensitive_keywords:
            pattern = re.compile(f"{keyword}[=:]\\s*[\\w-]+", re.IGNORECASE)
            sanitized = pattern.sub(f"{keyword}=[REDACTED]", sanitized)

        return sanitized

    def validate_api_keys(self) -> Dict[str, bool]:
        """ตรวจสอบว่า API keys ถูกตั้งค่าหรือไม่"""
        required_keys = ["GEMINI_API_KEY"]
        optional_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]

        result = {}

        for key in required_keys:
            result[key] = bool(os.getenv(key))

        for key in optional_keys:
            result[key] = bool(os.getenv(key))

        return result

    def check_file_upload(self, filename: str) -> Tuple[bool, str]:
        """ตรวจสอบไฟล์ที่อัปโหลด"""
        allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt"]

        ext = os.path.splitext(filename)[1].lower()

        if ext not in allowed_extensions:
            return False, f"Extension {ext} not allowed"

        max_size = 10 * 1024 * 1024

        return True, "OK"

    def filter_response(self, response: str, privacy_level: str = "normal") -> str:
        """กรองข้อมูลใน response ตามระดับ privacy"""
        if privacy_level == "high":
            phone_pattern = r"(\d{3,4}[-\s]?\d{3,4}[-\s]?\d{4})"
            response = re.sub(phone_pattern, "XXX-XXX-XXXX", response)

        return response
