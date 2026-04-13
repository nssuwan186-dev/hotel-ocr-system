# Handlers/query_handler.py
"""
Query Handler - จัดการคำถามและการค้นหาข้อมูล
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class QueryHandler:
    def __init__(self, model_manager, db_manager, prompt_loader):
        self.model_manager = model_manager
        self.db_manager = db_manager
        self.prompt_loader = prompt_loader

    async def handle_query(
        self, user_message: str, context: Dict = None
    ) -> Dict[str, Any]:
        """จัดการคำถามทั่วไป"""
        try:
            is_sql_query = self._is_sql_needed(user_message)

            if is_sql_query:
                return await self._handle_database_query(user_message)
            else:
                return await self._handle_general_query(user_message, context)

        except Exception as e:
            logger.error(f"Error handling query: {e}")
            return {"success": False, "error": str(e)}

    def _is_sql_needed(self, message: str) -> bool:
        """ตรวจสอบว่าต้องใช้ SQL หรือไม่"""
        sql_keywords = ["ยอด", "สรุป", "ห้อง", "ลูกค้า", "จอง", "ราย", "วัน", "เดือน", "ปี"]
        message_lower = message.lower()
        return any(kw in message_lower for kw in sql_keywords)

    async def _handle_database_query(self, user_message: str) -> Dict[str, Any]:
        """จัดการคำถามที่ต้อง query ฐานข้อมูล"""
        try:
            prompt = self._build_sql_prompt(user_message)

            response = await self.model_manager.generate(
                prompt=prompt, model_name="gemini-2.0-flash", json_mode=True
            )

            if response.get("error"):
                return {"success": False, "error": response.get("message")}

            sql_result = json.loads(response["text"])

            if not sql_result.get("read_only", True):
                return {"success": False, "error": "ไม่อนุญาตให้เปลี่ยนแปลงข้อมูล"}

            data = self.db_manager.execute_query(sql_result.get("sql", ""))

            return {
                "success": True,
                "data": data,
                "explanation": sql_result.get("explanation", ""),
                "model_used": response.get("model"),
            }

        except Exception as e:
            logger.error(f"Error in database query: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_general_query(
        self, user_message: str, context: Dict = None
    ) -> Dict[str, Any]:
        """จัดการคำถามทั่วไปไม่ต้องใช้ database"""
        try:
            system_context = context.get("system_context", "") if context else ""
            conversation = context.get("conversation_history", "") if context else ""

            prompt = f"""คุณคือ U'mi ผู้ช่วยบัญชีหอพัก

ข้อมูลระบบ:
{system_context}

ประวัติการสนทนา:
{conversation}

คำถาม: {user_message}

ตอบเป็นภาษาไทย ใช้ภาษาที่เป็นกันเอง แต่ professional"""

            response = await self.model_manager.generate(
                prompt=prompt, model_name="gemini-2.0-flash"
            )

            if response.get("error"):
                return {"success": False, "error": response.get("message")}

            return {
                "success": True,
                "response": response["text"],
                "model_used": response.get("model"),
            }

        except Exception as e:
            logger.error(f"Error in general query: {e}")
            return {"success": False, "error": str(e)}

    def _build_sql_prompt(self, user_message: str) -> str:
        """สร้าง prompt สำหรับสร้าง SQL"""
        return f"""คุณเป็น SQL Expert สำหรับระบบบัญชีหอพัก

ฐานข้อมูล: SQLite (hotel_account.db)
วันที่ใช้: พ.ศ. (เช่น 2568-04-09)

SCHEMA:
- transactions: id, date, item_name, phone, room, nights, expense, income, balance, deposit_cash, note, category
- rooms: room_number, building, floor, room_type, price_per_night, status, note
- customers: customer_id, customer_name, phone, nationality
- bookings: id, room_number, customer_name, check_in_date, nights, channel, deposit, note
- employees: employee_id, full_name, position, pay_type, salary, active

คำขอ: {user_message}

ตอบกลับเป็น JSON:
{{
  "sql": "คำสั่ง SQL",
  "explanation": "อธิบาย",
  "read_only": true/false
}}

กฎ: SELECT เท่านั้น, ห้าม DROP/DELETE/TRUNCATE"""

    async def get_balance(self) -> Dict[str, Any]:
        """ดึงยอดสะสม"""
        try:
            balance = self.db_manager.get_latest_balance()
            daily = self.db_manager.get_daily_summary()

            return {
                "success": True,
                "balance": balance,
                "today_income": daily.get("income", 0),
                "today_expense": daily.get("expense", 0),
                "today_bookings": daily.get("bookings", 0),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_available_rooms(self) -> Dict[str, Any]:
        """ดึงรายการห้องว่าง"""
        try:
            rooms = self.db_manager.get_available_rooms()
            all_rooms = self.db_manager.get_all_rooms()

            return {
                "success": True,
                "available_rooms": rooms,
                "all_rooms": all_rooms,
                "available_count": len(rooms),
                "total_count": len(all_rooms),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def search_customer(self, query: str) -> Dict[str, Any]:
        """ค้นหาลูกค้า"""
        try:
            customers = self.db_manager.search_customers(query)

            results = []
            for customer in customers:
                history = self.db_manager.get_customer_history(
                    customer["customer_name"]
                )
                results.append({**customer, "history": history})

            return {"success": True, "results": results, "count": len(results)}
        except Exception as e:
            return {"success": False, "error": str(e)}
