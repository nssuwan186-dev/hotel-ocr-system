#!/usr/bin/env python3
"""
Scripts/health_check.py
ตรวจสอบสถานะระบบ
"""

import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


async def check_database():
    """ตรวจสอบฐานข้อมูล"""
    print("🗄️  Database Check...")

    db_path = "Workspace/Database/hotel_account.db"
    if not Path(db_path).exists():
        print(f"  ❌ Database not found: {db_path}")
        return False

    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = ["transactions", "rooms", "customers", "bookings", "employees"]
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  ✓ {table}: {count} records")

    conn.close()
    print("  ✅ Database OK\n")
    return True


async def check_models():
    """ตรวจสอบโมเดล"""
    print("🤖 Model Check...")

    from Workspace.Core.model_manager import ModelManager

    try:
        mm = ModelManager("Workspace/Config/models.yaml")

        if not mm.models:
            print("  ❌ No models loaded")
            return False

        print(f"  ✓ Models loaded: {len(mm.models)}")
        for name, model in mm.models.items():
            print(f"    - {name}: {model.provider.value}")

        # ตรวจสอบ API keys
        print("\n  📝 API Keys Status:")
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

        print(f"    GEMINI_API_KEY: {'✅ Set' if gemini_key else '❌ Not set'}")
        print(f"    OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")
        print(f"    ANTHROPIC_API_KEY: {'✅ Set' if anthropic_key else '❌ Not set'}")

        print("  ✅ Models OK\n")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}\n")
        return False


async def check_config():
    """ตรวจสอบ config files"""
    print("⚙️  Config Check...")

    config_files = [
        "Workspace/Config/models.yaml",
        "Workspace/Config/routing_rules.yaml",
        "Workspace/Config/prompts/vision_slip.txt",
        "Workspace/Config/system/soul_core.txt",
    ]

    all_ok = True
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"  ✓ {config_file}")
        else:
            print(f"  ❌ Missing: {config_file}")
            all_ok = False

    if all_ok:
        print("  ✅ Config OK\n")
    else:
        print("  ⚠️  Some config files missing\n")

    return all_ok


async def check_handlers():
    """ตรวจสอบ handlers"""
    print("⚡ Handler Check...")

    try:
        from Workspace.Handlers import (
            SlipHandler,
            QueryHandler,
            BookingHandler,
            ReportHandler,
        )

        print("  ✓ All handlers imported successfully")
        print("  ✅ Handlers OK\n")
        return True
    except Exception as e:
        print(f"  ❌ Error importing handlers: {e}\n")
        return False


async def run_health_check():
    """รัน health check ทั้งหมด"""
    print("\n" + "=" * 50)
    print("🏥 OpenClaw Health Check")
    print("=" * 50 + "\n")

    results = []

    results.append(await check_config())
    results.append(await check_database())
    results.append(await check_models())
    results.append(await check_handlers())

    print("=" * 50)
    if all(results):
        print("✅ System Status: HEALTHY")
    else:
        print("⚠️  System Status: ISSUES FOUND")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(run_health_check())
