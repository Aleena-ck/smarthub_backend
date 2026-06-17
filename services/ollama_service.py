# services/ollama_service.py

import httpx
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))  # Increased to 2 minutes
OLLAMA_CONNECT_TIMEOUT = int(os.getenv("OLLAMA_CONNECT_TIMEOUT", "10"))

class OllamaService:
    """Service for interacting with Ollama LLM"""
    
    def __init__(self):
        self.base_url = OLLAMA_HOST
        self.model = OLLAMA_MODEL
        self.timeout = OLLAMA_TIMEOUT
        self.connect_timeout = OLLAMA_CONNECT_TIMEOUT
    
    async def generate(self, prompt: str, context: str = None) -> str:
        """Generate a response from the LLM"""
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\n\nUser: {prompt}\n\nAssistant:"
        
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(
                    self.timeout,           # Overall timeout
                    connect=self.connect_timeout  # Connection timeout
                )
            ) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": False,
                        "options": {
                            "num_predict": 512,  # Limit response length for speed
                            "temperature": 0.7,
                        }
                    },
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "No response from AI")
                else:
                    return "AI service is temporarily unavailable. Please try again later."
                    
        except httpx.TimeoutException:
            return "The AI service is taking too long to respond. Please try again."
        except Exception as e:
            return f"Unable to connect to AI service. Error: {str(e)}"
    
    async def generate_stream(self, prompt: str, context: str = None):
        """Stream response token by token (faster perceived performance)"""
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\n\nUser: {prompt}\n\nAssistant:"
        
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": True,
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            yield data.get("response", "")
        except Exception as e:
            yield f"Error: {str(e)}"
    
    async def analyze_document(self, content: str, prompt: str) -> str:
        """Analyze document content with the LLM"""
        # Truncate long documents
        max_chars = 4000
        truncated_content = content[:max_chars]
        if len(content) > max_chars:
            truncated_content += "\n...[document truncated]"
            
        full_prompt = f"Document content:\n{truncated_content}\n\nUser request: {prompt}\n\nPlease analyze the document and respond to the user's request."
        
        return await self.generate(full_prompt)