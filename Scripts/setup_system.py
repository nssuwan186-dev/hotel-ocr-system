#!/usr/bin/env python3
"""
Scripts/setup_system.py
ติดตั้งและตั้งค่าระบบครั้งแรก
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_directories():
    """สร้างโครงสร้างโฟลเดอร์ที่จำเป็น"""
    logger.info("📁 Creating directories...")

    directories = [
        "Workspace/Config/prompts",
        "Workspace/Config/system",
        "Workspace/Core",
        "Workspace/Handlers",
        "Workspace/Integrations",
        "Workspace/Database",
        "Workspace/Logs",
        "Workspace/Media/Slips",
        "Workspace/Media/Receipts",
        "Workspace/Reports/Monthly",
        "Workspace/Reports/Weekly",
        "Scripts",
        "Tests",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"  ✓ {directory}")

    logger.info("✅ Directories created!\n")


def create_database():
    """สร้างฐานข้อมูล SQLite"""
    logger.info("🗄️ Creating database...")

    db_path = "Workspace/Database/hotel_account.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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

    # เพิ่มข้อมูลห้องตัวอย่าง
    rooms_data = [
        ("A101", "A", 1, "Standard", 400, "ว่าง", ""),
        ("A102", "A", 1, "Standard", 400, "ว่าง", ""),
        ("A103", "A", 1, "Standard", 400, "ว่าง", ""),
        ("A104", "A", 1, "Standard", 400, "ว่าง", ""),
        ("A105", "A", 1, "Standard", 400, "ว่าง", ""),
        ("A106", "A", 1, "Standard", 400, "ว่าง", ""),
        ("A107", "A", 1, "Standard", 400, "ว่าง", ""),
        ("A108", "A", 1, "Standard", 400, "ว่าง", ""),
        ("A109", "A", 1, "Standard", 400, "ว่าง", ""),
        ("A110", "A", 1, "Standard", 400, "ว่าง", ""),
        ("A111", "A", 1, "Standard", 400, "ว่าง", ""),
        ("A201", "A", 2, "Standard", 500, "ปิดปรับปรุง", "ปิดปรับปรุง"),
        ("A202", "A", 2, "Standard", 500, "ว่าง", ""),
        ("A203", "A", 2, "Standard", 500, "ว่าง", ""),
        ("A204", "A", 2, "Monthly", 3500, "ไม่ว่าง", "ห้องรายเดือน"),
        ("A205", "A", 2, "Monthly", 3500, "ไม่ว่าง", "ห้องรายเดือน"),
        ("A206", "A", 2, "Monthly", 3500, "ไม่ว่าง", "ห้องรายเดือน"),
        ("A207", "A", 2, "Standard", 500, "ว่าง", ""),
        ("A208", "A", 2, "Monthly", 3500, "ไม่ว่าง", "ห้องรายเดือน"),
        ("A209", "A", 2, "Standard", 500, "ว่าง", ""),
        ("A210", "A", 2, "Standard", 500, "ว่าง", ""),
        ("A211", "A", 2, "Monthly", 3500, "ไม่ว่าง", "ห้องรายเดือน"),
        ("B101", "B", 1, "Standard", 400, "ว่าง", ""),
        ("B102", "B", 1, "Standard", 400, "ว่าง", ""),
        ("B103", "B", 1, "Standard", 400, "ว่าง", ""),
        ("B104", "B", 1, "Standard", 400, "ว่าง", ""),
        ("B105", "B", 1, "Standard", 400, "ว่าง", ""),
        ("B106", "B", 1, "Standard", 400, "ว่าง", ""),
        ("B107", "B", 1, "Standard", 400, "ว่าง", ""),
        ("B108", "B", 1, "Standard", 400, "ว่าง", ""),
        ("B109", "B", 1, "Standard", 400, "ว่าง", ""),
        ("B110", "B", 1, "Standard", 400, "ว่าง", ""),
        ("B111", "B", 1, "Standard", 400, "ว่าง", ""),
        ("B201", "B", 2, "Standard", 500, "ว่าง", ""),
        ("B202", "B", 2, "Standard", 500, "ว่าง", ""),
        ("B203", "B", 2, "Standard", 500, "ว่าง", ""),
        ("B204", "B", 2, "Standard", 500, "ว่าง", ""),
        ("B205", "B", 2, "Standard", 500, "ว่าง", ""),
        ("B206", "B", 2, "Standard", 500, "ว่าง", ""),
        ("B207", "B", 2, "Standard", 500, "ว่าง", ""),
        ("B208", "B", 2, "Standard", 500, "ว่าง", ""),
        ("B209", "B", 2, "Standard", 500, "ว่าง", ""),
        ("B210", "B", 2, "Standard", 500, "ว่าง", ""),
        ("B211", "B", 2, "Standard", 500, "ว่าง", ""),
        ("N01", "N", 1, "VIP", 600, "ว่าง", ""),
        ("N02", "N", 1, "VIP", 600, "ว่าง", ""),
        ("N03", "N", 1, "VIP", 600, "ว่าง", ""),
        ("N04", "N", 1, "VIP", 600, "ว่าง", ""),
        ("N05", "N", 1, "VIP", 600, "ว่าง", ""),
        ("N06", "N", 1, "VIP", 600, "ว่าง", ""),
        ("N07", "N", 1, "VIP", 600, "ว่าง", ""),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO rooms 
        (room_number, building, floor, room_type, price_per_night, status, note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        rooms_data,
    )

    conn.commit()
    conn.close()

    logger.info(f"✅ Database created at {db_path}\n")


def create_env_file():
    """สร้างไฟล์ .env.example"""
    logger.info("📝 Creating .env.example...")

    env_content = """# OpenClaw Hotel AI System - Environment Variables
# ================================================

# Google Gemini API (แนะนำใช้)
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI API (Optional)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude API (Optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Telegram Bot (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_WEBHOOK_URL=https://your-webhook-url.com/webhook

# Database Path
DATABASE_PATH=Workspace/Database/hotel_account.db

# System Settings
LOG_LEVEL=INFO
DEFAULT_MODEL=gemini-2.0-flash
"""

    with open(".env.example", "w", encoding="utf-8") as f:
        f.write(env_content)

    logger.info("✅ .env.example created!\n")


def create_memory_md():
    """สร้างไฟล์ memory.md"""
    logger.info("📓 Creating memory.md...")

    content = f"""# OpenClaw Memory - ความทรงจำระยะยาว

## ข้อมูลระบบ
- สร้างเมื่อ: {datetime.now().strftime("%Y-%m-%d %H:%M")}
- เวอร์ชัน: 3.0.0

## เหตุการณ์สำคัญ

## ข้อมูลลูกค้าประจำ

## บันทึกการบำรุงรักษา
"""

    with open("Workspace/memory.md", "w", encoding="utf-8") as f:
        f.write(content)

    logger.info("✅ memory.md created!\n")


def create_requirements_txt():
    """สร้าง requirements.txt"""
    logger.info("📦 Creating requirements.txt...")

    requirements = """aiohttp>=3.9.0
pyyaml>=6.0
python-dotenv>=1.0.0
"""

    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements)

    logger.info("✅ requirements.txt created!\n")


def create_readme():
    """สร้าง README.md"""
    logger.info("📖 Creating README.md...")

    readme = """# 🏨 OpenClaw Hotel AI System

Multi-Model AI Agent สำหรับระบบบัญชีหอพัก

## 🚀 Quick Start

1. ติดตั้ง dependencies:
```bash
pip install -r requirements.txt
```

2. ตั้งค่า API Keys:
```bash
copy .env.example .env
# แก้ไข .env ใส่ API keys ของคุณ
```

3. รันระบบ:
```bash
python Scripts/gateway.py interactive
```

## 📁 โครงสร้างระบบ

- `Workspace/Core/` - โมดูลหลัก
- `Workspace/Handlers/` - ตัวจัดการแต่ละงาน
- `Workspace/Config/` - การตั้งค่า
- `Scripts/` - Scripts หลัก

## 🔧 Commands

- `/balance` - ดูยอดสะสม
- `/rooms` - ดูห้องว่าง
- `/report` - สร้างรายงาน
- `/slip` - วิเคราะห์สลิป
"""

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    logger.info("✅ README.md created!\n")


def print_summary():
    """แสดงสรุปการติดตั้ง"""
    print("\n" + "=" * 50)
    print("🎉 การติดตั้งเสร็จสมบูรณ์!")
    print("=" * 50)
    print("""
ขั้นตอนถัดไป:
1. แก้ไขไฟล์ .env ใส่ API Keys
   - GEMINI_API_KEY (จำเป็น)
   - OPENAI_API_KEY (optional)
   - ANTHROPIC_API_KEY (optional)

2. รันระบบ:
   python Scripts/gateway.py test   # ทดสอบระบบ
   python Scripts/gateway.py interactive   # ใช้งานจริง

3. เชื่อมต่อ Telegram (optional):
   - สร้าง Bot ผ่าน @BotFather
   - ใส่ Token ใน .env
   - รัน: python Scripts/gateway.py telegram
""")
    print("=" * 50 + "\n")


def main():
    """Main function"""
    print("\n" + "=" * 50)
    print("🏨 OpenClaw Hotel AI System - Setup")
    print("=" * 50 + "\n")

    create_directories()
    create_database()
    create_env_file()
    create_memory_md()
    create_requirements_txt()
    create_readme()

    print_summary()


if __name__ == "__main__":
    main()
