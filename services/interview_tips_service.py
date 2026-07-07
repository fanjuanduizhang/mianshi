from utils.llm import call_llm

class InterviewTipsService:
    def get_tips_by_position(self, position: str) -> str:
        prompt = f"""请为申请以下岗位的求职者提供详细的面试技巧和注意事项。

目标岗位：{position}

请从以下几个方面提供建议：
1. 技术准备：需要重点复习的技术知识点
2. 简历准备：如何突出与该岗位相关的经验
3. 行为面试：常见的行为问题及回答策略
4. 自我介绍：如何准备一个出色的自我介绍
5. 薪资谈判：薪资谈判的技巧和策略
6. 常见问题：面试官常问的问题及回答建议
7. 注意事项：面试中的礼仪和注意事项

请用清晰的列表形式给出建议，每个部分要有具体的例子。"""
        
        return call_llm(prompt, max_tokens=3000)
    
    def get_behavior_questions(self, position: str = "") -> list:
        prompt = f"""请列出以下岗位常见的行为面试问题。

目标岗位：{position}

请提供至少10个常见的行为面试问题，并给出回答思路或要点。

请以JSON格式返回，包含一个questions数组，每个元素包含question和answer_tips字段。"""
        
        response = call_llm(prompt, max_tokens=2000)
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            json_str = response[start_idx:end_idx]
            result = eval(json_str)
            return result.get("questions", [])
        except:
            default_questions = [
                {"question": "请描述一次你遇到的技术挑战以及如何解决的", "answer_tips": "使用STAR法则：情境、任务、行动、结果"},
                {"question": "为什么想加入我们公司？", "answer_tips": "表达对公司业务的了解和认同，说明个人职业发展与公司目标的契合"},
                {"question": "你最大的优点和缺点是什么？", "answer_tips": "优点要结合岗位需求，缺点要体现自我认知和改进计划"},
                {"question": "描述一次团队合作经历", "answer_tips": "强调团队协作、沟通能力和贡献"},
                {"question": "你如何处理工作中的压力？", "answer_tips": "说明应对压力的方法和实际案例"}
            ]
            return default_questions
    
    def generate_practice_question(self, position: str = "") -> dict:
        prompt = f"""请为以下岗位生成一个模拟面试问题。

目标岗位：{position}

请生成一个技术问题或行为问题，并提供参考答案。

请以JSON格式返回，包含question_type（技术/行为）、question和answer字段。"""
        
        response = call_llm(prompt, max_tokens=1000)
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            json_str = response[start_idx:end_idx]
            return eval(json_str)
        except:
            return {
                "question_type": "技术",
                "question": "请解释RESTful API的设计原则",
                "answer": "RESTful API设计原则包括：使用HTTP方法表示操作、无状态通信、统一接口、资源通过URI标识、返回合适的HTTP状态码等。"
            }