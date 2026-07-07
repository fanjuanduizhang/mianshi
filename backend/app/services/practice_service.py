import json
import os
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.config import settings
from app.models import QuestionRecord, UserProgress
from app.core.llm import call_llm, parse_json_response


class PracticeService:
    def __init__(self):
        self.questions = self._load_questions()

    def _load_questions(self):
        path = os.path.join(settings.QUESTION_BANK_PATH, "interview_questions.json")
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_categories(self):
        categories = set()
        for q in self.questions:
            categories.add(q.get("category", "其他"))
        return sorted(list(categories))

    def get_questions_by_category(self, category: str):
        return [q for q in self.questions if q.get("category") == category]

    def get_random_questions(
        self, category: str = None, count: int = 10, difficulty: str = None
    ):
        pool = self.questions
        if category:
            pool = [q for q in pool if q.get("category") == category]
        if difficulty:
            pool = [q for q in pool if q.get("difficulty") == difficulty]

        if len(pool) <= count:
            return self._convert_difficulty(pool)
        return self._convert_difficulty(random.sample(pool, count))

    def _convert_difficulty(self, questions: list) -> list:
        difficulty_map = {1: "简单", 2: "中等", 3: "困难"}
        result = []
        for q in questions:
            q_copy = q.copy()
            if isinstance(q_copy.get("difficulty"), int):
                q_copy["difficulty"] = difficulty_map.get(q_copy["difficulty"], "中等")
            result.append(q_copy)
        return result

    def get_question_by_id(self, question_id: str):
        for q in self.questions:
            if q.get("id") == question_id:
                return q
        return None

    async def check_answer(self, question: dict, user_answer: str) -> dict:
        prompt = f"""请判断求职者对以下面试题的回答质量，并给出评分和反馈。

问题：{question['question']}

参考答案：{question['answer']}

求职者回答：{user_answer}

请评估：
1. 准确性（是否正确）
2. 完整性（是否全面）
3. 逻辑性（是否有条理）

请以JSON格式返回：
- score: 分数（0-100）
- is_correct: 是否基本正确（true/false）
- strengths: 优点列表
- weaknesses: 不足列表
- suggestions: 改进建议列表
- key_points_missed: 遗漏的关键点列表"""

        response = await call_llm(prompt, max_tokens=1500)
        result = parse_json_response(
            response,
            default={
                "score": 60,
                "is_correct": False,
                "strengths": [],
                "weaknesses": ["无法自动评估"],
                "suggestions": ["请对照参考答案自行检查"],
                "key_points_missed": [],
            },
        )
        return result

    def calculate_next_review(self, quality_score: int, review_count: int) -> str:
        intervals = [1, 2, 4, 7, 15, 30, 60]
        idx = min(review_count, len(intervals) - 1)

        if quality_score >= 90:
            days = intervals[idx] * 2
        elif quality_score >= 70:
            days = intervals[idx]
        elif quality_score >= 50:
            days = max(1, intervals[idx] // 2)
        else:
            days = 1

        next_review = datetime.now() + timedelta(days=days)
        return next_review.isoformat()

    def get_stats(self, db: Session):
        total = len(self.questions)
        categories = self.get_categories()

        mastered = (
            db.query(QuestionRecord).filter(QuestionRecord.is_correct == 1).count()
        )
        collected = (
            db.query(QuestionRecord).filter(QuestionRecord.is_collected == 1).count()
        )
        practiced = db.query(QuestionRecord).count()

        category_stats = []
        for cat in categories:
            cat_questions = self.get_questions_by_category(cat)
            cat_total = len(cat_questions)

            cat_practiced = (
                db.query(QuestionRecord)
                .filter(QuestionRecord.category == cat)
                .count()
            )
            cat_mastered = (
                db.query(QuestionRecord)
                .filter(
                    QuestionRecord.category == cat, QuestionRecord.is_correct == 1
                )
                .count()
            )

            category_stats.append(
                {
                    "category": cat,
                    "total": cat_total,
                    "practiced": cat_practiced,
                    "mastered": cat_mastered,
                    "progress": round(cat_mastered / cat_total * 100, 1)
                    if cat_total > 0
                    else 0,
                }
            )

        return {
            "total_questions": total,
            "practiced": practiced,
            "mastered": mastered,
            "collected": collected,
            "overall_progress": round(mastered / total * 100, 1)
            if total > 0
            else 0,
            "category_stats": category_stats,
        }
