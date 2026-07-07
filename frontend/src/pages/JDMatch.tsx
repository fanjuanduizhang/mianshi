import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api } from '@/services/api'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Textarea } from '@/components/ui/Textarea'
import { Badge } from '@/components/ui/Badge'
import { Progress } from '@/components/ui/Progress'
import {
  Target,
  CheckCircle,
  XCircle,
  BookOpen,
  TrendingUp,
  Calendar,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'

type TabType = 'analyze' | 'history'

export function JDMatch() {
  const [activeTab, setActiveTab] = useState<TabType>('analyze')
  const [jdText, setJdText] = useState('')
  const [userSkills, setUserSkills] = useState('')
  const [matchResult, setMatchResult] = useState<any>(null)
  const [jdInfo, setJdInfo] = useState<any>(null)
  const [studyPlan, setStudyPlan] = useState<any[]>([])
  const [expandedWeek, setExpandedWeek] = useState<number | null>(null)

  const analyzeMatch = useMutation({
    mutationFn: async () => {
      const skills = userSkills
        .split(/[,，\n]/)
        .map((s) => s.trim())
        .filter(Boolean)

      const [infoResult, matchResult] = await Promise.all([
        api.jd.extract(jdText),
        api.jd.match(jdText, skills, ''),
      ])

      setJdInfo(infoResult)
      setMatchResult(matchResult)
      setStudyPlan([])

      api.jd.save({
        company: infoResult.company,
        position: infoResult.position,
        location: infoResult.location,
        raw_text: jdText,
        extracted_skills: infoResult.skills,
        match_score: matchResult.match_score,
        gap_analysis: matchResult,
        ai_analysis: matchResult.gap_summary,
      })

      return matchResult
    },
  })

  const generatePlan = useMutation({
    mutationFn: () =>
      api.jd.generateStudyPlan(matchResult, jdInfo?.position || ''),
    onSuccess: (data) => {
      setStudyPlan(data.weeks)
    },
  })

  const getMatchColor = (score: number) => {
    if (score >= 80) return 'text-emerald-600'
    if (score >= 60) return 'text-amber-600'
    return 'text-red-600'
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">JD 匹配分析</h1>
        <p className="text-sm text-muted-foreground mt-1">
          分析岗位需求，找出差距，生成学习计划
        </p>
      </div>

      <div className="flex gap-2 mb-6 border-b border-border">
        {[
          { key: 'analyze', label: '智能分析' },
          { key: 'history', label: '历史记录' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as TabType)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${
              activeTab === tab.key
                ? 'border-foreground text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'analyze' && (
        <div className="grid grid-cols-5 gap-6">
          <Card className="col-span-2">
            <Card.Header>
              <Card.Title>输入岗位 JD</Card.Title>
            </Card.Header>
            <Card.Content className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-1.5 block">
                  岗位描述
                </label>
                <Textarea
                  placeholder="粘贴岗位招聘描述..."
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  rows={12}
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-1.5 block">
                  你的技能（用逗号分隔）
                </label>
                <Textarea
                  placeholder="Python, Django, MySQL, Redis..."
                  value={userSkills}
                  onChange={(e) => setUserSkills(e.target.value)}
                  rows={3}
                />
              </div>

              <Button
                className="w-full"
                onClick={() => analyzeMatch.mutate()}
                disabled={!jdText.trim() || analyzeMatch.isPending}
                loading={analyzeMatch.isPending}
              >
                <Target className="w-4 h-4" />
                开始匹配分析
              </Button>
            </Card.Content>
          </Card>

          <div className="col-span-3 space-y-6">
            {matchResult ? (
              <>
                <Card>
                  <Card.Content className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-xl font-semibold">
                          {jdInfo?.position || '岗位分析'}
                        </h3>
                        <p className="text-sm text-muted-foreground">
                          {jdInfo?.company || '未知公司'}
                          {jdInfo?.location && ` · ${jdInfo.location}`}
                        </p>
                      </div>
                      <div className="text-right">
                        <div
                          className={`text-4xl font-semibold ${getMatchColor(
                            matchResult.match_score
                          )}`}
                        >
                          {matchResult.match_score.toFixed(0)}
                          <span className="text-lg font-normal">%</span>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          匹配度
                        </div>
                      </div>
                    </div>
                    <Progress
                      value={matchResult.match_score}
                      variant={
                        matchResult.match_score >= 80
                          ? 'success'
                          : matchResult.match_score >= 60
                          ? 'warning'
                          : 'default'
                      }
                    />
                    <p className="text-sm text-muted-foreground mt-3">
                      {matchResult.gap_summary}
                    </p>
                  </Card.Content>
                </Card>

                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <Card.Header>
                      <Card.Title className="text-emerald-600 flex items-center gap-2">
                        <CheckCircle className="w-4 h-4" />
                        已具备技能
                      </Card.Title>
                    </Card.Header>
                    <Card.Content>
                      <div className="flex flex-wrap gap-1.5">
                        {matchResult.matched_skills?.map((s: string, i: number) => (
                          <Badge key={i} variant="success">
                            {s}
                          </Badge>
                        ))}
                      </div>
                    </Card.Content>
                  </Card>

                  <Card>
                    <Card.Header>
                      <Card.Title className="text-amber-600 flex items-center gap-2">
                        <XCircle className="w-4 h-4" />
                        需补充技能
                      </Card.Title>
                    </Card.Header>
                    <Card.Content>
                      <div className="space-y-2">
                        {matchResult.missing_skills?.map(
                          (s: any, i: number) => (
                            <div
                              key={i}
                              className="flex items-center justify-between text-sm"
                            >
                              <span>{s.skill_name}</span>
                              <Badge
                                variant={
                                  s.priority === 'high'
                                    ? 'error'
                                    : s.priority === 'medium'
                                    ? 'warning'
                                    : 'outline'
                                }
                              >
                                {s.priority === 'high'
                                  ? '高'
                                  : s.priority === 'medium'
                                  ? '中'
                                  : '低'}
                              </Badge>
                            </div>
                          )
                        )}
                      </div>
                    </Card.Content>
                  </Card>
                </div>

                <Card>
                  <Card.Header>
                    <Card.Title className="flex items-center gap-2">
                      <BookOpen className="w-4 h-4" />
                      岗位职责
                    </Card.Title>
                  </Card.Header>
                  <Card.Content>
                    <ul className="space-y-1.5">
                      {jdInfo?.responsibilities?.map(
                        (r: string, i: number) => (
                          <li
                            key={i}
                            className="text-sm text-muted-foreground flex items-start gap-2"
                          >
                            <span className="w-1.5 h-1.5 rounded-full bg-foreground mt-2 flex-shrink-0" />
                            {r}
                          </li>
                        )
                      )}
                    </ul>
                  </Card.Content>
                </Card>

                <Card>
                  <Card.Header>
                    <Card.Title className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4" />
                      改进建议
                    </Card.Title>
                  </Card.Header>
                  <Card.Content>
                    <ul className="space-y-2">
                      {matchResult.suggestions?.map(
                        (s: string, i: number) => (
                          <li
                            key={i}
                            className="text-sm text-muted-foreground flex items-start gap-2"
                          >
                            <span className="w-5 h-5 rounded-full bg-muted flex items-center justify-center text-xs font-medium flex-shrink-0">
                              {i + 1}
                            </span>
                            {s}
                          </li>
                        )
                      )}
                    </ul>
                  </Card.Content>
                </Card>

                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-semibold flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      学习计划
                    </h3>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => generatePlan.mutate()}
                      disabled={generatePlan.isPending}
                      loading={generatePlan.isPending}
                    >
                      生成学习计划
                    </Button>
                  </div>

                  {studyPlan.length > 0 && (
                    <div className="space-y-3">
                      {studyPlan.map((week: any) => (
                        <Card key={week.week}>
                          <button
                            className="w-full text-left"
                            onClick={() =>
                              setExpandedWeek(
                                expandedWeek === week.week ? null : week.week
                              )
                            }
                          >
                            <Card.Content className="p-4 flex items-center justify-between">
                              <div>
                                <div className="font-medium">
                                  第 {week.week} 周：{week.theme}
                                </div>
                                <div className="text-sm text-muted-foreground">
                                  {week.estimated_hours} 学时
                                </div>
                              </div>
                              {expandedWeek === week.week ? (
                                <ChevronUp className="w-4 h-4" />
                              ) : (
                                <ChevronDown className="w-4 h-4" />
                              )}
                            </Card.Content>
                          </button>
                          {expandedWeek === week.week && (
                            <div className="px-4 pb-4 pt-0 border-t border-border">
                              <div className="pt-4 space-y-3">
                                <div>
                                  <div className="text-xs font-medium text-muted-foreground mb-1">
                                    学习内容
                                  </div>
                                  <ul className="text-sm space-y-1">
                                    {week.topics?.map(
                                      (t: string, i: number) => (
                                        <li key={i}>• {t}</li>
                                      )
                                    )}
                                  </ul>
                                </div>
                                <div>
                                  <div className="text-xs font-medium text-muted-foreground mb-1">
                                    推荐资源
                                  </div>
                                  <ul className="text-sm space-y-1 text-muted-foreground">
                                    {week.resources?.map(
                                      (r: string, i: number) => (
                                        <li key={i}>• {r}</li>
                                      )
                                    )}
                                  </ul>
                                </div>
                                <div>
                                  <div className="text-xs font-medium text-muted-foreground mb-1">
                                    验收标准
                                  </div>
                                  <p className="text-sm text-muted-foreground">
                                    {week.milestone}
                                  </p>
                                </div>
                              </div>
                            </div>
                          )}
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
              </>
            ) : (
              <Card className="h-full">
                <Card.Content className="py-24 text-center">
                  <Target className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                  <p className="text-lg font-medium">开始分析</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    输入岗位 JD 和你的技能，查看匹配度
                  </p>
                </Card.Content>
              </Card>
            )}
          </div>
        </div>
      )}

      {activeTab === 'history' && (
        <div className="text-sm text-muted-foreground">
          历史记录功能开发中...
        </div>
      )}
    </div>
  )
}
