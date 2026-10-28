from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
from .models import Document
from .rag_service import RAGService
from .chroma_store import ChromaStore
from .ollama_service import OllamaService

# 延迟初始化服务
vector_store = None
ollama_service = None
rag_service = None

def get_services():
    """懒加载初始化服务"""
    global vector_store, ollama_service, rag_service
    if vector_store is None:
        try:
            # 首先尝试正常初始化
            vector_store = ChromaStore(force_recreate=False)
        except Exception as e:
            print(f"正常初始化ChromaStore失败，尝试强制重新创建: {e}")
            try:
                # 如果失败，尝试强制重新创建
                vector_store = ChromaStore(force_recreate=True)
            except Exception as e2:
                print(f"强制重新创建ChromaStore也失败: {e2}")
                # 使用一个空的向量存储，只依赖备用方案
                class DummyStore:
                    def similarity_search(self, *args, **kwargs):
                        return []
                    def add_documents(self, *args, **kwargs):
                        pass
                    def delete_document(self, *args, **kwargs):
                        pass
                    def update_document(self, *args, **kwargs):
                        pass
                    def clear(self, *args, **kwargs):
                        pass
                vector_store = DummyStore()
                
        ollama_service = OllamaService()
        rag_service = RAGService(vector_store=vector_store, ollama_service=ollama_service)
    return vector_store, ollama_service, rag_service

@login_required
def knowledge_base_view(request):
    """手语知识库前端页面"""
    documents = Document.objects.all().order_by('-updated_at')
    return render(request, 'agent/knowledge_base.html', {'documents': documents})

@csrf_exempt
@require_http_methods(["POST"])
def query_knowledge_base(request):
    """查询知识库API"""
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
        use_rag = data.get('use_rag', True)
        temperature = float(data.get('temperature', 0.7))

        if not query:
            return JsonResponse({'error': 'Query is required'}, status=400)

        # 获取服务实例
        try:
            _, ollama_service, rag_service = get_services()
        except Exception as e:
            import traceback
            print(f"服务初始化失败: {str(e)}")
            print(traceback.format_exc())
            
            # 备用方案：直接使用Ollama服务
            try:
                print("使用备用方案：直接查询Ollama")
                backup_ollama = OllamaService()
                response = backup_ollama.generate(
                    prompt=query,
                    model="qwen2.5:1.5b",
                    system_prompt="你是一个手语知识专家，请回答用户的问题。",
                    temperature=temperature
                )
                return JsonResponse({
                    "answer": response["text"],
                    "source": "backup_direct"
                })
            except Exception as e2:
                print(f"备用方案也失败: {str(e2)}")
                return JsonResponse({'error': f'服务初始化失败，备用方案也失败: {str(e)}'}, status=500)
        
        # 执行查询
        try:
            if use_rag:
                # 检查是否有文档
                docs_count = Document.objects.count()
                if docs_count == 0:
                    # 如果没有文档，使用直接查询
                    print("知识库为空，使用直接查询")
                    result = rag_service.direct_query(query, temperature=temperature)
                else:
                    try:
                        result = rag_service.query(query, temperature=temperature)
                    except Exception as e:
                        print(f"RAG查询失败，回退到直接查询: {str(e)}")
                        result = rag_service.direct_query(query, temperature=temperature)
            else:
                result = rag_service.direct_query(query, temperature=temperature)
            
            return JsonResponse(result)
        except Exception as e:
            import traceback
            print(f"查询执行失败: {str(e)}")
            print(traceback.format_exc())
            
            # 最后的备用方案
            try:
                print("使用最后的备用方案：简单关键词匹配")
                # 简单的关键词匹配
                documents = Document.objects.all()
                matched_docs = []
                
                for doc in documents:
                    # 简单计算相似度（关键词匹配）
                    query_words = set(query.lower().split())
                    content_words = set(doc.content.lower().split())
                    title_words = set(doc.title.lower().split())
                    
                    # 计算重叠词的数量
                    content_overlap = len(query_words.intersection(content_words))
                    title_overlap = len(query_words.intersection(title_words))
                    
                    # 如果有重叠，添加到匹配文档
                    if content_overlap > 0 or title_overlap > 0:
                        similarity = (content_overlap + title_overlap * 2) / len(query_words) if query_words else 0
                        matched_docs.append({
                            'id': doc.id,
                            'title': doc.title,
                            'content': doc.content,
                            'similarity': min(similarity, 1.0)  # 确保相似度不超过1
                        })
                
                # 按相似度排序
                matched_docs.sort(key=lambda x: x['similarity'], reverse=True)
                matched_docs = matched_docs[:3]  # 取前3个
                
                # 如果找到匹配文档，构建上下文
                if matched_docs:
                    context = "\n\n".join([f"文档: {doc['title']}\n内容: {doc['content']}" for doc in matched_docs])
                    prompt = f"""请基于以下文档回答问题:

{context}

问题: {query}
"""
                    backup_ollama = OllamaService()
                    response = backup_ollama.generate(
                        prompt=prompt,
                        model="qwen2.5:1.5b",
                        system_prompt="你是一个手语知识专家，请基于提供的文档回答用户的问题。",
                        temperature=temperature
                    )
                    
                    return JsonResponse({
                        "answer": response["text"],
                        "documents": matched_docs,
                        "source": "backup_rag"
                    })
                else:
                    # 没有匹配文档，直接查询
                    backup_ollama = OllamaService()
                    response = backup_ollama.generate(
                        prompt=query,
                        model="qwen2.5:1.5b",
                        system_prompt="你是一个手语知识专家，请回答用户的问题。",
                        temperature=temperature
                    )
                    
                    return JsonResponse({
                        "answer": response["text"],
                        "source": "backup_direct"
                    })
            except Exception as e3:
                print(f"所有备用方案都失败: {str(e3)}")
                return JsonResponse({'error': f'查询失败，所有备用方案都失败: {str(e)}'}, status=500)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        import traceback
        print(f"查询处理失败: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'error': f'查询处理失败: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_document(request, doc_id):
    """删除文档"""
    try:
        document = Document.objects.get(id=doc_id)
        document.delete()

        # 从向量存储中删除
        vector_store, _, _ = get_services()
        vector_store.delete_document(str(doc_id))

        return JsonResponse({'success': True})
    except Document.DoesNotExist:
        return JsonResponse({'error': 'Document not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
@login_required
def update_document(request, doc_id):
    """更新文档"""
    try:
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')

        document = Document.objects.get(id=doc_id)

        if title:
            document.title = title
        if content:
            document.content = content

        document.save()

        # 更新向量存储
        if content:
            vector_store, _, _ = get_services()
            vector_store.update_document(
                doc_id=str(document.id),
                content=document.content,
                metadata={'title': document.title}
            )

        return JsonResponse({'success': True})
    except Document.DoesNotExist:
        return JsonResponse({'error': 'Document not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def check_ollama_status(request):
    """检查Ollama服务状态"""
    _, ollama_service, _ = get_services()
    is_available = ollama_service.check_availability()
    return JsonResponse({'available': is_available})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def document_handler(request):
    """处理文档的GET和POST请求"""
    if request.method == "GET":
        # 获取所有文档
        try:
            documents = Document.objects.all().order_by('-updated_at')
            data = []
            for doc in documents:
                data.append({
                    'id': doc.id,
                    'title': doc.title,
                    'content': doc.content,
                    'created_at': doc.created_at.isoformat(),
                    'updated_at': doc.updated_at.isoformat()
                })
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    elif request.method == "POST":
        # 添加文档 - 开发环境中跳过认证检查
        # if not request.user.is_authenticated:
        #     return JsonResponse({'error': 'Authentication required'}, status=401)
            
        try:
            data = json.loads(request.body)
            title = data.get('title', '')
            content = data.get('content', '')

            if not title or not content:
                return JsonResponse({'error': 'Title and content are required'}, status=400)

            # 保存到数据库
            document = Document.objects.create(title=title, content=content)

            # 添加到向量存储
            _, _, rag_service = get_services()
            rag_service.add_documents([{
                'id': document.id,
                'title': title,
                'content': content
            }])

            return JsonResponse({'success': True, 'id': document.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
