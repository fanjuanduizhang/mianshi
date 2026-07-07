import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api } from '@/services/api'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Textarea } from '@/components/ui/Textarea'
import { Badge } from '@/components/ui/Badge'
import {
  PieChart,
  Upload,
  Sparkles,
  FileText,
  TrendingUp,
} from 'lucide-react'

export function Skills() {
  const [resumeText, setResumeText] = useState('')
  const [skills, setSkills] = useState<any[]>([])
  const [wordcloudImage, setWordcloudImage] = useState('')

  const extractSkills = useMutation({
    mutationFn: async () => {
      const result = await api.skills.extract(resumeText)
      setSkills(result.skills || [])

      if (result.skills?.length > 0) {
        const wcResult = await api.skills.wordcloud(result.skills)
        setWordcloudImage(wcResult.image)
      }

      return result
    },
  })

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        setResumeText(event.target?.result as string)
      }
      reader.readAsText(file)
    }
  }

  const sortedSkills = [...skills].sort((a, b) => b.count - a.count)
  const maxCount = Math.max(...sortedSkills.map((s) => s.count), 1)

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">技能分析</h1>
        <p className="text-sm text-muted-foreground mt-1">
          从简历中提取技能关键词，生成可视化技能云
        </p>
      </div>

      <div className="grid grid-cols-5 gap-6">
        <Card className="col-span-2">
          <Card.Header>
            <Card.Title>输入简历</Card.Title>
          </Card.Header>
          <Card.Content className="space-y-4">
            <label className="block">
              <div className="border-2 border-dashed border-border rounded-lg p-6 text-center cursor-pointer hover:border-foreground/30 transition-colors">
                <Upload className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
                <p className="text-sm font-medium">上传简历文件</p>
                <p className="text-xs text-muted-foreground mt-1">
                  支持 .txt 格式
                </p>
              </div>
              <input
                type="file"
                accept=".txt"
                onChange={handleUpload}
                className="hidden"
              />
            </label>

            <div className="text-center text-xs text-muted-foreground">或</div>

            <div>
              <label className="text-sm font-medium mb-1.5 block">
                粘贴简历内容
              </label>
              <Textarea
                placeholder="在此粘贴简历文本..."
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                rows={14}
              />
            </div>

            <Button
              className="w-full"
              onClick={() => extractSkills.mutate()}
              disabled={!resumeText.trim() || extractSkills.isPending}
              loading={extractSkills.isPending}
            >
              <Sparkles className="w-4 h-4" />
              分析技能
            </Button>
          </Card.Content>
        </Card>

        <div className="col-span-3 space-y-6">
          {skills.length > 0 ? (
            <>
              <Card>
                <Card.Header>
                  <Card.Title className="flex items-center gap-2">
                    <PieChart className="w-4 h-4" />
                    技能云图
                  </Card.Title>
                </Card.Header>
                <Card.Content>
                  {wordcloudImage ? (
                    <div className="flex justify-center p-4 bg-muted/30 rounded-lg">
                      <img
                        src={wordcloudImage}
                        alt="技能词云"
                        className="max-w-full rounded-lg"
                      />
                    </div>
                  ) : (
                    <div className="h-48 flex items-center justify-center text-muted-foreground text-sm">
                      词云生成中...
                    </div>
                  )}
                </Card.Content>
              </Card>

              <Card>
                <Card.Header>
                  <Card.Title className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" />
                    技能排名
                  </Card.Title>
                  <Badge variant="outline">共 {skills.length} 项技能</Badge>
                </Card.Header>
                <Card.Content>
                  <div className="space-y-3">
                    {sortedSkills.map((skill, i) => (
                      <div key={i}>
                        <div className="flex items-center justify-between text-sm mb-1.5">
                          <div className="flex items-center gap-2">
                            <span className="w-5 h-5 rounded-full bg-muted flex items-center justify-center text-xs font-medium">
                              {i + 1}
                            </span>
                            <span className="font-medium">{skill.skill_name}</span>
                          </div>
                          <span className="text-muted-foreground">
                            {skill.count} 次
                          </span>
                        </div>
                        <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-foreground rounded-full transition-all duration-500"
                            style={{
                              width: `${(skill.count / maxCount) * 100}%`,
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </Card.Content>
              </Card>

              <Card>
                <Card.Header>
                  <Card.Title>技能标签</Card.Title>
                </Card.Header>
                <Card.Content>
                  <div className="flex flex-wrap gap-2">
                    {sortedSkills.map((skill, i) => (
                      <Badge
                        key={i}
                        variant="outline"
                        className="text-sm px-3 py-1"
                      >
                        {skill.skill_name}
                        <span className="ml-1.5 text-xs text-muted-foreground">
                          {skill.count}
                        </span>
                      </Badge>
                    ))}
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
                  上传或粘贴简历，提取技能关键词
                </p>
              </Card.Content>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
