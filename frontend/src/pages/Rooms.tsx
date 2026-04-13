import { useState } from 'react'
import { 
  ArrowLeft, Home, Building, Bed, Users, Search,
  CheckCircle, Clock, Filter, Plus, MoreHorizontal
} from 'lucide-react'

const neu = "bg-[#f0f4f8] shadow-[4px_4px_10px_#d1d9e6,-4px_-4px_10px_#ffffff]"
const neuInset = "bg-[#f0f4f8] shadow-[inset_3px_3px_6px_#d1d9e6,inset_-3px_-3px_6px_#ffffff]"

const mockRooms = [
  { number: 'A101', building: 'A', floor: 1, type: 'Standard', price: 400, status: 'ว่าง', guest: null },
  { number: 'A102', building: 'A', floor: 1, type: 'Standard', price: 400, status: 'ไม่ว่าง', guest: 'สมชาย ใจดี' },
  { number: 'A103', building: 'A', floor: 1, type: 'Standard', price: 400, status: 'ว่าง', guest: null },
  { number: 'A201', building: 'A', floor: 2, type: 'Standard', price: 500, status: 'ปิดปรับปรุง', guest: null },
  { number: 'A204', building: 'A', floor: 2, type: 'Monthly', price: 3500, status: 'ไม่ว่าง', guest: 'มานี มีเงิน' },
  { number: 'B101', building: 'B', floor: 1, type: 'Standard', price: 400, status: 'ว่าง', guest: null },
  { number: 'B102', building: 'B', floor: 1, type: 'Standard', price: 400, status: 'ไม่ว่าง', guest: 'วิชัย รวย' },
  { number: 'B105', building: 'B', floor: 1, type: 'Deluxe', price: 600, status: 'ว่าง', guest: null },
  { number: 'N01', building: 'N', floor: 1, type: 'VIP', price: 600, status: 'ไม่ว่าง', guest: 'ลิลลี่ สวย' },
]

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { color: string, bg: string, label: string }> = {
    'ว่าง': { color: 'text-green-600', bg: 'bg-green-50', label: 'ว่าง' },
    'ไม่ว่าง': { color: 'text-blue-600', bg: 'bg-blue-50', label: 'มีแขก' },
    'ปิดปรับปรุง': { color: 'text-amber-600', bg: 'bg-amber-50', label: 'ปิด' },
  }
  const { color, bg, label } = map[status] || map['ว่าง']
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${bg} ${color}`}>
      {status === 'ว่าง' && <CheckCircle size={10} />}
      {status === 'ไม่ว่าง' && <Users size={10} />}
      {status === 'ปิดปรับปรุง' && <Clock size={10} />}
      {label}
    </span>
  )
}

export default function Rooms() {
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')

  const buildings = ['all', 'A', 'B', 'N']
  const filteredRooms = mockRooms.filter(r => {
    if (filter !== 'all' && r.building !== filter) return false
    if (search && !r.number.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  const stats = {
    total: mockRooms.length,
    available: mockRooms.filter(r => r.status === 'ว่าง').length,
    occupied: mockRooms.filter(r => r.status === 'ไม่ว่าง').length,
    maintenance: mockRooms.filter(r => r.status === 'ปิดปรับปรุง').length,
  }

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
              <h1 className="text-[#29343a] text-base font-bold">ห้องพัก</h1>
              <p className="text-[#566168] text-xs">จัดการห้องและการจอง</p>
            </div>
          </div>
          <button className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#006D36] text-white text-sm font-semibold active:scale-95 transition-transform">
            <Plus size={14} />
            <span>เพิ่มห้อง</span>
          </button>
        </div>
      </nav>

      <div className="px-4 py-4 space-y-4">
        {/* Stats */}
        <div className="grid grid-cols-4 gap-2">
          <div className={`${neuInset} p-2 text-center rounded-xl`}>
            <p className="text-lg font-bold text-[#29343a]">{stats.total}</p>
            <p className="text-[10px] text-[#566168]">ทั้งหมด</p>
          </div>
          <div className={`${neuInset} p-2 text-center rounded-xl`}>
            <p className="text-lg font-bold text-green-600">{stats.available}</p>
            <p className="text-[10px] text-[#566168]">ว่าง</p>
          </div>
          <div className={`${neuInset} p-2 text-center rounded-xl`}>
            <p className="text-lg font-bold text-blue-600">{stats.occupied}</p>
            <p className="text-[10px] text-[#566168]">มีแขก</p>
          </div>
          <div className={`${neuInset} p-2 text-center rounded-xl`}>
            <p className="text-lg font-bold text-amber-600">{stats.maintenance}</p>
            <p className="text-[10px] text-[#566168]">ปิด</p>
          </div>
        </div>

        {/* Search & Filter */}
        <div className="flex gap-2">
          <div className={`flex-1 flex items-center gap-2 px-3 py-2.5 rounded-xl ${neuInset}`}>
            <Search size={16} className="text-[#a0aab4]" />
            <input 
              className="bg-transparent outline-none flex-1 text-sm text-[#29343a] placeholder-[#a0aab4]"
              placeholder="ค้นหาห้อง..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <button className={`p-2.5 rounded-xl ${neu} active:scale-95 transition-transform`}>
            <Filter size={16} className="text-[#566168]" />
          </button>
        </div>

        {/* Building Tabs */}
        <div className="flex gap-2">
          {buildings.map(b => (
            <button
              key={b}
              onClick={() => setFilter(b)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                filter === b 
                  ? 'bg-[#006D36] text-white shadow-[4px_4px_8px_#d1d9e6,-4px_-4px_8px_#ffffff]' 
                  : neu
              }`}
            >
              {b === 'all' ? 'ทั้งหมด' : `ตึก ${b}`}
            </button>
          ))}
        </div>

        {/* Room List */}
        <div className="space-y-3">
          {filteredRooms.map((room) => (
            <div key={room.number} className={`${neu} rounded-2xl p-4`}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-[#006D36]/10 flex items-center justify-center">
                    <Bed size={20} className="text-[#006D36]" />
                  </div>
                  <div>
                    <p className="text-base font-bold text-[#29343a]">ห้อง {room.number}</p>
                    <p className="text-xs text-[#566168]">ตึก {room.building} • ชั้น {room.floor} • {room.type}</p>
                  </div>
                </div>
                <StatusBadge status={room.status} />
              </div>
              
              <div className={`${neuInset} p-3 rounded-xl flex items-center justify-between`}>
                <div>
                  <p className="text-xs text-[#566168]">ราคา</p>
                  <p className="text-base font-bold text-[#006D36]">฿{room.price.toLocaleString()}/คืน</p>
                </div>
                {room.guest ? (
                  <div className="text-right">
                    <p className="text-xs text-[#566168]">ผู้พัก</p>
                    <p className="text-sm font-medium text-[#29343a]">{room.guest}</p>
                  </div>
                ) : (
                  <button className={`px-3 py-1.5 rounded-lg ${neu} text-xs font-medium text-[#006D36]`}>
                    จองห้อง
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Nav */}
      <nav className={`fixed bottom-0 left-0 right-0 z-50 ${neu} rounded-t-2xl max-w-[500px] mx-auto`}>
        <div className="flex items-center justify-around py-2 pb-3">
          {[
            { icon: Search, label: "หน้าหลัก", path: "/" },
            { icon: Search, label: "สลิป", path: "/slip" },
            { icon: Home, label: "ห้อง", path: "/rooms" },
            { icon: Search, label: "รายงาน", path: "/reports" },
            { icon: Search, label: "ตั้งค่า", path: "/settings" },
          ].map((tab, i) => (
            <a
              key={i}
              href={tab.path}
              className={`flex flex-col items-center gap-0.5 px-3 py-1.5 ${tab.path === '/rooms' ? 'text-[#006D36]' : 'text-[#566168]'}`}
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