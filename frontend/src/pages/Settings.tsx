import { useState } from 'react'
import { 
  ArrowLeft, Home, Settings, User, Bell, Shield,
  Key, Database, Wifi, MessageCircle, Moon, Sun,
  Globe, ChevronRight
} from 'lucide-react'

const neu = "bg-surface-light shadow-neu rounded-neu"
const neuInset = "bg-surface-light shadow-neu-inset rounded-neu"
const neuInsetSm = "bg-surface-light shadow-neu-inset-sm rounded-2xl"

export default function SettingsPage() {
  const [darkMode, setDarkMode] = useState(false)
  const [notifications, setNotifications] = useState(true)
  const [offlineMode, setOfflineMode] = useState(false)

  const settingsSections = [
    {
      title: 'บัญชี',
      items: [
        { icon: User, label: 'โปรไฟล์', desc: 'จัดการข้อมูลผู้ใช้' },
        { icon: Shield, label: 'ความปลอดภัย', desc: 'เปลี่ยนรหัสผ่าน' },
      ]
    },
    {
      title: 'ระบบ',
      items: [
        { icon: Bell, label: 'การแจ้งเตือน', desc: 'ตั้งค่าการแจ้งเตือน' },
        { icon: Database, label: 'ข้อมูล', desc: 'สำรองข้อมูล' },
        { icon: Wifi, label: 'การเชื่อมต่อ', desc: 'API และ Local LLM' },
      ]
    },
    {
      title: 'อื่นๆ',
      items: [
        { icon: Globe, label: 'ภาษา', desc: 'ภาษาไทย' },
        { icon: MessageCircle, label: 'Telegram', desc: 'เชื่อมต่อ Bot' },
      ]
    }
  ]

  return (
    <div className="min-h-screen bg-surface font-sans pb-24 max-w-[500px] mx-auto">
      {/* Header */}
      <nav className={`sticky top-0 z-50 ${neu} rounded-b-2xl`}>
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <button className="neu-btn-icon">
              <ArrowLeft size={18} />
            </button>
            <div>
              <h1 className="text-text font-bold text-base">ตั้งค่า</h1>
              <p className="text-text-muted text-xs">ปรับแต่งระบบ</p>
            </div>
          </div>
        </div>
      </nav>

      <div className="px-4 py-4 space-y-4">
        {/* Profile Card */}
        <div className={neu}>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center shadow-neu-sm">
              <User size={28} className="text-white" />
            </div>
            <div>
              <p className="text-base font-bold text-text">แอดมิน</p>
              <p className="text-sm text-text-muted">admin@hotel.local</p>
              <p className="text-xs text-primary mt-1">U'mi AI Assistant</p>
            </div>
          </div>
        </div>

        {/* Quick Toggles */}
        <div className="grid grid-cols-3 gap-3">
          <button 
            onClick={() => setDarkMode(!darkMode)}
            className={`${neuInsetSm} p-3 flex flex-col items-center gap-2`}
          >
            {darkMode ? (
              <Moon size={20} className="text-primary" />
            ) : (
              <Sun size={20} className="text-amber-500" />
            )}
            <span className="text-xs text-text-muted">{darkMode ? 'มืด' : 'สว่าง'}</span>
          </button>
          <button 
            onClick={() => setNotifications(!notifications)}
            className={`${neuInsetSm} p-3 flex flex-col items-center gap-2`}
          >
            <Bell size={20} className={notifications ? 'text-primary' : 'text-text-muted'} />
            <span className="text-xs text-text-muted">แจ้งเตือน</span>
          </button>
          <button 
            onClick={() => setOfflineMode(!offlineMode)}
            className={`${neuInsetSm} p-3 flex flex-col items-center gap-2`}
          >
            <Wifi size={20} className={offlineMode ? 'text-amber-500' : 'text-green-600'} />
            <span className="text-xs text-text-muted">{offlineMode ? 'ออฟไลน์' : 'ออนไลน์'}</span>
          </button>
        </div>

        {/* API Status */}
        <div className={neu}>
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm font-bold text-text">สถานะ API</p>
            <span className="text-xs text-green-600 font-medium">ออนไลน์</span>
          </div>
          <div className="space-y-2">
            <div className={`${neuInsetSm} p-3 flex items-center justify-between`}>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500" />
                <span className="text-sm text-text">Gemini API</span>
              </div>
              <span className="text-xs text-text-muted">พร้อมใช้งาน</span>
            </div>
            <div className={`${neuInsetSm} p-3 flex items-center justify-between`}>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-gray-400" />
                <span className="text-sm text-text">OpenAI</span>
              </div>
              <span className="text-xs text-text-muted">ยังไม่ได้ตั้งค่า</span>
            </div>
            <div className={`${neuInsetSm} p-3 flex items-center justify-between`}>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-gray-400" />
                <span className="text-sm text-text">Local Ollama</span>
              </div>
              <span className="text-xs text-text-muted">ยังไม่ได้ตั้งค่า</span>
            </div>
          </div>
        </div>

        {/* Settings Sections */}
        {settingsSections.map((section) => (
          <div key={section.title}>
            <p className="text-xs font-semibold text-text-muted mb-2 ml-1">{section.title}</p>
            <div className="space-y-2">
              {section.items.map((item) => (
                <button key={item.label} className={`${neu} w-full p-3 flex items-center gap-3`}>
                  <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                    <item.icon size={18} className="text-primary" />
                  </div>
                  <div className="flex-1 text-left">
                    <p className="text-sm font-medium text-text">{item.label}</p>
                    <p className="text-xs text-text-muted">{item.desc}</p>
                  </div>
                  <ChevronRight size={16} className="text-text-light" />
                </button>
              ))}
            </div>
          </div>
        ))}

        {/* Version Info */}
        <div className="text-center py-4">
          <p className="text-xs text-text-muted">U'mi Hotel System v3.0.0</p>
          <p className="text-[10px] text-text-light mt-1">Powered by Gemini AI</p>
        </div>
      </div>

      {/* Bottom Nav */}
      <nav className={`fixed bottom-0 left-0 right-0 z-50 ${neu} rounded-t-2xl max-w-[500px] mx-auto`}>
        <div className="flex items-center justify-around py-2 pb-3">
          <a href="/" className="flex flex-col items-center gap-0.5 px-3 py-1.5 text-text-muted">
            <Home size={20} />
            <span className="text-[9px] font-semibold">หน้าหลัก</span>
          </a>
          <a href="/slip" className="flex flex-col items-center gap-0.5 px-3 py-1.5 text-text-muted">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>
            <span className="text-[9px] font-semibold">สลิป</span>
          </a>
          <div className="w-12" />
          <a href="/reports" className="flex flex-col items-center gap-0.5 px-3 py-1.5 text-text-muted">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
            <span className="text-[9px] font-semibold">รายงาน</span>
          </a>
          <a href="/settings" className="flex flex-col items-center gap-0.5 px-3 py-1.5 text-primary">
            <Settings size={20} />
            <span className="text-[9px] font-semibold">ตั้งค่า</span>
          </a>
        </div>
      </nav>
    </div>
  )
}