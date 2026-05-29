import httpx
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

class OllamaService:
    """Service for interacting with Ollama LLM"""
    
    def __init__(self):
        self.base_url = OLLAMA_HOST
        self.model = OLLAMA_MODEL
    
    async def generate(self, prompt: str, context: str = None) -> str:
        """Generate a response from the LLM"""
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\n\nUser: {prompt}\n\nAssistant:"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": False
                    },
                    timeout=30.0
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
    
    async def analyze_document(self, content: str, prompt: str) -> str:
        """Analyze document content with the LLM"""
        full_prompt = f"Document content:\n{content[:4000]}\n\nUser request: {prompt}\n\nPlease analyze the document and respond to the user's request."
        
        return await self.generate(full_prompt)