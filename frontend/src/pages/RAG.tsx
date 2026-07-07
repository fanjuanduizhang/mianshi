import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api } from '@/services/api'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import {
  Search,
  Send,
  BookOpen,
  Sparkles,
  MessageCircle,
  Lightbulb,
} from 'lucide-react'

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  sources?: any[]
}

export function RAG() {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: 'assistant',
      content:
        '你好！我是 AI 面试助手，基于精选面试题库为你解答问题。你可以问我任何技术面试相关的问题。',
    },
  ])

  const askQuestion = useMutation({
    mutationFn: async (q: string) => {
      const result = await api.rag.query(q)
      return result
    },
    onMutate: (q) => {
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), role: 'user', content: q },
      ])
    },
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: 'assistant',
          content: data.answer,
          sources: data.relevant_docs,
        },
      ])
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || askQuestion.isPending) return
    askQuestion.mutate(query)
    setQuery('')
  }

  const suggestedQuestions = [
    'Python中的GIL是什么？',
    'Redis的常见数据结构有哪些？',
    'HTTP和HTTPS的区别？',
    '什么是数据库索引？',
  ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">智能问答</h1>
        <p className="text-sm text-muted-foreground mt-1">
          基于 RAG 技术的面试题库智能问答
        </p>
      </div>

      <div className="grid grid-cols-4 gap-6">
        <Card className="col-span-3 flex flex-col h-[calc(100vh-180px)]">
          <Card.Content className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${
                  msg.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-foreground text-background flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-4 h-4" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] ${
                    msg.role === 'user' ? 'order-first' : ''
                  }`}
                >
                  <div
                    className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-foreground text-background rounded-tr-sm'
                        : 'bg-muted rounded-tl-sm'
                    }`}
                  >
                    {msg.content}
                  </div>

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <div className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                        <BookOpen className="w-3 h-3" />
                        参考来源
                      </div>
                      <div className="space-y-1.5">
                        {msg.sources.map((src, i) => (
                          <div
                            key={i}
                            className="p-3 rounded-lg border border-border bg-white text-xs"
                          >
                            <div className="flex items-center gap-2 mb-1">
                              <Badge variant="outline">{src.category}</Badge>
                              <span className="text-muted-foreground">
                                {src.difficulty}
                              </span>
                            </div>
                            <div className="font-medium">{src.question}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
                    <MessageCircle className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))}

            {askQuestion.isPending && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-foreground text-background flex items-center justify-center">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div className="px-4 py-3 rounded-2xl rounded-tl-sm bg-muted">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
          </Card.Content>

          <div className="border-t border-border p-4">
            {messages.length <= 1 && (
              <div className="mb-4">
                <p className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
                  <Lightbulb className="w-3 h-3" />
                  试试这些问题
                </p>
                <div className="flex flex-wrap gap-2">
                  {suggestedQuestions.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        setQuery(q)
                      }}
                      className="px-3 py-1.5 text-xs rounded-full border border-border hover:bg-muted transition-colors"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="flex gap-2">
              <Input
                placeholder="输入你的问题..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="flex-1"
              />
              <Button type="submit" disabled={!query.trim() || askQuestion.isPending}>
                <Send className="w-4 h-4" />
                发送
              </Button>
            </form>
          </div>
        </Card>

        <Card>
          <Card.Header>
            <Card.Title className="flex items-center gap-2">
              <Search className="w-4 h-4" />
              关于
            </Card.Title>
          </Card.Header>
          <Card.Content className="space-y-4 text-sm text-muted-foreground">
            <p>
              本系统基于 RAG（检索增强生成）技术，结合精选面试题库，为你提供精准的面试问题解答。
            </p>
            <div className="space-y-2">
              <div className="font-medium text-foreground">支持的技术领域</div>
              <ul className="space-y-1">
                <li>• Python / Java</li>
                <li>• 算法与数据结构</li>
                <li>• 数据库 / Redis</li>
                <li>• 操作系统 / 网络</li>
                <li>• Spring / 微服务</li>
              </ul>
            </div>
          </Card.Content>
        </Card>
      </div>
    </div>
  )
}
