import requests
import json
from typing import Dict, Any, List, Optional

class OllamaService:
    """Ollama服务接口，用于与Ollama API交互"""
    
    def __init__(self, base_url="http://localhost:11434"):
        """初始化Ollama服务
        
        Args:
            base_url: Ollama API的基础URL
        """
        self.base_url = base_url
        self.generate_url = f"{base_url}/api/generate"
        self.embeddings_url = f"{base_url}/api/embeddings"
    
    def generate(self, 
                prompt: str, 
                model: str = "qwen2.5:1.5b", 
                system_prompt: Optional[str] = None,
                temperature: float = 0.7,
                max_tokens: int = 2000) -> Dict[str, Any]:
        """生成文本响应
        
        Args:
            prompt: 用户提示
            model: 使用的模型名称
            system_prompt: 系统提示
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成的token数量
            
        Returns:
            包含生成文本的字典
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        try:
            response = requests.post(self.generate_url, json=payload)
            response.raise_for_status()
            
            # Ollama返回的是JSONL格式，需要处理最后一行
            lines = response.text.strip().split('\n')
            last_line = json.loads(lines[-1])
            
            return {
                "text": last_line.get("response", ""),
                "model": model,
                "finish_reason": last_line.get("done", False)
            }
        except Exception as e:
            print(f"Ollama API调用失败: {e}")
            return {"text": f"生成失败: {str(e)}", "error": str(e)}
    
    def get_embeddings(self, text: str, model: str = "qwen2.5:1.5b") -> List[float]:
        """获取文本的嵌入向量
        
        Args:
            text: 需要嵌入的文本
            model: 使用的模型名称
            
        Returns:
            嵌入向量
        """
        payload = {
            "model": model,
            "prompt": text
        }
        
        try:
            response = requests.post(self.embeddings_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", [])
        except Exception as e:
            print(f"获取嵌入向量失败: {e}")
            return []
    
    def check_availability(self) -> bool:
        """检查Ollama服务是否可用
        
        Returns:
            服务是否可用
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False 