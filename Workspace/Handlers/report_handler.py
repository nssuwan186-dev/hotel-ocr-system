# Handlers/report_handler.py
"""
Report Handler - สร้างรายงานต่างๆ
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ReportHandler:
    def __init__(self, model_manager, db_manager, prompt_loader):
        self.model_manager = model_manager
        self.db_manager = db_manager
        self.prompt_loader = prompt_loader

    async def generate_daily_report(self, date: str = None) -> Dict[str, Any]:
        """สร้างรายงานประจำวัน"""
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")

            summary = self.db_manager.get_daily_summary(date)
            bookings = self.db_manager.get_current_bookings()

            return {
                "success": True,
                "date": date,
                "summary": summary,
                "current_guests": bookings,
                "formatted": self._format_daily_report(summary, bookings),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def generate_weekly_report(self, days: int = 7) -> Dict[str, Any]:
        """สร้างรายงานรายสัปดาห์"""
        try:
            weekly_data = self.db_manager.get_weekly_summary(days)

            total_income = sum(d.get("income", 0) for d in weekly_data)
            total_expense = sum(d.get("expense", 0) for d in weekly_data)
            total_bookings = sum(d.get("bookings", 0) for d in weekly_data)

            return {
                "success": True,
                "period_days": days,
                "daily_data": weekly_data,
                "total_income": total_income,
                "total_expense": total_expense,
                "profit": total_income - total_expense,
                "total_bookings": total_bookings,
                "formatted": self._format_weekly_report(
                    weekly_data, total_income, total_expense, total_bookings
                ),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def generate_monthly_report(self, year_month: str = None) -> Dict[str, Any]:
        """สร้างรายงานรายเดือน"""
        try:
            if year_month is None:
                year_month = datetime.now().strftime("%Y-%m")

            summary = self.db_manager.get_monthly_summary(year_month)
            rooms = self.db_manager.get_all_rooms()
            customers = self.db_manager.search_customers("", limit=100)

            return {
                "success": True,
                "month": year_month,
                "summary": summary,
                "rooms": rooms,
                "total_rooms": len(rooms),
                "formatted": self._format_monthly_report(summary, rooms),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def generate_ai_analysis(self, date_range: str = "30 days") -> Dict[str, Any]:
        """สร้างรายงานวิเคราะห์ด้วย AI"""
        try:
            monthly = self.db_manager.get_monthly_summary()
            weekly = self.db_manager.get_weekly_summary(30)
            rooms = self.db_manager.get_all_rooms()

            prompt = f"""คุณเป็นนักวิเคราะห์ธุรกิจโรงแรม

ข้อมูลที่ได้รับ:
- รายเดือน: {monthly}
- รายสัปดาห์ 30 วัน: {weekly}
- ข้อมูลห้อง: {rooms}

ให้วิเคราะห์และแนะนำเป็นภาษาไทย"""

            response = await self.model_manager.generate(
                prompt=prompt, model_name="gemini-2.0-flash"
            )

            if response.get("error"):
                return {"success": False, "error": response.get("message")}

            return {
                "success": True,
                "analysis": response["text"],
                "model_used": response.get("model"),
            }

        except Exception as e:
            logger.error(f"Error generating AI analysis: {e}")
            return {"success": False, "error": str(e)}

    def _format_daily_report(self, summary: Dict, bookings: List) -> str:
        """จัดรูปแบบรายงานประจำวัน"""
        date = summary.get("date", "")
        th_date = self._to_thai_date(date)

        lines = [
            f"📊 รายงานประจำวัน {th_date}",
            "=" * 40,
            f"💰 รายรับ: {summary.get('income', 0):,} บาท",
            f"💸 รายจ่าย: {summary.get('expense', 0):,} บาท",
            f"📈 กำไร: {summary.get('profit', 0):,} บาท",
            f"🏠 จำนวนการจอง: {summary.get('bookings', 0)} ราย",
            f"💵 ยอดสะสม: {summary.get('balance', 0):,} บาท",
            "",
        ]

        if bookings:
            lines.append("👥 แขกที่พักอยู่:")
            for b in bookings:
                lines.append(
                    f"  - ห้อง {b.get('room_number')}: {b.get('customer_name')}"
                )

        return "\n".join(lines)

    def _format_weekly_report(
        self,
        daily_data: List,
        total_income: int,
        total_expense: int,
        total_bookings: int,
    ) -> str:
        """จัดรูปแบบรายงานรายสัปดาห์"""
        lines = [
            "📊 รายงานรายสัปดาห์",
            "=" * 40,
            f"💰 รายรับรวม: {total_income:,} บาท",
            f"💸 รายจ่ายรวม: {total_expense:,} บาท",
            f"📈 กำไรรวม: {total_income - total_expense:,} บาท",
            f"🏠 จำนวนการจอง: {total_bookings} ราย",
            f"📊 เฉลี่ยต่อวัน: {total_income // len(daily_data) if daily_data else 0:,} บาท",
            "",
        ]

        lines.append("📅 รายละเอียดรายวัน:")
        for day in daily_data[:7]:
            lines.append(f"  {day.get('date')}: รายรับ {day.get('income', 0):,}")

        return "\n".join(lines)

    def _format_monthly_report(self, summary: Dict, rooms: List) -> str:
        """จัดรูปแบบรายงานรายเดือน"""
        month = summary.get("month", "")
        th_month = self._to_thai_month(month)

        lines = [
            f"📊 รายงานรายเดือน {th_month}",
            "=" * 40,
            f"💰 รายรับ: {summary.get('income', 0):,} บาท",
            f"💸 รายจ่าย: {summary.get('expense', 0):,} บาท",
            f"📈 กำไร: {summary.get('profit', 0):,} บาท",
            f"🏠 จำนวนการจอง: {summary.get('bookings', 0)} ราย",
            f"🏢 จำนวนห้องที่ใช้: {summary.get('rooms_used', 0)} ห้อง",
            f"📊 เฉลี่ยต่อการจอง: {summary.get('income', 0) // max(summary.get('bookings', 1), 1):,} บาท",
            "",
        ]

        return "\n".join(lines)

    def _to_thai_date(self, date_str: str) -> str:
        """แปลงวันที่เป็นภาษาไทย"""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            year_th = dt.year + 543
            months_th = [
                "",
                "ม.ค.",
                "ก.พ.",
                "ม.ค.ค.",
                "เม.ย.",
                "พ.ค.",
                "ม.ย.",
                "ก.ค.",
                "ส.ค.",
                "ก.ย.",
                "ต.ค.",
                "พ.ย.",
                "ธ.ค.",
            ]
            return f"{dt.day} {months_th[dt.month]} {year_th}"
        except:
            return date_str

    def _to_thai_month(self, year_month: str) -> str:
        """แปลงเดือนเป็นภาษาไทย"""
        try:
            year, month = year_month.split("-")
            year_th = int(year) + 543
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
            return f"{months_th[int(month)]} {year_th}"
        except:
            return year_month

    async def export_to_file(
        self, report_type: str, data: Dict, output_dir: str = "Workspace/Reports"
    ) -> str:
        """ส่งออกรายงานเป็นไฟล์"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_type}_{timestamp}.txt"
            filepath = output_path / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(data.get("formatted", str(data)))

            return str(filepath)

        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            return ""
