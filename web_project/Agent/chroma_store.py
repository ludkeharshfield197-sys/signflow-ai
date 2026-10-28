import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
import traceback
import shutil

class ChromaStore:
    """ChromaDB向量数据库实现，用于存储和检索文档向量"""
    
    def __init__(self, collection_name="sign_language_knowledge", max_retries=3, force_recreate=False):
        """初始化ChromaDB向量存储
        
        Args:
            collection_name: 集合名称
            max_retries: 最大重试次数
            force_recreate: 是否强制重新创建集合
        """
        # 设置持久化目录
        self.persist_directory = Path(os.path.dirname(os.path.abspath(__file__))) / "chroma_data"
        
        # 如果强制重新创建或目录不存在，确保目录是全新的
        if force_recreate and self.persist_directory.exists():
            try:
                shutil.rmtree(str(self.persist_directory))
                print(f"已删除现有ChromaDB目录: {self.persist_directory}")
            except Exception as e:
                print(f"删除ChromaDB目录失败: {e}")
        
        # 确保目录存在
        self.persist_directory.mkdir(exist_ok=True)
        
        # 初始化ChromaDB客户端
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # 创建客户端
                self.client = chromadb.PersistentClient(
                    path=str(self.persist_directory),
                    settings=Settings(anonymized_telemetry=False)
                )
                
                # 使用Ollama作为嵌入函数
                self.embedding_function = embedding_functions.OllamaEmbeddingFunction(
                    model_name="qwen2.5:1.5b",
                    url="http://localhost:11434"
                )
                
                # 尝试创建新集合（不管是否存在）
                try:
                    # 如果集合已存在，先删除
                    try:
                        self.client.delete_collection(collection_name)
                        print(f"已删除现有集合: {collection_name}")
                    except Exception as e:
                        # 忽略集合不存在的错误
                        pass
                    
                    # 创建新集合
                    self.collection = self.client.create_collection(
                        name=collection_name,
                        embedding_function=self.embedding_function
                    )
                    print(f"已创建新集合: {collection_name}")
                    break  # 成功创建集合，跳出循环
                except Exception as e:
                    print(f"创建集合失败: {e}")
                    last_error = e
                    retry_count += 1
                    time.sleep(1)
                    continue
                    
            except Exception as e:
                print(f"ChromaDB客户端初始化失败 (尝试 {retry_count+1}/{max_retries}): {e}")
                print(traceback.format_exc())
                last_error = e
                retry_count += 1
                time.sleep(1)
        
        if retry_count >= max_retries:
            # 所有重试都失败了，使用内存集合作为备用
            print("使用内存集合作为备用")
            try:
                self.client = chromadb.Client()
                self.collection = self.client.create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function
                )
                print(f"已创建内存集合: {collection_name}")
            except Exception as e:
                raise Exception(f"ChromaDB初始化完全失败: {e}, 原始错误: {last_error}")
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """添加文档到向量存储
        
        Args:
            documents: 文档列表，每个文档是一个字典，包含'id', 'content'和其他元数据
        """
        if not documents:
            return
            
        try:
            ids = [str(doc['id']) for doc in documents]
            contents = [doc['content'] for doc in documents]
            metadatas = [{k: v for k, v in doc.items() if k != 'content'} for doc in documents]
            
            # 添加到ChromaDB
            self.collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas
            )
            
            print(f"已添加 {len(documents)} 个文档到向量存储")
        except Exception as e:
            print(f"添加文档失败: {e}")
            print(traceback.format_exc())
            # 不抛出异常，让应用继续运行
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """基于查询进行相似性搜索
        
        Args:
            query: 查询文本
            k: 返回的最相似文档数量
            
        Returns:
            最相似的k个文档列表
        """
        try:
            if self.collection.count() == 0:
                return []
                
            # 执行查询
            results = self.collection.query(
                query_texts=[query],
                n_results=min(k, self.collection.count())
            )
            
            # 格式化结果
            documents = []
            for i in range(len(results['documents'][0])):
                doc = {
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'similarity': 1.0 - (results['distances'][0][i] if 'distances' in results else 0)
                }
                
                # 添加元数据
                if 'metadatas' in results and results['metadatas'][0]:
                    doc.update(results['metadatas'][0][i])
                    
                documents.append(doc)
                
            return documents
        except Exception as e:
            print(f"相似性搜索失败: {e}")
            print(traceback.format_exc())
            return []
    
    def delete_document(self, doc_id: str):
        """删除文档
        
        Args:
            doc_id: 文档ID
        """
        try:
            self.collection.delete(ids=[doc_id])
            print(f"已删除文档 ID: {doc_id}")
        except Exception as e:
            print(f"删除文档失败: {e}")
            # 不抛出异常，让应用继续运行
    
    def update_document(self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """更新文档
        
        Args:
            doc_id: 文档ID
            content: 新的文档内容
            metadata: 新的元数据
        """
        try:
            self.collection.update(
                ids=[doc_id],
                documents=[content],
                metadatas=[metadata] if metadata else None
            )
            print(f"已更新文档 ID: {doc_id}")
        except Exception as e:
            print(f"更新文档失败: {e}")
            # 不抛出异常，让应用继续运行
    
    def clear(self):
        """清空向量存储"""
        try:
            # 获取当前集合名称
            collection_name = self.collection.name
            
            # 删除集合
            self.client.delete_collection(collection_name)
            
            # 重新创建集合
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            print(f"向量存储已清空并重新创建: {collection_name}")
        except Exception as e:
            print(f"清空向量存储失败: {e}")
            # 不抛出异常，让应用继续运行 