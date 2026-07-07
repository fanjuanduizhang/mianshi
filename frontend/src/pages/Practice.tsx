import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { api } from '@/services/api'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Textarea } from '@/components/ui/Textarea'
import { Badge } from '@/components/ui/Badge'
import { Progress } from '@/components/ui/Progress'
import {
  Play,
  CheckCircle,
  XCircle,
  RotateCcw,
  ChevronRight,
  ChevronLeft,
  Star,
  StarOff,
  Lightbulb,
} from 'lucide-react'

type TabType = 'practice' | 'collected' | 'review'

export function Practice() {
  const [activeTab, setActiveTab] = useState<TabType>('practice')
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [userAnswer, setUserAnswer] = useState('')
  const [showResult, setShowResult] = useState(false)
  const [questions, setQuestions] = useState<any[]>([])
  const [checkResult, setCheckResult] = useState<any>(null)
  const [isCollected, setIsCollected] = useState(false)

  const { data: categoriesData } = useQuery({
    queryKey: ['practice-categories'],
    queryFn: () => api.practice.getCategories(),
  })

  const categories = categoriesData?.categories || []

  const startPractice = useMutation({
    mutationFn: (category: string) =>
      api.practice.getQuestions({ category, count: 10 }),
    onSuccess: (data) => {
      console.log('Start practice success:', data)
      if (data && data.length > 0) {
        setQuestions(data)
        setCurrentQuestionIndex(0)
        setUserAnswer('')
        setShowResult(false)
        setCheckResult(null)
      }
    },
    onError: (error) => {
      console.error('Start practice error:', error)
      alert('获取题目失败，请重试')
    },
  })

  const checkAnswer = useMutation({
    mutationFn: () =>
      api.practice.checkAnswer(
        questions[currentQuestionIndex],
        userAnswer
      ),
    onSuccess: (data) => {
      setCheckResult(data)
      setShowResult(true)
    },
  })

  const currentQuestion = questions[currentQuestionIndex]

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
      setUserAnswer('')
      setShowResult(false)
      setCheckResult(null)
      setIsCollected(false)
    }
  }

  const handlePrev = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1)
      setShowResult(false)
      setCheckResult(null)
    }
  }

  const toggleCollect = () => {
    if (currentQuestion) {
      const newCollected = !isCollected
      setIsCollected(newCollected)
      api.practice.toggleCollect(currentQuestion.id, newCollected)
    }
  }

  if (questions.length === 0) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">刷题练习</h1>
          <p className="text-sm text-muted-foreground mt-1">
            选择分类，开始针对性练习
          </p>
        </div>

        <div className="flex gap-2 mb-6 border-b border-border">
          {[
            { key: 'practice', label: '分类练习' },
            { key: 'collected', label: '我的收藏' },
            { key: 'review', label: '待复习' },
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

        {activeTab === 'practice' && (
          <div className="grid grid-cols-3 gap-4">
            {categories.map((cat: string) => (
              <Card
                key={cat}
                className="cursor-pointer hover:shadow-md transition-shadow group"
                onClick={() => startPractice.mutate(cat)}
              >
                <Card.Content className="p-6">
                  <div className="flex items-center justify-between">
                    <h3 className="font-medium">{cat}</h3>
                    <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">
                    开始练习
                  </p>
                </Card.Content>
              </Card>
            ))}
          </div>
        )}

        {activeTab === 'collected' && <CollectedQuestions />}
        {activeTab === 'review' && <ReviewQuestions />}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            {currentQuestion?.category}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            第 {currentQuestionIndex + 1} / {questions.length} 题
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={toggleCollect}>
            {isCollected ? (
              <Star className="w-4 h-4 fill-current" />
            ) : (
              <StarOff className="w-4 h-4" />
            )}
            {isCollected ? '已收藏' : '收藏'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setQuestions([])
              setCurrentQuestionIndex(0)
            }}
          >
            <RotateCcw className="w-4 h-4" />
            重新选择
          </Button>
        </div>
      </div>

      <Progress
        value={((currentQuestionIndex + 1) / questions.length) * 100}
        className="h-1"
      />

      <Card>
        <Card.Content className="space-y-6">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Badge variant="outline">{currentQuestion?.difficulty}</Badge>
              <Badge>{currentQuestion?.category}</Badge>
            </div>
            <p className="text-lg font-medium leading-relaxed">
              {currentQuestion?.question}
            </p>
          </div>

          {!showResult ? (
            <div className="space-y-4">
              <Textarea
                placeholder="请输入你的回答..."
                value={userAnswer}
                onChange={(e) => setUserAnswer(e.target.value)}
                rows={8}
              />
              <div className="flex justify-end">
                <Button
                  onClick={() => checkAnswer.mutate()}
                  disabled={!userAnswer.trim() || checkAnswer.isPending}
                  loading={checkAnswer.isPending}
                >
                  <CheckCircle className="w-4 h-4" />
                  提交答案
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <div
                className={`p-4 rounded-lg ${
                  checkResult?.is_correct
                    ? 'bg-emerald-50 border border-emerald-200'
                    : 'bg-amber-50 border border-amber-200'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  {checkResult?.is_correct ? (
                    <CheckCircle className="w-5 h-5 text-emerald-600" />
                  ) : (
                    <XCircle className="w-5 h-5 text-amber-600" />
                  )}
                  <span
                    className={`font-semibold ${
                      checkResult?.is_correct
                        ? 'text-emerald-700'
                        : 'text-amber-700'
                    }`}
                  >
                    得分：{checkResult?.score} 分
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">
                  {checkResult?.is_correct ? '回答基本正确' : '回答有待提升'}
                </p>
              </div>

              {checkResult?.strengths?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-emerald-500" />
                    优点
                  </h4>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    {checkResult.strengths.map((s: string, i: number) => (
                      <li key={i}>• {s}</li>
                    ))}
                  </ul>
                </div>
              )}

              {checkResult?.weaknesses?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                    <XCircle className="w-4 h-4 text-amber-500" />
                    不足
                  </h4>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    {checkResult.weaknesses.map((w: string, i: number) => (
                      <li key={i}>• {w}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="p-4 rounded-lg bg-muted/50 border border-border">
                <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                  <Lightbulb className="w-4 h-4" />
                  参考答案
                </h4>
                <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                  {currentQuestion?.answer}
                </p>
              </div>

              {checkResult?.suggestions?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium mb-2">改进建议</h4>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    {checkResult.suggestions.map((s: string, i: number) => (
                      <li key={i}>• {s}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="flex justify-between pt-4 border-t border-border">
                <Button
                  variant="outline"
                  onClick={handlePrev}
                  disabled={currentQuestionIndex === 0}
                >
                  <ChevronLeft className="w-4 h-4" />
                  上一题
                </Button>
                <Button
                  onClick={handleNext}
                  disabled={currentQuestionIndex === questions.length - 1}
                >
                  下一题
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </Card.Content>
      </Card>
    </div>
  )
}

function CollectedQuestions() {
  const { data, isLoading } = useQuery({
    queryKey: ['collected-questions'],
    queryFn: () => api.practice.getCollected(),
  })

  if (isLoading) {
    return <div className="text-sm text-muted-foreground">加载中...</div>
  }

  if (!data || data.length === 0) {
    return (
      <Card>
        <Card.Content className="py-16 text-center">
          <Star className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">还没有收藏的题目</p>
        </Card.Content>
      </Card>
    )
  }

  return (
    <div className="space-y-3">
      {data.map((q: any) => (
        <Card key={q.id}>
          <Card.Content className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline">{q.category}</Badge>
              <Badge>{q.is_correct ? '已掌握' : '未掌握'}</Badge>
            </div>
            <p className="text-sm font-medium">{q.question_id}</p>
          </Card.Content>
        </Card>
      ))}
    </div>
  )
}

function ReviewQuestions() {
  const { data, isLoading } = useQuery({
    queryKey: ['review-questions'],
    queryFn: () => api.practice.getReview(),
  })

  if (isLoading) {
    return <div className="text-sm text-muted-foreground">加载中...</div>
  }

  if (!data || data.length === 0) {
    return (
      <Card>
        <Card.Content className="py-16 text-center">
          <Play className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">暂无需要复习的题目</p>
        </Card.Content>
      </Card>
    )
  }

  return (
    <div className="space-y-3">
      {data.map((q: any) => (
        <Card key={q.id}>
          <Card.Content className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline">{q.category}</Badge>
              <Badge variant="warning">复习 {q.review_count} 次</Badge>
            </div>
            <p className="text-sm font-medium">{q.question_id}</p>
          </Card.Content>
        </Card>
      ))}
    </div>
  )
}
