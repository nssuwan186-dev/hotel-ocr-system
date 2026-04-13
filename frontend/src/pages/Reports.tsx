import { useState } from 'react'
import { 
  ArrowLeft, Home, FileText, Download, Calendar,
  TrendingUp, DollarSign, Users, PieChart, Search
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart as RePieChart, Pie, Cell
} from 'recharts'

const neu = "bg-[#f0f4f8] shadow-[4px_4px_10px_#d1d9e6,-4px_-4px_10px_#ffffff]"
const neuInset = "bg-[#f0f4f8] shadow-[inset_3px_3px_6px_#d1d9e6,inset_-3px_-3px_6px_#ffffff]"

const monthlyData = [
  { month: 'ม.ค.', income: 45000, expenses: 28000 },
  { month: 'ก.พ.', income: 52000, expenses: 31000 },
  { month: 'มี.ค.', income: 48000, expenses: 25000 },
  { month: 'เม.ย.', income: 61000, expenses: 34000 },
]

const channelData = [
  { name: 'เงินสด', value: 35, color: '#006D36' },
  { name: 'โอน', value: 50, color: '#4ade80' },
  { name: 'Booking', value: 15, color: '#d1d9e6' },
]

const weeklySummary = [
  { day: 'จ.', bookings: 8, revenue: 3200 },
  { day: 'อ.', bookings: 12, revenue: 4800 },
  { day: 'พ.', bookings: 6, revenue: 2400 },
  { day: 'พฤ.', bookings: 15, revenue: 6000 },
  { day: 'ศ.', bookings: 18, revenue: 7200 },
]

export default function Reports() {
  const [period, setPeriod] = useState('month')

  const totalIncome = monthlyData.reduce((sum, m) => sum + m.income, 0)
  const totalExpenses = monthlyData.reduce((sum, m) => sum + m.expenses, 0)
  const profit = totalIncome - totalExpenses

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
              <h1 className="text-[#29343a] text-base font-bold">รายงาน</h1>
              <p className="text-[#566168] text-xs">สรุปข้อมูลและวิเคราะห์</p>
            </div>
          </div>
          <button className={`flex items-center gap-1.5 px-3 py-2 rounded-xl ${neu} text-sm font-medium text-[#566168]`}>
            <Download size={14} />
            <span>ส่งออก</span>
          </button>
        </div>
      </nav>

      <div className="px-4 py-4 space-y-4">
        {/* Period Tabs */}
        <div className="flex gap-2">
          {['week', 'month', 'year'].map(p => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`flex-1 py-2 rounded-xl text-sm font-medium transition-all ${
                period === p 
                  ? 'bg-[#006D36] text-white shadow-[4px_4px_8px_#d1d9e6,-4px_-4px_8px_#ffffff]' 
                  : neu
              }`}
            >
              {p === 'week' ? 'สัปดาห์' : p === 'month' ? 'เดือน' : 'ปี'}
            </button>
          ))}
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-3 gap-3">
          <div className={`${neuInset} p-3 rounded-xl`}>
            <div className="w-8 h-8 rounded-lg bg-[#006D36]/10 flex items-center justify-center mb-2">
              <TrendingUp size={16} className="text-[#006D36]" />
            </div>
            <p className="text-lg font-bold text-[#29343a]">฿{(totalIncome/1000).toFixed(1)}K</p>
            <p className="text-[10px] text-[#566168]">รายรับรวม</p>
          </div>
          <div className={`${neuInset} p-3 rounded-xl`}>
            <div className="w-8 h-8 rounded-lg bg-red-50 flex items-center justify-center mb-2">
              <DollarSign size={16} className="text-red-500" />
            </div>
            <p className="text-lg font-bold text-[#29343a]">฿{(totalExpenses/1000).toFixed(1)}K</p>
            <p className="text-[10px] text-[#566168]">รายจ่ายรวม</p>
          </div>
          <div className={`${neuInset} p-3 rounded-xl`}>
            <div className="w-8 h-8 rounded-lg bg-green-50 flex items-center justify-center mb-2">
              <PieChart size={16} className="text-green-600" />
            </div>
            <p className="text-lg font-bold text-[#006D36]">฿{(profit/1000).toFixed(1)}K</p>
            <p className="text-[10px] text-[#566168]">กำไรสุทธิ</p>
          </div>
        </div>

        {/* Monthly Chart */}
        <div className={`${neu} rounded-2xl p-4`}>
          <p className="text-sm font-bold text-[#29343a] mb-3">รายรับ-รายจ่ายรายเดือน</p>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={monthlyData} barGap={4}>
              <XAxis dataKey="month" tick={{ fontSize: 10, fill: '#566168' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: '#566168' }} axisLine={false} tickLine={false} width={30} />
              <Tooltip contentStyle={{ fontSize: 11, borderRadius: 8 }} />
              <Bar dataKey="income" fill="#006D36" radius={[4, 4, 0, 0]} name="รายรับ" />
              <Bar dataKey="expenses" fill="#d1d9e6" radius={[4, 4, 0, 0]} name="รายจ่าย" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Channel Distribution */}
        <div className="grid grid-cols-2 gap-3">
          <div className={`${neu} rounded-2xl p-3`}>
            <p className="text-xs font-semibold text-[#29343a] mb-2">ช่องทางการชำระเงิน</p>
            <div className="flex justify-center">
              <RePieChart width={120} height={120}>
                <Pie 
                  data={channelData} 
                  cx={60} cy={60} 
                  innerRadius={35} 
                  outerRadius={50} 
                  dataKey="value" 
                  strokeWidth={0}
                >
                  {channelData.map((d, i) => <Cell key={i} fill={d.color} />)}
                </Pie>
              </RePieChart>
            </div>
            <div className="space-y-1 mt-2">
              {channelData.map(d => (
                <div key={d.name} className="flex items-center justify-between text-xs">
                  <span className="text-[#566168]">{d.name}</span>
                  <span className="text-[#29343a] font-medium">{d.value}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Weekly Summary */}
          <div className={`${neu} rounded-2xl p-3`}>
            <p className="text-xs font-semibold text-[#29343a] mb-2">สรุปรายสัปดาห์</p>
            <div className="space-y-2">
              {weeklySummary.map(d => (
                <div key={d.day} className="flex items-center justify-between">
                  <span className="text-xs text-[#566168] w-6">{d.day}</span>
                  <div className="flex-1 h-2 mx-2 bg-[#f0f4f8] rounded-full overflow-hidden shadow-[inset_2px_2px_4px_#d1d9e6,inset_-2px_-2px_4px_#ffffff]">
                    <div 
                      className="h-full bg-[#006D36] rounded-full" 
                      style={{ width: `${(d.revenue / 10000) * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-[#29343a] font-medium">฿{(d.revenue/1000).toFixed(1)}K</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Reports */}
        <div className="space-y-2">
          <p className="text-sm font-bold text-[#29343a]">รายงานด่วน</p>
          {[
            { label: 'รายงานรายวัน', icon: Calendar, desc: 'สรุปรายรับ-รายจ่ายประจำวัน' },
            { label: 'รายงานรายเดือน', icon: FileText, desc: 'สรุปรายได้และค่าใช้จ่าย' },
            { label: 'รายงานลูกค้า', icon: Users, desc: 'สถิติและพฤติกรรมลูกค้า' },
          ].map((item, i) => (
            <button key={i} className={`${neu} w-full p-3 flex items-center gap-3 text-left`}>
              <div className="w-10 h-10 rounded-xl bg-[#006D36]/10 flex items-center justify-center">
                <item.icon size={18} className="text-[#006D36]" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-[#29343a]">{item.label}</p>
                <p className="text-xs text-[#566168]">{item.desc}</p>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Bottom Nav */}
      <nav className={`fixed bottom-0 left-0 right-0 z-50 ${neu} rounded-t-2xl max-w-[500px] mx-auto`}>
        <div className="flex items-center justify-around py-2 pb-3">
          {[
            { icon: Search, label: "หน้าหลัก", path: "/" },
            { icon: Search, label: "สลิป", path: "/slip" },
            { icon: Search, label: "ห้อง", path: "/rooms" },
            { icon: FileText, label: "รายงาน", path: "/reports" },
            { icon: Search, label: "ตั้งค่า", path: "/settings" },
          ].map((tab, i) => (
            <a
              key={i}
              href={tab.path}
              className={`flex flex-col items-center gap-0.5 px-3 py-1.5 ${tab.path === '/reports' ? 'text-[#006D36]' : 'text-[#566168]'}`}
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