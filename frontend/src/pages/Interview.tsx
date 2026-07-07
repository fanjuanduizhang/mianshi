import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api } from '@/services/api'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Badge } from '@/components/ui/Badge'
import { Progress } from '@/components/ui/Progress'
import {
  Play,
  CheckCircle,
  Clock,
  Award,
  ChevronRight,
  ChevronLeft,
  MessageSquare,
  TrendingUp,
} from 'lucide-react'

type InterviewStage = 'setup' | 'question' | 'summary'

export function Interview() {
  const [stage, setStage] = useState<InterviewStage>('setup')
  const [position, setPosition] = useState('')
  const [questionCount, setQuestionCount] = useState(5)
  const [questions, setQuestions] = useState<any[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [userAnswer, setUserAnswer] = useState('')
  const [answers, setAnswers] = useState<any[]>([])
  const [currentFeedback, setCurrentFeedback] = useState<any>(null)
  const [showFeedback, setShowFeedback] = useState(false)
  const [summary, setSummary] = useState<any>(null)
  const [totalScore, setTotalScore] = useState(0)

  const startInterview = useMutation({
    mutationFn: () => api.interview.start(position, questionCount),
    onSuccess: (data) => {
      setQuestions(data.questions)
      setAnswers([])
      setCurrentIndex(0)
      setUserAnswer('')
      setTotalScore(0)
      setStage('question')
    },
  })

  const evaluateAnswer = useMutation({
    mutationFn: () =>
      api.interview.evaluate(
        questions[currentIndex],
        userAnswer,
        currentIndex + 1,
        totalScore
      ),
    onSuccess: (data) => {
      setCurrentFeedback(data)
      setShowFeedback(true)
    },
  })

  const handleNext = () => {
    const answerData = {
      question: questions[currentIndex].question,
      user_answer: userAnswer,
      score: currentFeedback?.total_score || 0,
    }
    const newAnswers = [...answers, answerData]
    setAnswers(newAnswers)
    setTotalScore(totalScore + (currentFeedback?.total_score || 0))

    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1)
      setUserAnswer('')
      setShowFeedback(false)
      setCurrentFeedback(null)
    } else {
      generateSummary(newAnswers)
    }
  }

  const generateSummary = async (allAnswers: any[]) => {
    const result = await api.interview.summary(
      position,
      allAnswers,
      totalScore + (currentFeedback?.total_score || 0),
      questions.length
    )
    setSummary(result)
    setStage('summary')

    api.interview.save({
      position,
      questions,
      answers: allAnswers,
      score: result.overall_score,
      feedback: result.overall_comment,
      duration: questions.length * 60,
    })
  }

  const currentQuestion = questions[currentIndex]

  if (stage === 'setup') {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">模拟面试</h1>
          <p className="text-sm text-muted-foreground mt-1">
            AI 面试官陪你练习真实面试场景
          </p>
        </div>

        <Card className="max-w-xl">
          <Card.Content className="space-y-6">
            <div className="text-center py-8">
              <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                <MessageSquare className="w-8 h-8" />
              </div>
              <h2 className="text-xl font-semibold">开始模拟面试</h2>
              <p className="text-sm text-muted-foreground mt-2">
                设置目标岗位和题目数量，AI 将为你生成专属面试题
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-1.5 block">
                  目标岗位
                </label>
                <Input
                  placeholder="例如：Python后端开发工程师"
                  value={position}
                  onChange={(e) => setPosition(e.target.value)}
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-1.5 block">
                  题目数量：{questionCount} 道
                </label>
                <input
                  type="range"
                  min="3"
                  max="15"
                  value={questionCount}
                  onChange={(e) => setQuestionCount(Number(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>

            <Button
              className="w-full"
              size="lg"
              onClick={() => startInterview.mutate()}
              disabled={startInterview.isPending}
              loading={startInterview.isPending}
            >
              <Play className="w-4 h-4" />
              开始面试
            </Button>
          </Card.Content>
        </Card>
      </div>
    )
  }

  if (stage === 'question') {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              {position || '模拟面试'}
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              第 {currentIndex + 1} / {questions.length} 题
            </p>
          </div>
          <Badge variant="outline" className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            总分：{totalScore.toFixed(0)}
          </Badge>
        </div>

        <Progress
          value={((currentIndex + 1) / questions.length) * 100}
          className="h-1"
        />

        <Card>
          <Card.Content className="space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Badge>{currentQuestion?.type}</Badge>
                <Badge variant="outline">{currentQuestion?.difficulty}</Badge>
                <Badge variant="outline">{currentQuestion?.category}</Badge>
              </div>
              <p className="text-lg font-medium leading-relaxed">
                {currentQuestion?.question}
              </p>
            </div>

            {!showFeedback ? (
              <div className="space-y-4">
                <Textarea
                  placeholder="请输入你的回答，模拟真实面试场景..."
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  rows={10}
                />
                <div className="flex justify-end">
                  <Button
                    onClick={() => evaluateAnswer.mutate()}
                    disabled={!userAnswer.trim() || evaluateAnswer.isPending}
                    loading={evaluateAnswer.isPending}
                  >
                    <CheckCircle className="w-4 h-4" />
                    提交回答
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="p-4 rounded-lg bg-muted/50 border border-border">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-medium">本题得分</span>
                    <span className="text-2xl font-semibold">
                      {currentFeedback?.total_score}
                      <span className="text-sm font-normal text-muted-foreground">
                        /100
                      </span>
                    </span>
                  </div>
                  <div className="grid grid-cols-5 gap-2">
                    {Object.entries(currentFeedback?.scores || {}).map(
                      ([key, value]: any) => (
                        <div key={key} className="text-center">
                          <div className="text-lg font-semibold">{value}</div>
                          <div className="text-xs text-muted-foreground capitalize">
                            {key === 'accuracy'
                              ? '准确性'
                              : key === 'completeness'
                              ? '完整性'
                              : key === 'logic'
                              ? '逻辑性'
                              : key === 'depth'
                              ? '深度'
                              : '表达'}
                          </div>
                        </div>
                      )
                    )}
                  </div>
                </div>

                <div className="p-4 rounded-lg bg-muted/30 border border-border">
                  <p className="text-sm leading-relaxed">
                    {currentFeedback?.feedback}
                  </p>
                </div>

                {currentFeedback?.strengths?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium mb-2 text-emerald-600">
                      亮点
                    </h4>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {currentFeedback.strengths.map((s: string, i: number) => (
                        <li key={i}>• {s}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {currentFeedback?.improvements?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium mb-2 text-amber-600">
                      改进建议
                    </h4>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {currentFeedback.improvements.map(
                        (s: string, i: number) => (
                          <li key={i}>• {s}</li>
                        )
                      )}
                    </ul>
                  </div>
                )}

                {currentFeedback?.follow_up && (
                  <div className="p-3 rounded-lg bg-blue-50 border border-blue-200">
                    <p className="text-sm text-blue-700">
                      <span className="font-medium">追问：</span>
                      {currentFeedback.follow_up}
                    </p>
                  </div>
                )}

                <div className="flex justify-between pt-4 border-t border-border">
                  <Button
                    variant="outline"
                    onClick={() => setShowFeedback(false)}
                  >
                    <ChevronLeft className="w-4 h-4" />
                    修改回答
                  </Button>
                  <Button onClick={handleNext}>
                    {currentIndex < questions.length - 1
                      ? '下一题'
                      : '查看总结'}
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

  if (stage === 'summary') {
    return (
      <div className="space-y-8">
        <div className="text-center">
          <div className="w-20 h-20 rounded-full bg-foreground text-background flex items-center justify-center mx-auto mb-4">
            <Award className="w-10 h-10" />
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">面试总结</h1>
          <p className="text-muted-foreground mt-2">
            共 {questions.length} 道题，总分{' '}
            {summary?.overall_score?.toFixed(0)} 分
          </p>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <Card>
            <Card.Content className="p-5 text-center">
              <div className="text-3xl font-semibold">
                {summary?.overall_score?.toFixed(0)}
              </div>
              <div className="text-sm text-muted-foreground mt-1">总体评分</div>
              <Badge
                className="mt-3"
                variant={
                  summary?.overall_score >= 80
                    ? 'success'
                    : summary?.overall_score >= 60
                    ? 'warning'
                    : 'error'
                }
              >
                {summary?.level}
              </Badge>
            </Card.Content>
          </Card>
          <Card>
            <Card.Content className="p-5 text-center">
              <TrendingUp className="w-8 h-8 mx-auto mb-2 text-emerald-500" />
              <div className="text-sm font-medium">技术能力</div>
              <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                {summary?.technical_evaluation}
              </p>
            </Card.Content>
          </Card>
          <Card>
            <Card.Content className="p-5 text-center">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 text-blue-500" />
              <div className="text-sm font-medium">表达能力</div>
              <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                {summary?.communication_evaluation}
              </p>
            </Card.Content>
          </Card>
        </div>

        <Card>
          <Card.Header>
            <Card.Title>总体评价</Card.Title>
          </Card.Header>
          <Card.Content>
            <p className="text-sm leading-relaxed text-muted-foreground">
              {summary?.overall_comment}
            </p>
          </Card.Content>
        </Card>

        <div className="grid grid-cols-2 gap-6">
          <Card>
            <Card.Header>
              <Card.Title className="text-emerald-600">优势</Card.Title>
            </Card.Header>
            <Card.Content>
              <ul className="space-y-2">
                {summary?.strengths?.map((s: string, i: number) => (
                  <li key={i} className="text-sm flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                    <span className="text-muted-foreground">{s}</span>
                  </li>
                ))}
              </ul>
            </Card.Content>
          </Card>

          <Card>
            <Card.Header>
              <Card.Title className="text-amber-600">待提升</Card.Title>
            </Card.Header>
            <Card.Content>
              <ul className="space-y-2">
                {summary?.weaknesses?.map((w: string, i: number) => (
                  <li key={i} className="text-sm flex items-start gap-2">
                    <Clock className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                    <span className="text-muted-foreground">{w}</span>
                  </li>
                ))}
              </ul>
            </Card.Content>
          </Card>
        </div>

        <Card>
          <Card.Header>
            <Card.Title>学习建议</Card.Title>
          </Card.Header>
          <Card.Content>
            <ul className="space-y-2">
              {summary?.study_suggestions?.map((s: string, i: number) => (
                <li key={i} className="text-sm flex items-start gap-2">
                  <span className="w-5 h-5 rounded-full bg-muted flex items-center justify-center text-xs font-medium flex-shrink-0">
                    {i + 1}
                  </span>
                  <span className="text-muted-foreground">{s}</span>
                </li>
              ))}
            </ul>
          </Card.Content>
        </Card>

        <div className="flex justify-center gap-3">
          <Button variant="outline" onClick={() => setStage('setup')}>
            再来一次
          </Button>
        </div>
      </div>
    )
  }

  return null
}
