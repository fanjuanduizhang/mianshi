import os
import re
import io
import base64
from PyPDF2 import PdfReader
from wordcloud import WordCloud
from app.core.llm import call_llm, parse_json_response


class ResumeService:
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()

    async def analyze_resume(
        self, resume_text: str, target_position: str = ""
    ) -> dict:
        prompt = f"""请分析以下简历内容，并提供详细的分析报告。

简历内容：
{resume_text}

目标岗位（可选）：{target_position}

请从以下几个方面分析：
1. 基本信息完整性（姓名、联系方式、教育背景等）
2. 技能清单和熟练度评估
3. 工作经历亮点和不足
4. 项目经验评估
5. 整体结构和排版建议

请以JSON格式返回结果，包含以下字段：
- basic_info: 基本信息分析
- skills: 技能列表（包含技能名称和熟练度）
- experience_highlights: 工作经历亮点
- experience_gaps: 工作经历不足
- project_evaluation: 项目经验评估
- suggestions: 优化建议列表"""

        response = await call_llm(prompt, max_tokens=3000)
        result = parse_json_response(
            response,
            default={
                "basic_info": "无法解析结构化数据",
                "skills": [],
                "experience_highlights": [],
                "experience_gaps": [],
                "project_evaluation": "无法解析",
                "suggestions": [],
            },
        )
        return result

    async def optimize_resume(
        self, resume_text: str, target_position: str = ""
    ) -> str:
        prompt = f"""请根据以下简历内容提供优化建议，使其更符合目标岗位的要求。

简历内容：
{resume_text}

目标岗位：{target_position}

请提供以下优化建议：
1. 关键词优化：针对目标岗位的关键词建议
2. 内容优化：如何突出与目标岗位相关的经验
3. 量化建议：如何用数据量化工作成果
4. 结构建议：简历结构优化建议
5. 语言优化：用词和表达优化建议

请用清晰的列表形式给出建议。"""

        return await call_llm(prompt, max_tokens=3000)

    async def extract_skills(self, resume_text: str) -> list:
        prompt = f"""请从以下简历中提取技能关键词，并按出现频率排序。

简历内容：
{resume_text}

请以JSON格式返回，包含一个skills数组，每个元素包含skill_name和count字段。"""

        response = await call_llm(prompt, max_tokens=1000)
        result = parse_json_response(response, default={"skills": []})

        skills = result.get("skills", [])
        if not skills:
            skills = self._extract_skills_regex(resume_text)

        return skills

    def _extract_skills_regex(self, resume_text: str) -> list:
        skills_pattern = re.compile(
            r"(Python|Java|C\+\+|JavaScript|React|Vue|Django|Flask|SQL|MySQL|PostgreSQL|Redis|MongoDB|Git|Linux|Docker|Kubernetes|AWS|GCP|TensorFlow|PyTorch|NLP|机器学习|深度学习)",
            re.IGNORECASE,
        )
        matches = skills_pattern.findall(resume_text)
        skill_counts = {}
        for skill in matches:
            skill_lower = skill.lower()
            skill_counts[skill_lower] = skill_counts.get(skill_lower, 0) + 1
        return [
            {"skill_name": k, "count": v} for k, v in skill_counts.items()
        ]

    def generate_wordcloud(self, skills: list) -> str:
        if not skills:
            return ""

        freq_dict = {s["skill_name"]: s["count"] for s in skills}

        wc = WordCloud(
            font_path=None,
            width=800,
            height=400,
            background_color="white",
            colormap="viridis",
            max_words=50,
        )
        wc.generate_from_frequencies(freq_dict)

        img = wc.to_image()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        return f"data:image/png;base64,{img_base64}"
