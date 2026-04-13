# Core/context_engine.py
"""
จัดการบริบท (Context) และความจำระยะยาว
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import re


class ContextEngine:
    def __init__(
        self,
        db_path: str = "Workspace/Database/hotel_account.db",
        memory_path: str = "Workspace/memory.md",
    ):
        self.db_path = db_path
        self.memory_path = memory_path
        self.session_context: Dict[str, Any] = {}
        self.conversation_history: List[Dict] = []
        self.max_history = 10

    def load_system_context(self) -> str:
        """โหลด context ระบบพื้นฐาน"""
        context_parts = []

        try:
            mem_path = Path(self.memory_path)
            if mem_path.exists():
                with open(mem_path, "r", encoding="utf-8") as f:
                    memory_content = f.read()
                context_parts.append("## ความทรงจำระยะยาว\n")
                context_parts.append(self._extract_recent_memory(memory_content))
        except Exception as e:
            pass

        stats = self._get_quick_stats()
        context_parts.append(f"\n## สถิติล่าสุด\n{stats}")

        return "\n".join(context_parts)

    def _extract_recent_memory(self, content: str) -> str:
        """ดึงความทรงจำล่าสุด"""
        entries = re.findall(
            r"## \[\d{4}-\d{2}-\d{2}.*?\n(.*?)(?=## \[|\Z)", content, re.DOTALL
        )
        recent = entries[-5:] if len(entries) > 5 else entries
        return "\n\n".join(recent) if recent else "ไม่มีความทรงจำ"

    def _get_quick_stats(self) -> str:
        """ดึงสถิติเร็วจาก database"""
        try:
            db_path = Path(self.db_path)
            if not db_path.exists():
                return "- ยังไม่มีฐานข้อมูล"

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT balance FROM transactions ORDER BY id DESC LIMIT 1")
            latest_balance = cursor.fetchone()
            balance = latest_balance[0] if latest_balance else 0

            cursor.execute("SELECT COUNT(*) FROM rooms WHERE status = 'ว่าง'")
            available_rooms = cursor.fetchone()[0]

            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT COUNT(*) FROM transactions WHERE date = ? AND income > 0",
                (today,),
            )
            today_customers = cursor.fetchone()[0]

            conn.close()

            return f"""
- ยอดสะสมล่าสุด: {balance:,} บาท
- ห้องว่าง: {available_rooms} ห้อง
- ลูกค้าวันนี้: {today_customers} ราย
"""
        except Exception as e:
            return f"- ไม่สามารถดึงสถิติได้: {e}"

    def add_to_history(self, role: str, content: str, metadata: Dict = None):
        """เพิ่มข้อความในประวัติการสนทนา"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {},
        }
        self.conversation_history.append(entry)

        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history :]

    def get_conversation_context(self, last_n: int = 5) -> str:
        """ดึงบริบทจากการสนทนาล่าสุด"""
        recent = self.conversation_history[-last_n:]
        formatted = []
        for entry in recent:
            role = "ผู้ใช้" if entry["role"] == "user" else "ยูมิ"
            formatted.append(f"{role}: {entry['content'][:200]}...")
        return "\n".join(formatted)

    def build_prompt_context(self, intent: str, user_message: str) -> Dict[str, str]:
        """สร้างบริบทสำหรับ prompt"""
        return {
            "system_context": self.load_system_context(),
            "conversation_history": self.get_conversation_context(),
            "current_intent": intent,
            "user_message": user_message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "thai_date": self._get_thai_date(),
        }

    def _get_thai_date(self) -> str:
        """แปลงวันที่เป็นภาษาไทย"""
        months_th = [
            "",
            "มกราคม",
            "กุมภาพันธ์",
            "มีนาคม",
            "เมษายน",
            "พฤษภาคม",
            "มิถุนายน",
            "กรกฎาคม",
            "สิงหาคม",
            "กันยายน",
            "ตุลาคม",
            "พฤศจิกายน",
            "ธันวาคม",
        ]

        now = datetime.now()
        year_th = now.year + 543
        return f"{now.day} {months_th[now.month]} {year_th}"

    def save_important_event(self, event: str, category: str = "general"):
        """บันทึกเหตุการณ์สำคัญลง memory.md"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n## [{timestamp}] — {category}\n\n- {event}\n"

        try:
            with open(self.memory_path, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            print(f"Failed to save memory: {e}")

    def clear_session(self):
        """ล้างบริบทเซสชัน"""
        self.session_context = {}
        self.conversation_history = []

    def set_session_data(self, key: str, value: Any):
        """เก็บข้อมูลใน session"""
        self.session_context[key] = value

    def get_session_data(self, key: str, default: Any = None) -> Any:
        """ดึงข้อมูลจาก session"""
        return self.session_context.get(key, default)
