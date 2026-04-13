import { useState, useRef } from 'react'
import { 
  Upload, Camera, Image, CheckCircle, Clock, ArrowLeft, 
  Trash2, RotateCcw, DollarSign, MoreHorizontal, Search
} from 'lucide-react'

const neu = "bg-[#f0f4f8] shadow-[4px_4px_10px_#d1d9e6,-4px_-4px_10px_#ffffff]"
const neuInset = "bg-[#f0f4f8] shadow-[inset_3px_3px_6px_#d1d9e6,inset_-3px_-3px_6px_#ffffff]"

const mockSlips = [
  { id: 1, amount: 1200, from: 'สมชาย ใจดี', date: '2026-04-13', time: '14:35', bank: 'KBank', verified: true },
  { id: 2, amount: 3500, from: 'มานี มีเงิน', date: '2026-04-13', time: '13:20', bank: 'SCB', verified: true },
  { id: 3, amount: 2400, from: 'วิชัย รวย', date: '2026-04-13', time: '11:45', bank: 'BBL', verified: false },
  { id: 4, amount: 800, from: 'ลิลลี่ สวย', date: '2026-04-12', time: '16:20', bank: 'KTB', verified: true },
  { id: 5, amount: 1500, from: 'จิระ ทำนอง', date: '2026-04-12', time: '09:15', bank: 'KBank', verified: false },
]

function StatusBadge({ verified }: { verified: boolean }) {
  if (verified) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#006D36]/10 text-[#006D36]">
        <CheckCircle size={12} />
        <span className="text-[11px]">ยืนยันแล้ว</span>
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-50 text-amber-600">
      <Clock size={12} />
      <span className="text-[11px]">รอตรวจ</span>
    </span>
  )
}

export default function SlipAnalysis() {
  const [slips] = useState(mockSlips)
  const [uploadMode, setUploadMode] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const verifiedCount = slips.filter(s => s.verified).length
  const pendingCount = slips.filter(s => !s.verified).length
  const totalAmount = slips.reduce((sum, s) => sum + s.amount, 0)

  return (
    <div className="min-h-screen bg-[#e8eef5] font-['Manrope',sans-serif] pb-20 max-w-[500px] mx-auto">
      {/* Header */}
      <nav className={`sticky top-0 z-50 ${neu} rounded-b-2xl`}>
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <a href="/" className={`p-2 rounded-xl ${neu} active:scale-95 transition-transform`}>
              <ArrowLeft size={18} />
            </a>
            <div>
              <h1 className="text-[#29343a] text-base font-bold">วิเคราะห์สลิป</h1>
              <p className="text-[#566168] text-xs">ตรวจสอบสลิปโอนเงิน</p>
            </div>
          </div>
          <button 
            onClick={() => setUploadMode(true)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#006D36] text-white text-sm font-semibold active:scale-95 transition-transform"
          >
            <Upload size={14} />
            <span>อัปโหลด</span>
          </button>
        </div>
      </nav>

      <div className="px-4 py-4 space-y-4">
        {/* Stats Row */}
        <div className="grid grid-cols-3 gap-3">
          <div className={`${neuInset} p-3 text-center rounded-xl`}>
            <p className="text-xl font-bold text-[#006D36]">{slips.length}</p>
            <p className="text-xs text-[#566168]">ทั้งหมด</p>
          </div>
          <div className={`${neuInset} p-3 text-center rounded-xl`}>
            <p className="text-xl font-bold text-green-600">{verifiedCount}</p>
            <p className="text-xs text-[#566168]">ยืนยันแล้ว</p>
          </div>
          <div className={`${neuInset} p-3 text-center rounded-xl`}>
            <p className="text-xl font-bold text-amber-600">{pendingCount}</p>
            <p className="text-xs text-[#566168]">รอตรวจ</p>
          </div>
        </div>

        {/* Total Amount */}
        <div className={`${neu} rounded-2xl p-4`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-[#006D36]/10 flex items-center justify-center">
                <DollarSign size={20} className="text-[#006D36]" />
              </div>
              <div>
                <p className="text-xs text-[#566168]">ยอดรวมวันนี้</p>
                <p className="text-lg font-bold text-[#29343a]">฿{totalAmount.toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Upload Mode */}
        {uploadMode && (
          <div className={`${neu} rounded-2xl p-4`}>
            <div className="text-center py-6">
              <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-[#006D36]/10 flex items-center justify-center">
                <Camera size={32} className="text-[#006D36]" />
              </div>
              <p className="text-sm font-medium text-[#29343a] mb-2">อัปโหลดสลิปโอนเงิน</p>
              <p className="text-xs text-[#566168] mb-4">ถ่ายรูปหรือเลือกไฟล์ภาพ</p>
              <div className="flex gap-3 justify-center">
                <button className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#006D36] text-white text-sm font-semibold">
                  <Camera size={14} />
                  ถ่ายรูป
                </button>
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  className={`flex items-center gap-1.5 px-4 py-2 rounded-xl ${neu} text-sm font-medium text-[#566168]`}
                >
                  <Image size={14} />
                  เลือกไฟล์
                </button>
                <input ref={fileInputRef} type="file" accept="image/*" className="hidden" />
              </div>
            </div>
            <button 
              onClick={() => setUploadMode(false)}
              className="w-full mt-3 py-2 text-sm text-[#566168]"
            >
              ยกเลิก
            </button>
          </div>
        )}

        {/* Slip List */}
        <div className={`${neu} rounded-2xl p-4`}>
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm font-bold text-[#29343a]">รายการสลิป</p>
            <button className={`p-1.5 rounded-lg ${neu}`}>
              <MoreHorizontal size={14} className="text-[#566168]" />
            </button>
          </div>
          <div className="space-y-3">
            {slips.map((slip) => (
              <div key={slip.id} className={`${neuInset} rounded-xl p-3 cursor-pointer active:scale-[0.98] transition-transform`}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-[#006D36]/10 flex items-center justify-center">
                      <Image size={14} className="text-[#006D36]" />
                    </div>
                    <div>
                      <p className="text-xs text-[#566168]">#{slip.id}</p>
                      <p className="text-xs text-[#566168]">{slip.date} {slip.time}</p>
                    </div>
                  </div>
                  <StatusBadge verified={slip.verified} />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-[#29343a]">{slip.from}</p>
                    <p className="text-[10px] text-[#566168]">ธนาคาร {slip.bank}</p>
                  </div>
                  <p className="text-lg font-bold text-[#006D36]">฿{slip.amount.toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-3">
          <button className={`${neu} p-3 flex items-center gap-3`}>
            <div className="w-10 h-10 rounded-xl bg-[#006D36]/10 flex items-center justify-center">
              <RotateCcw size={18} className="text-[#006D36]" />
            </div>
            <div className="text-left">
              <p className="text-sm font-medium text-[#29343a]">ยืนยันทั้งหมด</p>
              <p className="text-xs text-[#566168]">อนุมัติรายการ</p>
            </div>
          </button>
          <button className={`${neu} p-3 flex items-center gap-3`}>
            <div className="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center">
              <Trash2 size={18} className="text-red-500" />
            </div>
            <div className="text-left">
              <p className="text-sm font-medium text-[#29343a]">ลบรายการ</p>
              <p className="text-xs text-[#566168]">ล้างข้อมูล</p>
            </div>
          </button>
        </div>
      </div>

      {/* Bottom Navigation */}
      <nav className={`fixed bottom-0 left-0 right-0 z-50 ${neu} rounded-t-2xl max-w-[500px] mx-auto`}>
        <div className="flex items-center justify-around py-2 pb-3">
          {[
            { icon: Search, label: "หน้าหลัก", path: "/" },
            { icon: Image, label: "สลิป", path: "/slip" },
            { icon: Image, label: "ห้อง", path: "/rooms" },
            { icon: Search, label: "รายงาน", path: "/reports" },
            { icon: Search, label: "ตั้งค่า", path: "/settings" },
          ].map((tab, i) => (
            <a
              key={i}
              href={tab.path}
              className="flex flex-col items-center gap-0.5 px-3 py-1.5 text-[#566168]"
            >
              <tab.icon size={18} />
              <span className="text-[9px] font-semibold">{tab.label}</span>
            </a>
          ))}
        </div>
      </nav>
    </div>
  )
}