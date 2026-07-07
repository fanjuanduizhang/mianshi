import os
import re
from PyPDF2 import PdfReader
from utils.llm import call_llm
from config import RESUME_UPLOAD_PATH

class ResumeService:
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    
    def analyze_resume(self, resume_text: str, target_position: str = "") -> dict:
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
        
        response = call_llm(prompt, max_tokens=3000)
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            json_str = response[start_idx:end_idx]
            return eval(json_str)
        except:
            return {
                "basic_info": "无法解析结构化数据",
                "skills": [],
                "experience_highlights": [],
                "experience_gaps": [],
                "project_evaluation": "无法解析",
                "suggestions": []
            }
    
    def optimize_resume(self, resume_text: str, target_position: str = "") -> str:
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
        
        return call_llm(prompt, max_tokens=3000)
    
    def extract_skills(self, resume_text: str) -> list:
        prompt = f"""请从以下简历中提取技能关键词，并按出现频率排序。

简历内容：
{resume_text}

请以JSON格式返回，包含一个skills数组，每个元素包含skill_name和count字段。"""
        
        response = call_llm(prompt, max_tokens=1000)
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            json_str = response[start_idx:end_idx]
            result = eval(json_str)
            return result.get("skills", [])
        except:
            skills_pattern = re.compile(
                r'(Python|Java|C\+\+|JavaScript|React|Vue|Django|Flask|SQL|MySQL|PostgreSQL|Redis|MongoDB|Git|Linux|Docker|Kubernetes|AWS|GCP|TensorFlow|PyTorch|NLP|机器学习|深度学习)',
                re.IGNORECASE
            )
            matches = skills_pattern.findall(resume_text)
            skill_counts = {}
            for skill in matches:
                skill_counts[skill.lower()] = skill_counts.get(skill.lower(), 0) + 1
            return [{"skill_name": k, "count": v} for k, v in skill_counts.items()]