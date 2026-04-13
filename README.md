# 🏨 OpenClaw Hotel AI System

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
