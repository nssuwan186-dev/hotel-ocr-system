import { useState } from "react"
import { Link } from "react-router-dom"
import {
  Search, Plus, Bell, Shield, Server, Database, Globe,
  Users, FileText, Calendar, Activity, TrendingUp, ArrowUpRight, ArrowDownRight,
  MoreHorizontal, CheckCircle, Clock, AlertTriangle, Home, ScanLine, BarChart3, Menu, X,
  CreditCard, Settings as SettingsIcon
} from "lucide-react"
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  AreaChart, Area, PieChart, Pie, Cell
} from "recharts"

const barData = [
  { name: "ม.ค.", revenue: 45, expenses: 28 },
  { name: "ก.พ.", revenue: 52, expenses: 31 },
  { name: "มี.ค.", revenue: 48, expenses: 25 },
  { name: "เม.ย.", revenue: 61, expenses: 34 },
  { name: "พ.ค.", revenue: 55, expenses: 29 },
  { name: "มิ.ย.", revenue: 67, expenses: 38 },
  { name: "ก.ค.", revenue: 72, expenses: 35 },
]

const areaData = [
  { name: "จ.", guests: 24 },
  { name: "อ.", guests: 31 },
  { name: "พ.", guests: 28 },
  { name: "พฤ.", guests: 42 },
  { name: "ศ.", guests: 56 },
  { name: "ส.", guests: 68 },
  { name: "อา.", guests: 52 },
]

const pieData = [
  { name: "เสร็จสิ้น", value: 68, color: "#006D36" },
  { name: "กำลังดำเนินการ", value: 22, color: "#4ade80" },
  { name: "รอดำเนินการ", value: 10, color: "#d1d9e6" },
]

const tableData = [
  { id: "TRX-001", client: "สมชาย ใจดี", room: "B101", amount: "1,200", status: "completed", date: "13 เม.ย. 69" },
  { id: "TRX-002", client: "มานี มีเงิน", room: "A205", amount: "3,500", date: "13 เม.ย. 69", status: "completed" },
  { id: "TRX-003", client: "วิชัย รวย", room: "N03", amount: "2,400", date: "13 เม.ย. 69", status: "pending" },
  { id: "TRX-004", client: "ลิลลี่ สวย", room: "B105", amount: "800", date: "12 เม.ย. 69", status: "completed" },
  { id: "TRX-005", client: "จิระ ทำนอง", room: "A102", amount: "1,500", date: "12 เม.ย. 69", status: "in-progress" },
]

const neu = "bg-[#f0f4f8] shadow-[4px_4px_10px_#d1d9e6,-4px_-4px_10px_#ffffff]"
const neuInset = "bg-[#f0f4f8] shadow-[inset_3px_3px_6px_#d1d9e6,inset_-3px_-3px_6px_#ffffff]"

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { icon: typeof CheckCircle; color: string; bg: string; label: string }> = {
    completed: { icon: CheckCircle, color: "text-[#006D36]", bg: "bg-[#006D36]/10", label: "เสร็จสิ้น" },
    pending: { icon: Clock, color: "text-amber-600", bg: "bg-amber-50", label: "รอดำเนินการ" },
    "in-progress": { icon: AlertTriangle, color: "text-blue-600", bg: "bg-blue-50", label: "กำลังดำเนินการ" },
  }
  const { icon: Icon, color, bg, label } = map[status] || map.pending
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full ${bg} ${color}`}>
      <Icon size={12} />
      <span className="text-[11px]">{label}</span>
    </span>
  )
}

export default function Dashboard() {
  const [searchOpen, setSearchOpen] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [activeTab, setActiveTab] = useState("home")

  return (
    <div className="min-h-screen bg-[#e8eef5] font-['Manrope',sans-serif] pb-20 max-w-[500px] mx-auto relative">
      {/* Sticky Top Nav */}
      <nav className={`sticky top-0 z-50 ${neu} rounded-b-2xl`}>
        <div className="flex items-center justify-between px-4 py-2.5">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[#006D36] flex items-center justify-center">
              <Shield size={15} className="text-white" />
            </div>
            <span className="text-[#29343a] text-[15px] font-[700] tracking-tight">U'mi HOTEL</span>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => setSearchOpen(!searchOpen)} className={`p-2 rounded-xl ${neu} active:scale-95 transition-transform`}>
              <Search size={16} className="text-[#566168]" />
            </button>
            <button className={`p-2 rounded-xl ${neu} relative active:scale-95 transition-transform`}>
              <Bell size={16} className="text-[#566168]" />
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-[9px] text-white flex items-center justify-center">3</span>
            </button>
            <button onClick={() => setMenuOpen(!menuOpen)} className={`p-2 rounded-xl ${neu} active:scale-95 transition-transform`}>
              {menuOpen ? <X size={16} className="text-[#566168]" /> : <Menu size={16} className="text-[#566168]" />}
            </button>
          </div>
        </div>
        {searchOpen && (
          <div className="px-4 pb-2.5">
            <div className={`flex items-center gap-2 px-3 py-2.5 rounded-xl ${neuInset}`}>
              <Search size={15} className="text-[#a0aab4]" />
              <input autoFocus className="bg-transparent outline-none flex-1 text-[13px] text-[#29343a] placeholder-[#a0aab4]" placeholder="ค้นหาลูกค้า, สลิป, รายการ..." />
            </div>
          </div>
        )}
        {menuOpen && (
          <div className="px-4 pb-3 space-y-1">
            <button className="w-full text-left px-3 py-2.5 text-[14px] text-[#566168] active:text-[#006D36] rounded-lg">โปรไฟล์</button>
            <button className="w-full text-left px-3 py-2.5 text-[14px] text-[#566168] active:text-[#006D36] rounded-lg">ตั้งค่า</button>
            <hr className="border-[#d1d9e6]" />
            <Link to="/rooms" className="block w-full text-left px-3 py-2.5 text-[14px] text-[#006D36] font-[600] rounded-lg">จัดการห้องพัก</Link>
            <Link to="/reports" className="block w-full text-left px-3 py-2.5 text-[14px] text-[#006D36] font-[600] rounded-lg">รายงาน</Link>
          </div>
        )}
      </nav>

      <div className="px-4 py-4 space-y-4">
        {/* Hero Greeting */}
        <div className={`${neu} rounded-2xl p-4`}>
          <div className="flex items-center justify-between mb-3">
            <div>
              <h1 className="text-[#29343a] text-[20px] font-[700] tracking-tight">สวัสดี, แอดมิน 💚</h1>
              <p className="text-[#566168] text-[12px] mt-0.5">สรุปภาพรวมวันนี้ของที่พักของคุณ</p>
            </div>
            <button className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#006D36] text-white text-[12px] font-[600] active:scale-95 transition-transform">
              <Plus size={14} />
              รายการใหม่
            </button>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 gap-2.5">
            {[
              { label: "ยอดสะสม", value: "฿128,500", icon: TrendingUp, trend: "+12%", up: true },
              { label: "รายรับวันนี้", value: "฿18,400", icon: Activity, trend: "+8%", up: true },
              { label: "ห้องว่าง", value: "23/51", icon: Home, trend: "5 จอง", up: true },
              { label: "สลิปรอตรวจ", value: "3", icon: CreditCard, trend: "-2", up: false },
            ].map((s) => (
              <div key={s.label} className={`${neuInset} rounded-xl p-3`}>
                <div className="flex items-center justify-between mb-1.5">
                  <s.icon size={16} className="text-[#006D36]" />
                  <span className={`text-[10px] flex items-center gap-0.5 font-[600] ${s.up ? "text-[#006D36]" : "text-red-500"}`}>
                    {s.up ? <ArrowUpRight size={10} /> : <ArrowDownRight size={10} />}
                    {s.trend}
                  </span>
                </div>
                <p className="text-[18px] font-[700] text-[#29343a] leading-tight">{s.value}</p>
                <p className="text-[10px] text-[#566168] mt-0.5">{s.label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Revenue Chart */}
        <div className={`${neu} rounded-2xl p-4`}>
          <div className="flex items-center justify-between mb-3">
            <p className="text-[13px] font-[600] text-[#29343a]">รายรับ vs รายจ่าย (พัน ฿)</p>
            <span className="text-[10px] text-[#566168]">เม.ย. 2569</span>
          </div>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={barData} barGap={2} barSize={12}>
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#566168" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: "#566168" }} axisLine={false} tickLine={false} width={28} />
              <Tooltip contentStyle={{ fontSize: 11, borderRadius: 8 }} />
              <Bar dataKey="revenue" fill="#006D36" radius={[4, 4, 0, 0]} name="รายรับ" />
              <Bar dataKey="expenses" fill="#d1d9e6" radius={[4, 4, 0, 0]} name="รายจ่าย" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie + Area Row */}
        <div className="grid grid-cols-2 gap-3">
          <div className={`${neu} rounded-2xl p-3`}>
            <p className="text-[12px] font-[600] text-[#29343a] mb-1">สถานะห้อง</p>
            <div className="flex justify-center">
              <PieChart width={110} height={110}>
                <Pie data={pieData} cx={55} cy={55} innerRadius={34} outerRadius={50} dataKey="value" strokeWidth={0}>
                  {pieData.map((d, i) => <Cell key={`cell-${i}`} fill={d.color} />)}
                </Pie>
              </PieChart>
            </div>
            <div className="space-y-0.5 mt-1">
              {pieData.map((d) => (
                <div key={d.name} className="flex items-center gap-1.5 text-[10px] text-[#566168]">
                  <span className="w-2 h-2 rounded-full shrink-0" style={{ background: d.color }} />
                  {d.name}
                </div>
              ))}
            </div>
          </div>

          <div className={`${neu} rounded-2xl p-3`}>
            <p className="text-[12px] font-[600] text-[#29343a] mb-1">เช็คอินแขก</p>
            <ResponsiveContainer width="100%" height={110}>
              <AreaChart data={areaData}>
                <defs>
                  <linearGradient id="guestGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#006D36" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#006D36" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" tick={{ fontSize: 9, fill: "#566168" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ fontSize: 10, borderRadius: 8 }} />
                <Area type="monotone" dataKey="guests" stroke="#006D36" fill="url(#guestGrad)" strokeWidth={2} name="แขก" />
              </AreaChart>
            </ResponsiveContainer>

            {/* System status mini */}
            <div className="mt-2 space-y-1.5">
              {[
                { name: "API", icon: Globe, ok: true },
                { name: "Database", icon: Database, ok: true },
              ].map((s) => (
                <div key={s.name} className="flex items-center gap-1.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#006D36]" />
                  <span className="text-[10px] text-[#566168]">{s.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: "รายรับรวม", value: "฿1.25ล.", icon: TrendingUp, change: "+12.5%", up: true },
            { label: "ห้องว่าง", value: "23", icon: Home, change: "+5", up: true },
            { label: "แขกวันนี้", value: "18", icon: Users, change: "+3", up: true },
            { label: "สลิปรอ", value: "3", icon: CreditCard, change: "-2", up: false },
          ].map((c) => (
            <div key={c.label} className={`${neu} rounded-2xl p-3.5`}>
              <div className="flex items-center justify-between mb-2">
                <div className="w-8 h-8 rounded-lg bg-[#e1e9f0] flex items-center justify-center shadow-[inset_2px_2px_4px_#d1d9e6,inset_-2px_-2px_4px_#ffffff]">
                  <c.icon size={15} className="text-[#006D36]" />
                </div>
                <span className={`text-[10px] flex items-center gap-0.5 font-[600] ${c.up ? "text-[#006D36]" : "text-red-500"}`}>
                  {c.up ? <ArrowUpRight size={10} /> : <ArrowDownRight size={10} />}
                  {c.change}
                </span>
              </div>
              <p className="text-[17px] font-[700] text-[#29343a] leading-tight">{c.value}</p>
              <p className="text-[10px] text-[#566168] mt-0.5">{c.label}</p>
            </div>
          ))}
        </div>

        {/* Table as Card List */}
        <div className={`${neu} rounded-2xl p-4`}>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-[14px] font-[700] text-[#29343a]">รายการล่าสุด</h2>
            <button className={`p-1.5 rounded-lg ${neu}`}><MoreHorizontal size={14} className="text-[#566168]" /></button>
          </div>
          <div className="space-y-2.5">
            {tableData.map((row) => (
              <div key={row.id} className={`${neuInset} rounded-xl p-3`}>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[11px] text-[#006D36] font-[600]">{row.id}</span>
                  <StatusBadge status={row.status} />
                </div>
                <p className="text-[13px] text-[#29343a] font-[600]">{row.client}</p>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-[11px] text-[#566168]">ห้อง {row.room}</span>
                  <span className="text-[13px] text-[#29343a] font-[700]">฿{row.amount}</span>
                </div>
                <p className="text-[10px] text-[#a0aab4] mt-1">{row.date}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Navigation */}
      <nav className={`fixed bottom-0 left-0 right-0 z-50 ${neu} rounded-t-2xl max-w-[500px] mx-auto`}>
        <div className="flex items-center justify-around py-2 pb-[max(8px,env(safe-area-inset-bottom))]">
          {[
            { id: "home", icon: Home, label: "หน้าหลัก", path: "/" },
            { id: "slip", icon: CreditCard, label: "สลิป", path: "/slip" },
            { id: "rooms", icon: Home, label: "ห้อง", path: "/rooms" },
            { id: "reports", icon: BarChart3, label: "รายงาน", path: "/reports" },
            { id: "settings", icon: SettingsIcon, label: "ตั้งค่า", path: "/settings" },
          ].map((tab) => (
            <Link
              key={tab.id}
              to={tab.path}
              onClick={() => setActiveTab(tab.id)}
              className={`flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-xl transition-all min-w-[56px] ${
                activeTab === tab.id
                  ? "shadow-[inset_3px_3px_6px_#d1d9e6,inset_-3px_-3px_6px_#ffffff] text-[#006D36]"
                  : "text-[#566168] active:scale-90"
              }`}
            >
              <tab.icon size={18} />
              <span className="text-[9px] font-[600]">{tab.label}</span>
            </Link>
          ))}
        </div>
      </nav>
    </div>
  )
}