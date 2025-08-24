import os
from typing import Optional
from google import genai
from ..llm_provider import LLMProvider

class GeminiProvider(LLMProvider):
    def _get_api_key(self, provided_key: Optional[str]) -> str:
        if provided_key is None:
            provided_key = os.environ.get("GEMINI_API_KEY")
        if not provided_key:
            raise ValueError("API key not provided and GEMINI_API_KEY environment variable not set")
        return provided_key
    
    def _initialize_client(self):
        self.client = genai.Client(api_key=self.api_key)
    
    async def chat(self, model: str, prompt: str, system_prompt: Optional[str] = None, streaming: bool = False) -> str:
        if streaming:
            return await self._chat_streaming(model, prompt, system_prompt)
        else:
            return await self._chat_sync(model, prompt, system_prompt)
    
    async def _chat_streaming(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        import asyncio
        full_response = ""
        
        def sync_streaming():
            result = ""
            contents = []
            if system_prompt:
                contents.append(system_prompt)
            contents.append(prompt)
            
            for chunk in self.client.models.generate_content_stream(
                model=model,
                contents=contents,
            ):
                if chunk.text:
                    print(chunk.text, end="", flush=True)
                    result += chunk.text
            return result
        
        full_response = await asyncio.to_thread(sync_streaming)
        return full_response
    
    async def _chat_sync(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        import asyncio
        
        def sync_chat():
            contents = []
            if system_prompt:
                contents.append(system_prompt)
            contents.append(prompt)
            
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
            )
            return response.text
        
        return await asyncio.to_thread(sync_chat)

async def conversar(modelo: str, pregunta: str, system_prompt: Optional[str] = None, streaming: bool = False, api_key: Optional[str] = None) -> str:
    client = GeminiProvider(api_key)
    return await client.chat(modelo, pregunta, system_prompt, streaming)
