import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  BookOpen,
  MessageSquare,
  FileText,
  Target,
  Search,
  PieChart,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { path: '/', label: '仪表盘', icon: LayoutDashboard },
  { path: '/practice', label: '刷题练习', icon: BookOpen },
  { path: '/interview', label: '模拟面试', icon: MessageSquare },
  { path: '/resume', label: '简历优化', icon: FileText },
  { path: '/jd-match', label: 'JD匹配', icon: Target },
  { path: '/rag', label: '智能问答', icon: Search },
  { path: '/skills', label: '技能分析', icon: PieChart },
]

export function Sidebar() {
  return (
    <aside className="w-60 border-r border-border bg-white flex flex-col h-screen sticky top-0">
      <div className="h-16 flex items-center px-5 border-b border-border">
        <h1 className="text-lg font-semibold tracking-tight">
          AI Job Hunter
        </h1>
      </div>
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors',
                  isActive
                    ? 'bg-muted text-foreground font-medium'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                )
              }
            >
              <Icon className="w-4 h-4" />
              {item.label}
            </NavLink>
          )
        })}
      </nav>
      <div className="p-4 border-t border-border">
        <div className="text-xs text-muted-foreground">
          v2.0.0 · 全面升级版
        </div>
      </div>
    </aside>
  )
}
