# Core/database.py
"""
จัดการฐานข้อมูล SQLite สำหรับระบบหอพัก
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager
from pathlib import Path
import threading


class DatabaseManager:
    def __init__(self, db_path: str = "Workspace/Database/hotel_account.db"):
        self.db_path = db_path
        self.local = threading.local()
        self._init_connection()

    def _init_connection(self):
        """สร้าง connection สำหรับ thread"""
        if not hasattr(self.local, "conn") or self.local.conn is None:
            self.local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.local.conn.row_factory = sqlite3.Row

    @contextmanager
    def get_cursor(self):
        """Context manager สำหรับ cursor"""
        self._init_connection()
        cursor = self.local.conn.cursor()
        try:
            yield cursor
            self.local.conn.commit()
        except Exception as e:
            self.local.conn.rollback()
            raise e

    def init_database(self):
        """สร้างตารางทั้งหมดถ้ายังไม่มี"""
        with self.get_cursor() as cursor:
            # transactions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    item_name TEXT,
                    phone TEXT,
                    room TEXT,
                    nights INTEGER DEFAULT 0,
                    expense INTEGER DEFAULT 0,
                    income INTEGER DEFAULT 0,
                    balance INTEGER DEFAULT 0,
                    deposit_cash INTEGER DEFAULT 0,
                    note TEXT,
                    category TEXT DEFAULT 'รายรับ',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # rooms
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    room_number TEXT PRIMARY KEY,
                    building TEXT,
                    floor INTEGER,
                    room_type TEXT,
                    price_per_night INTEGER,
                    status TEXT DEFAULT 'ว่าง',
                    note TEXT
                )
            """)

            # customers
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    customer_name TEXT,
                    phone TEXT,
                    nationality TEXT DEFAULT 'ไทย',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # bookings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_number TEXT,
                    customer_name TEXT,
                    check_in_date TEXT,
                    nights INTEGER,
                    channel TEXT DEFAULT 'เงินสด',
                    deposit INTEGER DEFAULT 0,
                    note TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # employees
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id TEXT PRIMARY KEY,
                    full_name TEXT,
                    position TEXT,
                    pay_type TEXT,
                    salary INTEGER,
                    active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # settings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

    # ========== Transactions ==========

    def get_latest_balance(self) -> int:
        """ดึงยอดสะสมล่าสุด"""
        with self.get_cursor() as cursor:
            cursor.execute("SELECT balance FROM transactions ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            return result[0] if result else 0

    def add_transaction(
        self,
        date: str,
        item_name: str,
        phone: str = "",
        room: str = "",
        nights: int = 0,
        expense: int = 0,
        income: int = 0,
        deposit_cash: int = 0,
        note: str = "",
        category: str = "รายรับ",
    ) -> Dict:
        """เพิ่มรายการธุรกรรมใหม่"""
        latest_balance = self.get_latest_balance()
        new_balance = latest_balance + income - expense

        with self.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO transactions 
                (date, item_name, phone, room, nights, expense, income, 
                 balance, deposit_cash, note, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    date,
                    item_name,
                    phone,
                    room,
                    nights,
                    expense,
                    income,
                    new_balance,
                    deposit_cash,
                    note,
                    category,
                ),
            )

            transaction_id = cursor.lastrowid

        return {
            "id": transaction_id,
            "balance": new_balance,
            "previous_balance": latest_balance,
        }

    def get_daily_summary(self, date: Optional[str] = None) -> Dict:
        """สรุปยอดประจำวัน"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        with self.get_cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    COALESCE(SUM(income), 0) as total_income,
                    COALESCE(SUM(expense), 0) as total_expense,
                    COUNT(CASE WHEN income > 0 THEN 1 END) as booking_count,
                    MAX(balance) as end_balance
                FROM transactions 
                WHERE date = ?
            """,
                (date,),
            )

            result = cursor.fetchone()

            return {
                "date": date,
                "income": result[0],
                "expense": result[1],
                "profit": result[0] - result[1],
                "bookings": result[2],
                "balance": result[3],
            }

    def get_weekly_summary(self, days: int = 7) -> List[Dict]:
        """สรุปยอดรายสัปดาห์"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    date,
                    SUM(income) as income,
                    SUM(expense) as expense,
                    COUNT(CASE WHEN income > 0 THEN 1 END) as bookings
                FROM transactions 
                WHERE date >= date('now', f'-{days} days')
                GROUP BY date
                ORDER BY date DESC
            """)

            return [dict(row) for row in cursor.fetchall()]

    def get_monthly_summary(self, year_month: Optional[str] = None) -> Dict:
        """สรุปยอดรายเดือน"""
        if year_month is None:
            year_month = datetime.now().strftime("%Y-%m")

        with self.get_cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    SUM(income) as total_income,
                    SUM(expense) as total_expense,
                    COUNT(CASE WHEN income > 0 AND room != '' THEN 1 END) as total_bookings,
                    COUNT(DISTINCT room) as unique_rooms
                FROM transactions 
                WHERE strftime('%Y-%m', date) = ?
            """,
                (year_month,),
            )

            result = cursor.fetchone()

            return {
                "month": year_month,
                "income": result[0] or 0,
                "expense": result[1] or 0,
                "profit": (result[0] or 0) - (result[1] or 0),
                "bookings": result[2] or 0,
                "rooms_used": result[3] or 0,
            }

    # ========== Rooms ==========

    def get_available_rooms(self) -> List[Dict]:
        """ดึงรายการห้องว่างทั้งหมด"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT room_number, building, floor, room_type, 
                       price_per_night, note
                FROM rooms 
                WHERE status = 'ว่าง'
                ORDER BY building, room_number
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_all_rooms(self) -> List[Dict]:
        """ดึงสถานะห้องทั้งหมด"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT room_number, building, floor, room_type,
                       price_per_night, status, note
                FROM rooms 
                ORDER BY building, room_number
            """)
            return [dict(row) for row in cursor.fetchall()]

    def update_room_status(self, room_number: str, status: str):
        """อัปเดตสถานะห้อง"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "UPDATE rooms SET status = ? WHERE room_number = ?",
                (status, room_number),
            )

    def add_room(
        self,
        room_number: str,
        building: str,
        floor: int,
        room_type: str,
        price_per_night: int,
        status: str = "ว่าง",
        note: str = "",
    ):
        """เพิ่มห้องใหม่"""
        with self.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT OR REPLACE INTO rooms 
                (room_number, building, floor, room_type, price_per_night, status, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    room_number,
                    building,
                    floor,
                    room_type,
                    price_per_night,
                    status,
                    note,
                ),
            )

    # ========== Customers ==========

    def search_customers(self, query: str, limit: int = 10) -> List[Dict]:
        """ค้นหาลูกค้าจากชื่อหรือเบอร์"""
        with self.get_cursor() as cursor:
            cursor.execute(
                """
                SELECT customer_id, customer_name, phone, nationality
                FROM customers
                WHERE customer_name LIKE ? OR phone LIKE ?
                ORDER BY customer_name
                LIMIT ?
            """,
                (f"%{query}%", f"%{query}%", limit),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_customer_history(self, customer_name: str) -> List[Dict]:
        """ดึงประวัติการพักของลูกค้า"""
        with self.get_cursor() as cursor:
            cursor.execute(
                """
                SELECT date, room, nights, income, note
                FROM transactions
                WHERE item_name = ? AND income > 0
                ORDER BY date DESC
                LIMIT 10
            """,
                (customer_name,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def add_customer(
        self, customer_name: str, phone: str = "", nationality: str = "ไทย"
    ) -> str:
        """เพิ่มลูกค้าใหม่"""
        with self.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM customers")
            count = cursor.fetchone()[0] + 1
            customer_id = f"CM-{count:05d}"

            cursor.execute(
                """
                INSERT OR IGNORE INTO customers 
                (customer_id, customer_name, phone, nationality)
                VALUES (?, ?, ?, ?)
            """,
                (customer_id, customer_name, phone, nationality),
            )

            return customer_id

    # ========== Bookings ==========

    def get_current_bookings(self) -> List[Dict]:
        """ดูใครพักอยู่ตอนนี้"""
        today = datetime.now().strftime("%Y-%m-%d")

        with self.get_cursor() as cursor:
            cursor.execute(
                """
                SELECT b.room_number, b.customer_name, b.check_in_date, 
                       b.nights, date(b.check_in_date, '+' || b.nights || ' days') as check_out_date,
                       b.channel, b.deposit
                FROM bookings b
                WHERE b.check_in_date <= ?
                  AND date(b.check_in_date, '+' || b.nights || ' days') > ?
                ORDER BY b.room_number
            """,
                (today, today),
            )
            return [dict(row) for row in cursor.fetchall()]

    def add_booking(
        self,
        room_number: str,
        customer_name: str,
        check_in_date: str,
        nights: int,
        channel: str = "เงินสด",
        deposit: int = 0,
        note: str = "",
    ) -> int:
        """เพิ่มการจองใหม่"""
        with self.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO bookings 
                (room_number, customer_name, check_in_date, nights, 
                 channel, deposit, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    room_number,
                    customer_name,
                    check_in_date,
                    nights,
                    channel,
                    deposit,
                    note,
                ),
            )

            return cursor.lastrowid

    # ========== Raw Query ==========

    def execute_query(self, sql: str, params: Tuple = ()) -> List[Dict]:
        """รัน SQL query (SELECT เท่านั้น)"""
        sql_lower = sql.strip().lower()

        if not sql_lower.startswith("select"):
            raise ValueError("Only SELECT queries allowed")

        if any(word in sql_lower for word in ["drop", "delete", "truncate", "alter"]):
            raise ValueError("Dangerous SQL keywords not allowed")

        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """ปิด connection"""
        if hasattr(self.local, "conn") and self.local.conn:
            self.local.conn.close()
