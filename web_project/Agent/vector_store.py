import os
import numpy as np
from pathlib import Path
import pickle
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

class VectorStore:
    """向量数据库实现，用于存储和检索文档向量"""
    
    def __init__(self, model_name="paraphrase-multilingual-MiniLM-L12-v2"):
        """初始化向量存储
        
        Args:
            model_name: 用于生成嵌入的模型名称
        """
        self.model = SentenceTransformer(model_name)
        self.vectors = []
        self.documents = []
        self.store_path = Path(os.path.dirname(os.path.abspath(__file__))) / "vector_data"
        self.store_path.mkdir(exist_ok=True)
        self.vector_file = self.store_path / "vectors.pkl"
        self.document_file = self.store_path / "documents.pkl"
        self._load_if_exists()
    
    def _load_if_exists(self):
        """如果存在向量数据，则加载"""
        if self.vector_file.exists() and self.document_file.exists():
            try:
                with open(self.vector_file, 'rb') as f:
                    self.vectors = pickle.load(f)
                with open(self.document_file, 'rb') as f:
                    self.documents = pickle.load(f)
                print(f"已加载 {len(self.vectors)} 个文档向量")
            except Exception as e:
                print(f"加载向量数据失败: {e}")
                self.vectors = []
                self.documents = []
    
    def _save(self):
        """保存向量和文档数据"""
        with open(self.vector_file, 'wb') as f:
            pickle.dump(self.vectors, f)
        with open(self.document_file, 'wb') as f:
            pickle.dump(self.documents, f)
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """添加文档到向量存储
        
        Args:
            documents: 文档列表，每个文档是一个字典，包含'content'和其他元数据
        """
        if not documents:
            return
            
        texts = [doc['content'] for doc in documents]
        embeddings = self.model.encode(texts)
        
        for i, doc in enumerate(documents):
            self.vectors.append(embeddings[i])
            self.documents.append(doc)
        
        self._save()
        print(f"已添加 {len(documents)} 个文档到向量存储")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """基于查询进行相似性搜索
        
        Args:
            query: 查询文本
            k: 返回的最相似文档数量
            
        Returns:
            最相似的k个文档列表
        """
        if not self.vectors:
            return []
            
        query_embedding = self.model.encode(query)
        
        # 计算余弦相似度
        similarities = []
        for vec in self.vectors:
            similarity = np.dot(query_embedding, vec) / (np.linalg.norm(query_embedding) * np.linalg.norm(vec))
            similarities.append(similarity)
        
        # 获取最相似的k个文档索引
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        
        # 返回文档和相似度
        results = []
        for idx in top_k_indices:
            doc = self.documents[idx].copy()
            doc['similarity'] = float(similarities[idx])
            results.append(doc)
            
        return results
    
    def clear(self):
        """清空向量存储"""
        self.vectors = []
        self.documents = []
        if self.vector_file.exists():
            self.vector_file.unlink()
        if self.document_file.exists():
            self.document_file.unlink()
        print("向量存储已清空") 