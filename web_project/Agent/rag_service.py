from typing import List, Dict, Any, Optional
from .chroma_store import ChromaStore
from .ollama_service import OllamaService

class RAGService:
    """检索增强生成(RAG)服务，结合向量检索和语言模型"""
    
    def __init__(self, 
                vector_store: Optional[ChromaStore] = None,
                ollama_service: Optional[OllamaService] = None,
                model_name: str = "qwen2.5:1.5b"):
        """初始化RAG服务
        
        Args:
            vector_store: 向量存储实例
            ollama_service: Ollama服务实例
            model_name: 使用的模型名称
        """
        self.vector_store = vector_store or ChromaStore()
        self.ollama_service = ollama_service or OllamaService()
        self.model_name = model_name
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """添加文档到知识库
        
        Args:
            documents: 文档列表
        """
        self.vector_store.add_documents(documents)
    
    def query(self, 
             query: str, 
             k: int = 3, 
             temperature: float = 0.7,
             system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """查询知识库并生成回答
        
        Args:
            query: 用户查询
            k: 检索的文档数量
            temperature: 生成温度
            system_prompt: 系统提示
            
        Returns:
            包含回答和相关文档的字典
        """
        try:
            # 检索相关文档
            relevant_docs = self.vector_store.similarity_search(query, k=k)
            
            if not relevant_docs:
                print("未找到相关文档，使用直接查询")
                return self.direct_query(query, system_prompt, temperature)
            
            # 构建提示
            context = "\n\n".join([f"文档: {doc['title']}\n内容: {doc['content']}" for doc in relevant_docs])
            
            default_system_prompt = """你是一个专业的手语识别与翻译专家，拥有丰富的手语知识和经验。请基于提供的文档回答用户关于手语识别、手语翻译、手语语法和手语文化的问题。

在回答时请注意：
1. 准确解释手语的语法特点、表达方式和文化背景
2. 说明手语识别技术的原理、挑战和最新进展
3. 提供关于手语学习和使用的实用建议
4. 如果文档中没有相关信息，请坦诚告知你不知道，不要编造信息
5. 尽可能使用通俗易懂的语言解释专业概念

你的回答应该对聋人群体保持尊重，并促进听障和非听障人士之间的沟通与理解。
"""
            
            rag_prompt = f"""请基于以下文档回答关于手语的问题:

{context}

问题: {query}
"""
            
            # 生成回答
            response = self.ollama_service.generate(
                prompt=rag_prompt,
                model=self.model_name,
                system_prompt=system_prompt or default_system_prompt,
                temperature=temperature
            )
            
            return {
                "answer": response["text"],
                "documents": relevant_docs,
                "source": "rag"
            }
        except Exception as e:
            import traceback
            print(f"RAG查询失败: {str(e)}")
            print(traceback.format_exc())
            # 出错时回退到直接查询
            try:
                return self.direct_query(query, system_prompt, temperature)
            except Exception as e2:
                print(f"直接查询也失败: {str(e2)}")
                return {
                    "answer": f"抱歉，查询处理过程中出现错误: {str(e)}",
                    "documents": [],
                    "source": "error"
                }
    
    def direct_query(self, 
                    query: str, 
                    system_prompt: Optional[str] = None,
                    temperature: float = 0.7) -> Dict[str, Any]:
        """直接查询语言模型，不使用RAG
        
        Args:
            query: 用户查询
            system_prompt: 系统提示
            temperature: 生成温度
            
        Returns:
            包含回答的字典
        """
        default_system_prompt = """你是一个专业的手语识别与翻译专家，拥有丰富的手语知识和经验。请回答用户关于手语识别、手语翻译、手语语法和手语文化的问题。

在回答时请注意：
1. 准确解释手语的语法特点、表达方式和文化背景
2. 说明手语识别技术的原理、挑战和最新进展
3. 提供关于手语学习和使用的实用建议
4. 如果你不确定答案，请坦诚告知你不知道，不要编造信息
5. 尽可能使用通俗易懂的语言解释专业概念

你的回答应该对聋人群体保持尊重，并促进听障和非听障人士之间的沟通与理解。
"""
        
        response = self.ollama_service.generate(
            prompt=query,
            model=self.model_name,
            system_prompt=system_prompt or default_system_prompt,
            temperature=temperature
        )
        
        return {
            "answer": response["text"],
            "source": "model_only"
        } 