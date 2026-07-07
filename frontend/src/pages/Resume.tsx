import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api } from '@/services/api'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import {
  Upload,
  FileText,
  CheckCircle,
  AlertTriangle,
  Lightbulb,
  Sparkles,
  User,
} from 'lucide-react'

export function Resume() {
  const [resumeText, setResumeText] = useState('')
  const [targetPosition, setTargetPosition] = useState('')
  const [fileName, setFileName] = useState('')
  const [analysisResult, setAnalysisResult] = useState<any>(null)

  const uploadResume = useMutation({
    mutationFn: (file: File) => api.resume.upload(file),
    onSuccess: (data) => {
      setResumeText(data.text)
      setFileName(data.filename)
    },
  })

  const analyzeResume = useMutation({
    mutationFn: () => api.resume.analyze(resumeText, targetPosition),
    onSuccess: (data) => {
      setAnalysisResult(data)
      api.resume.save({
        file_name: fileName,
        resume_text: resumeText,
        target_position: targetPosition,
        analysis: data.analysis,
        suggestions: data.suggestions,
        skills: data.skills,
      })
    },
  })

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      uploadResume.mutate(file)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">简历优化</h1>
        <p className="text-sm text-muted-foreground mt-1">
          AI 帮你分析简历，提供专业优化建议
        </p>
      </div>

      <div className="grid grid-cols-5 gap-6">
        <Card className="col-span-2">
          <Card.Header>
            <Card.Title>上传简历</Card.Title>
          </Card.Header>
          <Card.Content className="space-y-4">
            <label className="block">
              <div className="border-2 border-dashed border-border rounded-lg p-8 text-center cursor-pointer hover:border-foreground/30 transition-colors">
                <Upload className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
                <p className="text-sm font-medium">点击上传 PDF 简历</p>
                <p className="text-xs text-muted-foreground mt-1">
                  或粘贴简历文本到下方
                </p>
              </div>
              <input
                type="file"
                accept=".pdf,.txt"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>

            {fileName && (
              <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg">
                <FileText className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm truncate flex-1">{fileName}</span>
                <Badge variant="success">已解析</Badge>
              </div>
            )}

            <div>
              <label className="text-sm font-medium mb-1.5 block">
                简历内容
              </label>
              <textarea
                className="w-full h-64 px-3 py-2 text-sm rounded-md border border-border bg-white placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-foreground/20 focus:border-foreground/50 transition-colors resize-y font-mono"
                placeholder="在此粘贴简历文本..."
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1.5 block">
                目标岗位
              </label>
              <Input
                placeholder="例如：Python开发工程师"
                value={targetPosition}
                onChange={(e) => setTargetPosition(e.target.value)}
              />
            </div>

            <Button
              className="w-full"
              onClick={() => analyzeResume.mutate()}
              disabled={!resumeText.trim() || analyzeResume.isPending}
              loading={analyzeResume.isPending}
            >
              <Sparkles className="w-4 h-4" />
              AI 分析简历
            </Button>
          </Card.Content>
        </Card>

        <div className="col-span-3 space-y-6">
          {analysisResult ? (
            <>
              <Card>
                <Card.Header>
                  <Card.Title className="flex items-center gap-2">
                    <User className="w-4 h-4" />
                    基本信息分析
                  </Card.Title>
                </Card.Header>
                <Card.Content>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {analysisResult.analysis?.basic_info}
                  </p>
                </Card.Content>
              </Card>

              <Card>
                <Card.Header>
                  <Card.Title className="flex items-center gap-2">
                    <Lightbulb className="w-4 h-4" />
                    技能评估
                  </Card.Title>
                </Card.Header>
                <Card.Content>
                  <div className="flex flex-wrap gap-2">
                    {analysisResult.skills?.map((skill: any, i: number) => (
                      <Badge key={i} variant="outline">
                        {skill.skill_name}
                        <span className="ml-1 text-muted-foreground">
                          ×{skill.count}
                        </span>
                      </Badge>
                    ))}
                  </div>
                </Card.Content>
              </Card>

              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <Card.Header>
                    <Card.Title className="text-emerald-600 flex items-center gap-2">
                      <CheckCircle className="w-4 h-4" />
                      亮点
                    </Card.Title>
                  </Card.Header>
                  <Card.Content>
                    <ul className="space-y-2">
                      {analysisResult.analysis?.experience_highlights?.map(
                        (h: string, i: number) => (
                          <li
                            key={i}
                            className="text-sm text-muted-foreground flex items-start gap-2"
                          >
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                            {h}
                          </li>
                        )
                      )}
                    </ul>
                  </Card.Content>
                </Card>

                <Card>
                  <Card.Header>
                    <Card.Title className="text-amber-600 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" />
                      不足
                    </Card.Title>
                  </Card.Header>
                  <Card.Content>
                    <ul className="space-y-2">
                      {analysisResult.analysis?.experience_gaps?.map(
                        (g: string, i: number) => (
                          <li
                            key={i}
                            className="text-sm text-muted-foreground flex items-start gap-2"
                          >
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 flex-shrink-0" />
                            {g}
                          </li>
                        )
                      )}
                    </ul>
                  </Card.Content>
                </Card>
              </div>

              <Card>
                <Card.Header>
                  <Card.Title className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    优化建议
                  </Card.Title>
                </Card.Header>
                <Card.Content>
                  <div className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                    {analysisResult.suggestions}
                  </div>
                </Card.Content>
              </Card>
            </>
          ) : (
            <Card className="h-full">
              <Card.Content className="py-24 text-center">
                <FileText className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                <p className="text-lg font-medium">等待分析</p>
                <p className="text-sm text-muted-foreground mt-1">
                  上传或粘贴简历后，点击 AI 分析按钮
                </p>
              </Card.Content>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
