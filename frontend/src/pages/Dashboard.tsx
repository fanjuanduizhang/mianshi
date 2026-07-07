import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'
import { Card } from '@/components/ui/Card'
import { Progress } from '@/components/ui/Progress'
import { Badge } from '@/components/ui/Badge'
import {
  BookOpen,
  CheckCircle2,
  Star,
  TrendingUp,
  Clock,
  Target,
  ChevronRight,
} from 'lucide-react'
import { formatDate } from '@/lib/utils'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'

export function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => api.dashboard.getStats(),
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 w-48 bg-muted rounded mb-2" />
          <div className="h-4 w-64 bg-muted rounded" />
        </div>
        <div className="grid grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-28 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  const statCards = [
    {
      label: '题库总量',
      value: stats?.total_questions ?? 0,
      icon: BookOpen,
      description: '道面试题',
    },
    {
      label: '已练习',
      value: stats?.practiced ?? 0,
      icon: Target,
      description: '道题目',
    },
    {
      label: '已掌握',
      value: stats?.mastered ?? 0,
      icon: CheckCircle2,
      description: '道题目',
    },
    {
      label: '收藏题',
      value: stats?.collected ?? 0,
      icon: Star,
      description: '重点题目',
    },
  ]

  const chartData = stats?.category_stats?.map((s: any) => ({
    name: s.category,
    progress: s.progress,
  })) || []

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">仪表盘</h1>
        <p className="text-sm text-muted-foreground mt-1">
          你的学习进度一目了然
        </p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {statCards.map((stat, i) => {
          const Icon = stat.icon
          return (
            <Card key={i}>
              <Card.Content className="p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <p className="text-3xl font-semibold mt-2 tracking-tight">
                      {stat.value}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {stat.description}
                    </p>
                  </div>
                  <div className="p-2.5 rounded-lg bg-muted">
                    <Icon className="w-5 h-5 text-foreground/70" />
                  </div>
                </div>
              </Card.Content>
            </Card>
          )
        })}
      </div>

      <div className="grid grid-cols-3 gap-6">
        <Card className="col-span-2">
          <Card.Header>
            <Card.Title>学习进度</Card.Title>
            <Badge variant="outline">
              总体 {stats?.overall_progress?.toFixed(1)}%
            </Badge>
          </Card.Header>
          <Card.Content>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ left: 0 }}>
                  <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 12 }} />
                  <YAxis
                    type="category"
                    dataKey="name"
                    tick={{ fontSize: 12 }}
                    width={80}
                  />
                  <Tooltip
                    contentStyle={{
                      borderRadius: 6,
                      border: '1px solid #e5e5e5',
                      fontSize: 12,
                    }}
                    formatter={(value: number) => [`${value.toFixed(1)}%`, '掌握度']}
                  />
                  <Bar dataKey="progress" radius={[0, 4, 4, 0]}>
                    {chartData.map((_: any, index: number) => (
                      <Cell key={index} fill="#0a0a0a" />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card.Content>
        </Card>

        <Card>
          <Card.Header>
            <Card.Title>分类详情</Card.Title>
          </Card.Header>
          <Card.Content className="space-y-4">
            {stats?.category_stats?.map((cat: any, i: number) => (
              <div key={i}>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="font-medium">{cat.category}</span>
                  <span className="text-muted-foreground">
                    {cat.mastered}/{cat.total}
                  </span>
                </div>
                <Progress value={cat.progress} />
              </div>
            ))}
          </Card.Content>
        </Card>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <Card>
          <Card.Header>
            <Card.Title>最近面试</Card.Title>
            <ChevronRight className="w-4 h-4 text-muted-foreground" />
          </Card.Header>
          <Card.Content className="p-0">
            {stats?.recent_interviews?.length > 0 ? (
              <div className="divide-y divide-border">
                {stats.recent_interviews.map((iv: any) => (
                  <div
                    key={iv.id}
                    className="flex items-center justify-between px-6 py-3 hover:bg-muted/30 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-md bg-muted">
                        <TrendingUp className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">
                          {iv.position || '模拟面试'}
                        </p>
                        <p className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDate(iv.created_at)}
                        </p>
                      </div>
                    </div>
                    <Badge
                      variant={
                        iv.score >= 80
                          ? 'success'
                          : iv.score >= 60
                          ? 'warning'
                          : 'error'
                      }
                    >
                      {iv.score?.toFixed(0)} 分
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-12 text-center text-sm text-muted-foreground">
                暂无面试记录
              </div>
            )}
          </Card.Content>
        </Card>

        <Card>
          <Card.Header>
            <Card.Title>最近 JD</Card.Title>
            <ChevronRight className="w-4 h-4 text-muted-foreground" />
          </Card.Header>
          <Card.Content className="p-0">
            {stats?.jd_list?.length > 0 ? (
              <div className="divide-y divide-border">
                {stats.jd_list.map((jd: any) => (
                  <div
                    key={jd.id}
                    className="flex items-center justify-between px-6 py-3 hover:bg-muted/30 transition-colors"
                  >
                    <div>
                      <p className="text-sm font-medium">
                        {jd.position || '未命名岗位'}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {jd.company || '未知公司'}
                      </p>
                    </div>
                    <Badge variant="outline">
                      匹配 {jd.match_score?.toFixed(0)}%
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-12 text-center text-sm text-muted-foreground">
                暂无 JD 分析记录
              </div>
            )}
          </Card.Content>
        </Card>
      </div>
    </div>
  )
}
