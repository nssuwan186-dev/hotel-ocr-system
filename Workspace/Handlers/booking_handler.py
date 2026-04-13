# Handlers/booking_handler.py
"""
Booking Handler - จัดการการจองห้องพัก
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class BookingHandler:
    def __init__(self, model_manager, db_manager):
        self.model_manager = model_manager
        self.db_manager = db_manager

    async def create_booking(
        self,
        customer_name: str,
        room_number: str,
        check_in_date: str,
        nights: int,
        channel: str = "เงินสด",
        deposit: int = 0,
        phone: str = "",
        note: str = "",
    ) -> Dict[str, Any]:
        """สร้างการจองใหม่"""
        try:
            available_rooms = self.db_manager.get_available_rooms()
            room_exists = any(r["room_number"] == room_number for r in available_rooms)

            if not room_exists:
                all_rooms = self.db_manager.get_all_rooms()
                room_info = next(
                    (r for r in all_rooms if r["room_number"] == room_number), None
                )
                if room_info and room_info.get("status") != "ว่าง":
                    return {
                        "success": False,
                        "error": f"ห้อง {room_number} ไม่ว่าง สถานะ: {room_info.get('status')}",
                    }

            booking_id = self.db_manager.add_booking(
                room_number=room_number,
                customer_name=customer_name,
                check_in_date=check_in_date,
                nights=nights,
                channel=channel,
                deposit=deposit,
                note=note,
            )

            self.db_manager.add_transaction(
                date=check_in_date,
                item_name=customer_name,
                phone=phone,
                room=room_number,
                nights=nights,
                income=deposit,
                deposit_cash=deposit,
                note=f"มัดจำการจองห้อง {room_number}",
                category="รายรับ",
            )

            self.db_manager.update_room_status(room_number, "ไม่ว่าง")

            return {
                "success": True,
                "booking_id": booking_id,
                "room": room_number,
                "check_in": check_in_date,
                "nights": nights,
                "deposit": deposit,
                "message": f"จองห้อง {room_number} สำเร็จ! เช็คอิน {check_in_date} พัก {nights} คืน",
            }

        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            return {"success": False, "error": str(e)}

    async def check_in(
        self,
        room_number: str,
        customer_name: str,
        nights: int,
        price_per_night: int,
        channel: str = "เงินสด",
        phone: str = "",
    ) -> Dict[str, Any]:
        """เช็คอินแขก"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            result = self.db_manager.add_transaction(
                date=today,
                item_name=customer_name,
                phone=phone,
                room=room_number,
                nights=nights,
                income=price_per_night * nights,
                note=f"เช็คอินห้อง {room_number} ราคา {price_per_night}/คืน",
                category="รายรับ",
            )

            self.db_manager.update_room_status(room_number, "ไม่ว่าง")

            return {
                "success": True,
                "transaction_id": result.get("id"),
                "room": room_number,
                "total": price_per_night * nights,
                "message": f"เช็คอินห้อง {room_number} สำเร็จ! ยอด {price_per_night * nights:,} บาท",
            }

        except Exception as e:
            logger.error(f"Error during check-in: {e}")
            return {"success": False, "error": str(e)}

    async def check_out(
        self, room_number: str, extra_charge: int = 0, note: str = ""
    ) -> Dict[str, Any]:
        """เช็คเอาท์แขก"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            if extra_charge > 0:
                self.db_manager.add_transaction(
                    date=today,
                    item_name="ค่าบริการเพิ่มเติม",
                    room=room_number,
                    income=extra_charge,
                    note=note,
                    category="รายรับ",
                )

            self.db_manager.update_room_status(room_number, "ว่าง")

            return {
                "success": True,
                "room": room_number,
                "message": f"เช็คเอาท์ห้อง {room_number} สำเร็จ! ห้องว่างแล้ว",
            }

        except Exception as e:
            logger.error(f"Error during check-out: {e}")
            return {"success": False, "error": str(e)}

    async def get_current_guests(self) -> Dict[str, Any]:
        """ดูแขกที่พักอยู่ตอนนี้"""
        try:
            bookings = self.db_manager.get_current_bookings()

            return {"success": True, "guests": bookings, "count": len(bookings)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_available_rooms(self) -> Dict[str, Any]:
        """ดูห้องว่าง"""
        try:
            rooms = self.db_manager.get_available_rooms()

            return {"success": True, "rooms": rooms, "count": len(rooms)}
        except Exception as e:
            return {"success": False, "error": str(e)}
