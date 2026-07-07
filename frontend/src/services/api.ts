const API_BASE = '/api/v1'

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`)
  }
  return res.json()
}

export const api = {
  dashboard: {
    getStats: () => fetchJSON<any>('/dashboard/stats'),
  },

  practice: {
    getCategories: () => fetchJSON<any>('/practice/categories'),
    getQuestions: (params?: { category?: string; count?: number; difficulty?: string }) => {
      const qs = new URLSearchParams()
      if (params?.category) qs.set('category', params.category)
      if (params?.count) qs.set('count', String(params.count))
      if (params?.difficulty) qs.set('difficulty', params.difficulty)
      return fetchJSON<any[]>(`/practice/questions?${qs.toString()}`)
    },
    checkAnswer: (question: any, user_answer: string) =>
      fetchJSON<any>('/practice/check', {
        method: 'POST',
        body: JSON.stringify({ question, user_answer }),
      }),
    getStats: () => fetchJSON<any>('/practice/stats'),
    getCollected: () => fetchJSON<any[]>('/practice/collected'),
    getReview: () => fetchJSON<any[]>('/practice/review'),
    toggleCollect: (questionId: string, collected: boolean) =>
      fetchJSON<any>(`/practice/collect/${questionId}?collected=${collected}`, {
        method: 'POST',
      }),
  },

  interview: {
    start: (position: string, questionCount: number) =>
      fetchJSON<any>('/interview/start', {
        method: 'POST',
        body: JSON.stringify({ position, question_count: questionCount }),
      }),
    evaluate: (question: any, user_answer: string, question_index: number, total_score = 0) =>
      fetchJSON<any>('/interview/evaluate', {
        method: 'POST',
        body: JSON.stringify({ question, user_answer, question_index, total_score }),
      }),
    summary: (position: string, answers: any[], total_score: number, question_count: number) =>
      fetchJSON<any>('/interview/summary', {
        method: 'POST',
        body: JSON.stringify({ position, answers, total_score, question_count }),
      }),
    save: (data: any) =>
      fetchJSON<any>('/interview/save', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    getSessions: (limit = 10) => fetchJSON<any[]>(`/interview/sessions?limit=${limit}`),
    getSession: (id: number) => fetchJSON<any>(`/interview/sessions/${id}`),
  },

  resume: {
    upload: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch(`${API_BASE}/resume/upload`, {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) throw new Error('Upload failed')
      return res.json()
    },
    analyze: (resume_text: string, target_position = '') =>
      fetchJSON<any>('/resume/analyze', {
        method: 'POST',
        body: JSON.stringify({ resume_text, target_position }),
      }),
    save: (data: any) =>
      fetchJSON<any>('/resume/save', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    getRecords: (limit = 10) => fetchJSON<any[]>(`/resume/records?limit=${limit}`),
    getRecord: (id: number) => fetchJSON<any>(`/resume/records/${id}`),
    wordcloud: (skills: any[]) =>
      fetchJSON<any>('/resume/wordcloud', {
        method: 'POST',
        body: JSON.stringify({ skills }),
      }),
  },

  jd: {
    extract: (jd_text: string) =>
      fetchJSON<any>('/jd/extract', {
        method: 'POST',
        body: JSON.stringify({ jd_text }),
      }),
    match: (jd_text: string, user_skills: string[] = [], resume_text = '') =>
      fetchJSON<any>('/jd/match', {
        method: 'POST',
        body: JSON.stringify({ jd_text, user_skills, resume_text }),
      }),
    save: (data: any) =>
      fetchJSON<any>('/jd/save', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    getList: (limit = 10) => fetchJSON<any[]>(`/jd/list?limit=${limit}`),
    getDetail: (id: number) => fetchJSON<any>(`/jd/${id}`),
    generateStudyPlan: (gap_analysis: any, target_position = '') =>
      fetchJSON<any>('/jd/study-plan/generate', {
        method: 'POST',
        body: JSON.stringify({ gap_analysis, target_position }),
      }),
    saveStudyPlan: (data: any) =>
      fetchJSON<any>('/jd/study-plan/save', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    getStudyPlans: (status?: string) => {
      const url = status ? `/jd/study-plan/list?status=${status}` : '/jd/study-plan/list'
      return fetchJSON<any[]>(url)
    },
  },

  rag: {
    query: (question: string, top_k = 3) =>
      fetchJSON<any>('/rag/query', {
        method: 'POST',
        body: JSON.stringify({ question, top_k }),
      }),
    search: (q: string, top_k = 5) => fetchJSON<any>(`/rag/search?q=${encodeURIComponent(q)}&top_k=${top_k}`),
  },

  skills: {
    extract: (resume_text: string) =>
      fetchJSON<any>('/skills/extract', {
        method: 'POST',
        body: JSON.stringify({ resume_text }),
      }),
    wordcloud: (skills: any[]) =>
      fetchJSON<any>('/skills/wordcloud', {
        method: 'POST',
        body: JSON.stringify({ skills }),
      }),
  },

  user: {
    getProfile: () => fetchJSON<any>('/user/profile'),
    updateProfile: (data: any) =>
      fetchJSON<any>('/user/profile', {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
  },
}
