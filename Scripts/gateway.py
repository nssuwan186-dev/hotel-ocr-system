#!/usr/bin/env python3
"""
Scripts/gateway.py
Entry Point หลักของระบบ OpenClaw Hotel AI
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional, Any

# โหลด .env file
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# เพิ่ม path สำหรับ import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from Workspace.Core.model_manager import ModelManager
from Workspace.Core.context_engine import ContextEngine
from Workspace.Core.database import DatabaseManager
from Workspace.Core.router import TaskRouter
from Workspace.Core.security_filter import SecurityFilter
from Workspace.Handlers.slip_handler import SlipHandler
from Workspace.Handlers.query_handler import QueryHandler
from Workspace.Handlers.booking_handler import BookingHandler
from Workspace.Handlers.report_handler import ReportHandler
from Workspace.Integrations.prompt_loader import PromptLoader
from Workspace.Integrations.telegram_bot import TelegramBot

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OpenClawGateway:
    """
    Gateway หลักสำหรับระบบ Multi-Model AI Agent
    """

    def __init__(self):
        self.model_manager: Optional[ModelManager] = None
        self.context_engine: Optional[ContextEngine] = None
        self.db_manager: Optional[DatabaseManager] = None
        self.router: Optional[TaskRouter] = None
        self.security: Optional[SecurityFilter] = None
        self.prompt_loader: Optional[PromptLoader] = None

        self.slip_handler: Optional[SlipHandler] = None
        self.query_handler: Optional[QueryHandler] = None
        self.booking_handler: Optional[BookingHandler] = None
        self.report_handler: Optional[ReportHandler] = None

        self.telegram_bot: Optional[TelegramBot] = None
        self.mode = "auto"  # auto, manual, offline, economy

        self.initialized = False

    async def initialize(self):
        """เริ่มต้นระบบทั้งหมด"""
        logger.info("🚀 Initializing OpenClaw Hotel AI System...")

        try:
            # 1. เริ่มต้น Database
            logger.info("📦 Initializing Database...")
            self.db_manager = DatabaseManager("Workspace/Database/hotel_account.db")
            self.db_manager.init_database()

            # 2. เริ่มต้น Model Manager
            logger.info("🤖 Initializing Model Manager...")
            self.model_manager = ModelManager("Workspace/Config/models.yaml")

            # 3. เริ่มต้น Context Engine
            logger.info("🧠 Initializing Context Engine...")
            self.context_engine = ContextEngine()

            # 4. เริ่มต้น Router
            logger.info("🛤️ Initializing Task Router...")
            self.router = TaskRouter("Workspace/Config/routing_rules.yaml")

            # 5. เริ่มต้น Security Filter
            logger.info("🔒 Initializing Security Filter...")
            self.security = SecurityFilter()

            # 6. เริ่มต้น Prompt Loader
            logger.info("📝 Initializing Prompt Loader...")
            self.prompt_loader = PromptLoader("Workspace/Config/prompts")

            # 7. เริ่มต้น Handlers
            logger.info("⚡ Initializing Handlers...")
            self.slip_handler = SlipHandler(
                self.model_manager, self.db_manager, self.prompt_loader
            )
            self.query_handler = QueryHandler(
                self.model_manager, self.db_manager, self.prompt_loader
            )
            self.booking_handler = BookingHandler(self.model_manager, self.db_manager)
            self.report_handler = ReportHandler(
                self.model_manager, self.db_manager, self.prompt_loader
            )

            # 8. เริ่มต้น Telegram Bot (ถ้ามี token)
            telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if telegram_token:
                logger.info("📱 Initializing Telegram Bot...")
                self.telegram_bot = TelegramBot(telegram_token)

            self.initialized = True
            logger.info("✅ OpenClaw System initialized successfully!")

            return {"success": True, "message": "ระบบพร้อมใช้งาน"}

        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return {"success": False, "error": str(e)}

    async def process_message(
        self, message: str, image_data: str = None
    ) -> Dict[str, Any]:
        """ประมวลผลข้อความจากผู้ใช้"""
        if not self.initialized:
            await self.initialize()

        # ตรวจจับ intent
        intent, config = self.router.detect_intent(message)
        logger.info(f"📌 Detected intent: {intent}")

        # ตรวจ system command
        command = self.router.parse_command(message)
        if command:
            return await self._handle_command(command, message)

        # ส่งไป handler ที่เหมาะสม
        if intent == "slip_upload":
            return await self._handle_slip(image_data)
        elif intent in ["balance_query", "room_query", "customer_query"]:
            return await self.query_handler.handle_query(message)
        elif intent == "report_request":
            return await self._handle_report_request(message)
        else:
            return await self.query_handler.handle_query(message)

    async def _handle_command(self, command: Dict, message: str) -> Dict:
        """จัดการ system command"""
        config = command.get("config", {})
        cmd = command.get("command")

        if cmd == "/pro":
            self.mode = "manual"
            return {"success": True, "message": "สลับไปใช้ Gemini Pro แล้ว"}
        elif cmd == "/local":
            self.mode = "offline"
            return {"success": True, "message": "สลับไปใช้ Local Mode แล้ว"}
        elif cmd == "/offline":
            self.mode = "offline"
            return {"success": True, "message": "โหมดออฟไลน์: ใช้ Local LLM เท่านั้น"}
        elif cmd == "/economy":
            self.mode = "economy"
            return {"success": True, "message": "โหมดประหยัด: ใช้โมเดลราคาถูก"}
        elif cmd == "/auto":
            self.mode = "auto"
            return {"success": True, "message": "กลับสู่โหมดอัตโนมัติ"}

        return {"success": False, "error": "Unknown command"}

    async def _handle_slip(self, image_data: str = None) -> Dict:
        """จัดการสลิป"""
        return await self.slip_handler.analyze_slip(image_base64=image_data)

    async def _handle_report_request(self, message: str) -> Dict:
        """จัดการรายงาน"""
        message_lower = message.lower()

        if "รายวัน" in message_lower or "daily" in message_lower:
            return await self.report_handler.generate_daily_report()
        elif "รายสัปดาห์" in message_lower or "weekly" in message_lower:
            return await self.report_handler.generate_weekly_report()
        elif "รายเดือน" in message_lower or "monthly" in message_lower:
            return await self.report_handler.generate_monthly_report()
        elif "วิเคราะห์" in message_lower or "analysis" in message_lower:
            return await self.report_handler.generate_ai_analysis()

        return await self.report_handler.generate_daily_report()

    async def handle_telegram_update(self, update: Dict) -> Dict:
        """จัดการ update จาก Telegram"""
        if not self.telegram_bot:
            return {"success": False, "error": "Telegram bot not initialized"}

        parsed = self.telegram_bot.parse_update(update)

        if parsed.get("type") == "message":
            text = parsed.get("text", "")
            chat_id = parsed.get("chat_id")

            # ตรวจสอบว่าเป็นรูปภาพหรือไม่
            if parsed.get("photo"):
                result = await self._handle_slip_from_telegram(update)
                await self.telegram_bot.send_message(
                    chat_id, f"✅ วิเคราะห์สลิปสำเร็จ!\n\n{result.get('message', '')}"
                )
                return result
            else:
                result = await self.process_message(text)

                response_text = result.get("response", result.get("message", ""))
                if not response_text:
                    response_text = str(result)

                await self.telegram_bot.send_message(chat_id, response_text)
                return result

        return {"success": True}

    async def _handle_slip_from_telegram(self, update: Dict) -> Dict:
        """จัดการสลิปจาก Telegram"""
        photo = update.get("message", {}).get("photo", [])
        if photo:
            # ในการใช้งานจริง ต้องดาวน์โหลดรูปภาพก่อน
            return {"success": True, "message": "รับรูปภาพแล้ว กำลังวิเคราะห์..."}
        return {"success": False, "error": "No photo found"}

    async def shutdown(self):
        """ปิดระบบ"""
        logger.info("🛑 Shutting down OpenClaw System...")

        if self.model_manager:
            await self.model_manager.close()

        if self.db_manager:
            self.db_manager.close()

        logger.info("✅ System shutdown complete")


# ========== Main Functions ==========


async def run_interactive():
    """รันในโหมด interactive"""
    gateway = OpenClawGateway()
    await gateway.initialize()

    print("\n" + "=" * 50)
    print("🏨 OpenClaw Hotel AI System")
    print("=" * 50)
    print("พิมพ์ข้อความเพื่อสนทนากับยูมิ (พิมพ์ 'exit' เพื่อออก)")
    print("=" * 50 + "\n")

    while True:
        try:
            user_input = input("คุณ: ").strip()

            if user_input.lower() in ["exit", "quit", "ออก"]:
                break

            if not user_input:
                continue

            result = await gateway.process_message(user_input)

            if result.get("success"):
                if result.get("response"):
                    print(f"ยูมิ: {result['response']}")
                elif result.get("message"):
                    print(f"ยูมิ: {result['message']}")
            else:
                print(f"❌ Error: {result.get('error')}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

    await gateway.shutdown()


async def run_telegram():
    """รันในโหมด Telegram Bot"""
    gateway = OpenClawGateway()
    await gateway.initialize()

    if not gateway.telegram_bot:
        print("❌ Telegram bot not configured")
        return

    await gateway.telegram_bot.set_webhook()
    print("📱 Telegram bot is running...")


async def run_test():
    """รันการทดสอบ"""
    gateway = OpenClawGateway()
    result = await gateway.initialize()

    print("\n" + "=" * 50)
    print("🧪 OpenClaw System Test")
    print("=" * 50)

    if result.get("success"):
        print("✅ System initialized successfully!")

        # ทดสอบ Query
        print("\n📝 Testing query handler...")
        result = await gateway.query_handler.handle_query("ยอดสะสมเท่าไหร่?")
        print(f"Result: {result}")

        # ทดสอบ Rooms
        print("\n📝 Testing available rooms...")
        result = await gateway.query_handler.get_available_rooms()
        print(f"Available: {result.get('count', 0)} rooms")

        # ทดสอบ Daily Report
        print("\n📝 Testing daily report...")
        result = await gateway.report_handler.generate_daily_report()
        print(f"Report: {result.get('formatted', '')[:200]}...")

    else:
        print(f"❌ Initialization failed: {result.get('error')}")

    await gateway.shutdown()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OpenClaw Hotel AI System")
    parser.add_argument(
        "mode",
        choices=["interactive", "telegram", "test"],
        default="interactive",
        help="Run mode",
    )
    args = parser.parse_args()

    if args.mode == "interactive":
        asyncio.run(run_interactive())
    elif args.mode == "telegram":
        asyncio.run(run_telegram())
    elif args.mode == "test":
        asyncio.run(run_test())
