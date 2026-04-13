#!/usr/bin/env python3
"""Quick test - ทดสอบส่งข้อความไป Gemini"""

import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, str(Path(__file__).parent.parent))

from Workspace.Core.model_manager import ModelManager


async def test_gemini():
    print("🤖 Testing Gemini API...")

    mm = ModelManager("Workspace/Config/models.yaml")

    response = await mm.generate(
        prompt="สวัสดีค่ะ ยูมิ คุณชื่ออะไร?", model_name="gemini-2.0-flash"
    )

    if response.get("error"):
        print(f"❌ Error: {response.get('message')}")
    else:
        print(f"✅ Success!")
        print(f"Model: {response.get('model')}")
        print(f"Response: {response.get('text')[:200]}...")


if __name__ == "__main__":
    asyncio.run(test_gemini())
