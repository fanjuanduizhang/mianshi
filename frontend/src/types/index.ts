export interface QuestionItem {
  id: string
  question: string
  answer: string
  category: string
  difficulty: string
}

export interface PracticeCheckResult {
  score: number
  is_correct: boolean
  strengths: string[]
  weaknesses: string[]
  suggestions: string[]
  key_points_missed: string[]
}

export interface DashboardStats {
  total_questions: number
  practiced: number
  mastered: number
  collected: number
  overall_progress: number
  category_stats: CategoryStat[]
  recent_interviews: InterviewSession[]
  jd_list: JDAnalysis[]
}

export interface CategoryStat {
  category: string
  total: number
  practiced: number
  mastered: number
  progress: number
}

export interface InterviewSession {
  id: number
  position?: string
  score?: number
  created_at: string
  questions?: any[]
  answers?: Record<string, any>
  feedback?: string
  duration?: number
}

export interface JDAnalysis {
  id: number
  company?: string
  position?: string
  location?: string
  match_score?: number
  created_at: string
  raw_text?: string
  extracted_skills?: any[]
  gap_analysis?: any
  ai_analysis?: string
}

export interface ResumeAnalysis {
  id: number
  file_name?: string
  target_position?: string
  created_at: string
  resume_text?: string
  analysis?: any
  suggestions?: string
  skills?: SkillItem[]
}

export interface SkillItem {
  skill_name: string
  count: number
}

export interface StudyPlan {
  id: number
  jd_id?: number
  title: string
  plan: any[]
  priority: number
  status: string
  estimated_hours: number
  created_at: string
  updated_at?: string
}

export interface UserProfile {
  id: number
  username: string
  education?: string
  school?: string
  major?: string
  target_position?: string
  skills: string[]
  created_at: string
  updated_at?: string
}

export interface RAGAnswer {
  answer: string
  relevant_docs: any[]
}

export interface JDMatchResult {
  match_score: number
  matched_skills: string[]
  missing_skills: { skill_name: string; priority: string }[]
  strengths: string[]
  weaknesses: string[]
  suggestions: string[]
  gap_summary: string
}
