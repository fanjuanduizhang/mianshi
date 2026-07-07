from utils.llm import call_llm

class MockInterviewService:
    def start_interview(self, position: str = "", question_count: int = 5) -> list:
        prompt = f"""请生成一个{question_count}道题的模拟面试题目列表。

目标岗位：{position if position else '通用技术岗位'}

要求：
1. 包含技术题和行为题，比例约为7:3
2. 题目难度递进（简单→中等→困难）
3. 覆盖该岗位的核心知识点
4. 每道题都要有参考答案

请以JSON格式返回，包含一个questions数组，每个元素包含：
- id: 序号
- type: 题目类型（技术/行为）
- category: 分类
- question: 问题
- answer: 参考答案
- difficulty: 难度（简单/中等/困难）"""
        
        response = call_llm(prompt, max_tokens=4000)
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            json_str = response[start_idx:end_idx]
            result = eval(json_str)
            return result.get('questions', [])
        except:
            return [
                {
                    "id": 1,
                    "type": "技术",
                    "category": "基础",
                    "question": "请简单自我介绍一下你掌握的技术栈",
                    "answer": "这是一个开放性问题，建议从语言、框架、工具等方面有条理地介绍。",
                    "difficulty": "简单"
                }
            ]
    
    def evaluate_answer(self, question: dict, user_answer: str, question_index: int, total_score: float = 0) -> dict:
        prompt = f"""请对面试者的回答进行点评和打分。

第 {question_index} 题
题目类型：{question.get('type', '')}
问题：{question['question']}
参考答案：{question.get('answer', '')}
面试者回答：{user_answer}

请从以下维度评分（每项0-20分，总分100）：
1. 准确性 - 回答是否正确
2. 完整性 - 是否覆盖关键点
3. 逻辑性 - 表达是否有条理
4. 深度 - 是否有深入理解
5. 表达能力 - 语言表达是否清晰

请以JSON格式返回：
- scores: {{accuracy: 0-20, completeness: 0-20, logic: 0-20, depth: 0-20, expression: 0-20}}
- total_score: 总分（0-100）
- feedback: 详细点评文字
- strengths: 优点列表
- improvements: 改进建议列表
- follow_up: 一个追问问题（可选）"""
        
        response = call_llm(prompt, max_tokens=2000)
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            json_str = response[start_idx:end_idx]
            return eval(json_str)
        except:
            return {
                "scores": {"accuracy": 12, "completeness": 12, "logic": 12, "depth": 12, "expression": 12},
                "total_score": 60,
                "feedback": "已收到回答，建议对照参考答案进一步完善。",
                "strengths": [],
                "improvements": [],
                "follow_up": ""
            }
    
    def generate_summary(self, position: str, answers: list, total_score: float, question_count: int) -> dict:
        answers_str = ""
        for i, a in enumerate(answers, 1):
            answers_str += f"""
第{i}题：{a.get('question', '')}
回答：{a.get('user_answer', '')}
得分：{a.get('score', 0)}
"""
        
        prompt = f"""请为以下模拟面试生成总结报告。

目标岗位：{position if position else '通用岗位'}
总题目数：{question_count}
总分：{total_score} 分（满分{question_count * 100}分）

各题详情：
{answers_str}

请生成面试总结报告，包含：
1. 总体评价
2. 技术能力评估
3. 表达能力评估
4. 优势分析
5. 待提升点
6. 后续学习建议

请以JSON格式返回：
- overall_score: 总体评分（百分制）
- overall_comment: 总体评价
- technical_evaluation: 技术能力评估
- communication_evaluation: 表达能力评估
- strengths: 优势列表
- weaknesses: 待提升点列表
- study_suggestions: 学习建议列表
- level: 评级（优秀/良好/合格/需努力）"""
        
        response = call_llm(prompt, max_tokens=3000)
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            json_str = response[start_idx:end_idx]
            return eval(json_str)
        except:
            return {
                "overall_score": 60,
                "overall_comment": "面试完成，继续加油！",
                "technical_evaluation": "技术能力有待提升",
                "communication_evaluation": "表达能力可以进一步加强",
                "strengths": [],
                "weaknesses": [],
                "study_suggestions": ["多做练习题", "加强基础知识"],
                "level": "需努力"
            }
