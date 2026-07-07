import json
import os
import chromadb
from app.config import settings
from app.core.llm import call_llm


class RAGService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMADB_PATH)
        self.collection = self.client.get_or_create_collection(
            name="interview_questions"
        )
        self._ensure_data_loaded()

    def _ensure_data_loaded(self):
        if self.collection.count() == 0:
            self.load_question_bank()

    def load_question_bank(self):
        questions_path = os.path.join(
            settings.QUESTION_BANK_PATH, "interview_questions.json"
        )
        if not os.path.exists(questions_path):
            return

        with open(questions_path, "r", encoding="utf-8") as f:
            questions = json.load(f)

        documents = []
        metadatas = []
        ids = []

        for q in questions:
            doc = f"问题：{q['question']}\n答案：{q['answer']}"
            documents.append(doc)
            metadatas.append(
                {"category": q["category"], "difficulty": q["difficulty"]}
            )
            ids.append(q["id"])

        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def query(self, question: str, top_k: int = 3) -> list:
        results = self.collection.query(
            query_texts=[question],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        return [
            {
                "question": doc.split("\n")[0].replace("问题：", ""),
                "answer": doc.split("\n")[1].replace("答案：", ""),
                "category": meta["category"],
                "difficulty": meta["difficulty"],
                "distance": dist,
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]

    async def answer_with_rag(self, question: str) -> dict:
        relevant_docs = self.query(question, top_k=3)

        context = "\n\n".join(
            [
                f"【{doc['category']}】\n问题：{doc['question']}\n答案：{doc['answer']}"
                for doc in relevant_docs
            ]
        )

        prompt = f"""基于以下面试题库知识回答用户问题：

知识库内容：
{context}

用户问题：{question}

请根据知识库内容回答问题，如果知识库中没有相关信息，可以结合你的专业知识回答。回答要简洁、专业。"""

        answer = await call_llm(prompt)
        return {"answer": answer, "relevant_docs": relevant_docs}
