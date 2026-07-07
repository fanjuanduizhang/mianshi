import json
from app.core.llm import call_llm, parse_json_response


class JDService:
    async def extract_jd_info(self, jd_text: str) -> dict:
        prompt = f"""请从以下岗位招聘描述中提取关键信息。

岗位描述：
{jd_text}

请提取：
1. 公司名称（如果有）
2. 岗位名称
3. 工作地点（如果有）
4. 要求的技能清单（技术栈、软技能等）
5. 岗位职责
6. 任职要求

请以JSON格式返回，包含以下字段：
- company: 公司名称，没有则为null
- position: 岗位名称
- location: 工作地点，没有则为null
- skills: 技能清单数组，每个元素包含skill_name和importance(1-5)
- responsibilities: 岗位职责数组
- requirements: 任职要求数组"""

        response = await call_llm(prompt, max_tokens=2000)
        result = parse_json_response(
            response,
            default={
                "company": None,
                "position": "未识别",
                "location": None,
                "skills": [],
                "responsibilities": [],
                "requirements": [],
            },
        )
        return result

    async def analyze_match(
        self, jd_text: str, user_skills: list = None, resume_text: str = ""
    ) -> dict:
        user_skills_str = ", ".join(user_skills) if user_skills else "未知"

        prompt = f"""请分析用户简历与目标岗位的匹配度，并找出差距。

岗位描述：
{jd_text}

用户技能：{user_skills_str}

用户简历内容（如果有）：
{resume_text}

请从以下几个方面分析：
1. 整体匹配度评分（0-100分）
2. 匹配的技能（用户已具备的技能）
3. 缺失的技能（需要补充的技能）
4. 改进建议（如何提升匹配度）
5. 核心差距分析

请以JSON格式返回，包含以下字段：
- match_score: 匹配度分数（数字，0-100）
- matched_skills: 匹配的技能数组
- missing_skills: 缺失的技能数组，每个包含skill_name和priority(high/medium/low)
- strengths: 优势列表数组
- weaknesses: 劣势列表数组
- suggestions: 改进建议数组
- gap_summary: 差距总结字符串"""

        response = await call_llm(prompt, max_tokens=3000)
        result = parse_json_response(
            response,
            default={
                "match_score": 0,
                "matched_skills": [],
                "missing_skills": [],
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "gap_summary": "分析失败，请重试",
            },
        )
        return result

    async def generate_study_plan(
        self, gap_analysis: dict, target_position: str = ""
    ) -> list:
        missing_skills_str = json.dumps(
            gap_analysis.get("missing_skills", []), ensure_ascii=False
        )

        prompt = f"""根据岗位差距分析，生成一个详细的学习计划。

目标岗位：{target_position}

需要提升的技能：
{missing_skills_str}

请生成4-6周的学习计划，每周包含：
1. 周主题
2. 学习内容列表
3. 推荐学习资源
4. 预计学习时长（小时）
5. 实践项目或练习
6. 验收标准

请以JSON格式返回，包含一个weeks数组，每个元素包含：
- week: 第几周
- theme: 周主题
- topics: 学习主题列表
- resources: 推荐资源列表
- estimated_hours: 预计学时
- practice: 实践练习
- milestone: 验收标准"""

        response = await call_llm(prompt, max_tokens=4000)
        result = parse_json_response(response, default={"weeks": []})
        weeks = result.get("weeks", [])

        if not weeks:
            weeks = [
                {
                    "week": 1,
                    "theme": "基础强化",
                    "topics": ["巩固核心基础概念", "梳理知识体系"],
                    "resources": ["官方文档", "经典教程"],
                    "estimated_hours": 10,
                    "practice": "基础练习题",
                    "milestone": "完成基础知识点梳理",
                }
            ]

        return weeks
