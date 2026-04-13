# Integrations/telegram_bot.py
"""
Telegram Bot - เชื่อมต่อกับ Telegram
"""

import os
import json
import asyncio
import logging
from typing import Dict, Optional, Any
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str = None, webhook_url: str = None):
        self.token = token or os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.webhook_url = webhook_url or os.getenv('TELEGRAM_WEBHOOK_URL', '')
        self.api_base = f"https://api.telegram.org/bot{self.token}"
        self.commands = {}
        self._register_default_commands()
    
    def _register_default_commands(self):
        """ลงทะเบียนคำสั่งเริ่มต้น"""
        self.commands = {
            '/start': self._handle_start,
            '/help': self._handle_help,
            '/balance': self._handle_balance,
            '/rooms': self._handle_rooms,
            '/book': self._handle_book,
            '/slip': self._handle_slip,
            '/report': self._handle_report,
        }
    
    async def send_message(self, chat_id: str, text: str, 
                          reply_markup: Dict = None) -> Dict:
        """ส่งข้อความไป Telegram"""
        if not self.token:
            return {"ok": False, "error": "No token configured"}
        
        url = f"{self.api_base}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    return await resp.json()
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {"ok": False, "error": str(e)}
    
    async def send_photo(self, chat_id: str, photo_url: str = None,
                        photo_data: bytes = None, caption: str = "") -> Dict:
        """ส่งรูปภาพไป Telegram"""
        if not self.token:
            return {"ok": False, "error": "No token configured"}
        
        url = f"{self.api_base}/sendPhoto"
        
        if photo_data:
            form = aiohttp.FormData()
            form.add_field('chat_id', chat_id)
            form.add_field('caption', caption)
            form.add_field('parse_mode', 'HTML')
            form.add_field('photo', photo_data, filename='slip.jpg', 
                         content_type='image/jpeg')
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form) as resp:
                    return await resp.json()
        elif photo_url:
            payload = {
                'chat_id': chat_id,
                'photo': photo_url,
                'caption': caption,
                'parse_mode': 'HTML'
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    return await resp.json()
        
        return {"ok": False, "error": "No photo provided"}
    
    async def set_webhook(self) -> bool:
        """ตั้งค่า webhook"""
        if not self.token or not self.webhook_url:
            logger.warning("Token or webhook URL not set")
            return False
        
        url = f"{self.api_base}/setWebhook"
        payload = {'url': self.webhook_url}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    result = await resp.json()
                    logger.info(f"Webhook set: {result}")
                    return result.get('ok', False)
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False
    
    def parse_update(self, update: Dict) -> Dict:
        """แยกวิเคราะห์ update จาก Telegram"""
        message = update.get('message', {})
        callback = update.get('callback_query', {})
        
        if message:
            return {
                'update_id': update.get('update_id'),
                'chat_id': message.get('chat', {}).get('id'),
                'user_id': message.get('from', {}).get('id'),
                'text': message.get('text', ''),
                'photo': message.get('photo', []),
                'type': 'message'
            }
        elif callback:
            return {
                'update_id': update.get('update_id'),
                'chat_id': callback.get('message', {}).get('chat', {}).get('id'),
                'user_id': callback.get('from', {}).get('id'),
                'data': callback.get('data', ''),
                'type': 'callback'
            }
        
        return {}
    
    async def _handle_start(self, update: Dict) -> str:
        """จัดการ /start"""
        return """👋 สวัสดีค่ะ! ยินดีต้อนรับสู่ U'mi Bot

ฉันคือยูมิ ผู้ช่วยบัญชีหอพักค่ะ 💚

คำสั่งที่ใช้ได้:
/balance - ดูยอดสะสม
/rooms - ดูห้องว่าง
/report - สร้างรายงาน
/slip - วิเคราะห์สลิป

หรือส่งข้อความมาถามได้เลยค่ะ!"""
    
    async def _handle_help(self, update: Dict) -> str:
        """จัดการ /help"""
        return """📖 คู่มือการใช้งาน U'mi Bot

🏠 จองห้อง:
  ส่งข้อความ: "จองห้อง B101 ชื่อ สมชาย วันที่ 2024-04-10 จำนวน 2 คืน"

💰 แนบสลิป:
  ส่งรูปภาพสลิปมาได้เลยค่ะ

📊 สอบถามข้อมูล:
  - "ยอดเท่าไหร่?"
  - "ห้องว่างมีไหม?"
  - "ลูกค้าชื่อ XXX"

💡 ส่งข้อความถามเป็นภาษาไทยได้เลยค่ะ!"""
    
    async def _handle_balance(self, update: Dict) -> str:
        """จัดการ /balance"""
        return "กรุณารอสักครู่... กำลังดึงยอดสะสมจากฐานข้อมูลค่ะ"
    
    async def _handle_rooms(self, update: Dict) -> str:
        """จัดการ /rooms"""
        return "กรุณารอสักครู่... กำลังดึงรายการห้องว่างค่ะ"
    
    async def _handle_book(self, update: Dict) -> str:
        """จัดการ /book"""
        return """📝 การจองห้อง

กรุณาระบุ:
- ห้องที่ต้องการ (เช่น B101)
- ชื่อผู้พัก
- วันที่เช็คอิน (YYYY-MM-DD)
- จำนวนคืน

ตัวอย่าง: "จอง B101 สมชาย 2024-04-10 2 คืน""""
    
    async def _handle_slip(self, update: Dict) -> str:
        """จัดการ /slip"""
        return """🖼️ วิเคราะห์สลิป

กรุณาส่งรูปภาพสลิปโอนเงินมาได้เลยค่ะ
ระบบจะวิเคราะห์:
- จำนวนเงิน
- วันที่/เวลา
- ผู้โอน/ผู้รับ"""
    
    async def _handle_report(self, update: Dict) -> str:
        """จัดการ /report"""
        return """📊 สร้างรายงาน

เลือกประเภทรายงาน:
/report_daily - รายวัน
/report_weekly - รายสัปดาห์
/report_monthly - รายเดือน"""

    def create_keyboard(self, buttons: list, cols: int = 2) -> Dict:
        """สร้าง inline keyboard"""
        rows = []
        for i in range(0, len(buttons), cols):
            row = buttons[i:i+cols]
            rows.append([{'text': btn[0], 'callback_data': btn[1]} for btn in row])
        
        return {'inline_keyboard': rows}