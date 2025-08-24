import os
from typing import Optional
from ..llm_provider import LLMProvider

class CohereProvider(LLMProvider):
    """Cohere provider implementation using AsyncClientV2"""
    
    def _get_api_key(self, provided_key: Optional[str]) -> str:
        if provided_key is None:
            provided_key = os.environ.get("COHERE_API_KEY")
        if not provided_key:
            raise ValueError("API key not provided and COHERE_API_KEY environment variable not set")
        return provided_key
    
    def _initialize_client(self):
        try:
            import cohere
            self.client = cohere.AsyncClientV2(api_key=self.api_key)
        except ImportError:
            raise ImportError("cohere library not installed. Run: pip install cohere")
    
    async def chat(self, model: str, prompt: str, system_prompt: Optional[str] = None, streaming: bool = False) -> str:
        if streaming:
            return await self._chat_streaming(model, prompt, system_prompt)
        else:
            return await self._chat_sync(model, prompt, system_prompt)
    
    async def _chat_streaming(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        import cohere
        full_response = ""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat_stream(
            model=model,
            messages=messages,
        )
        
        async for event in response:
            if event.type == "content-delta":
                print(event.delta.message.content.text, end="", flush=True)
                full_response += event.delta.message.content.text
            elif event.type == "message-end":
                print()
        
        return full_response
    
    async def _chat_sync(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        import cohere
        
        messages = []
        if system_prompt:
            messages.append(cohere.SystemChatMessageV2(content=system_prompt))
        messages.append(cohere.UserChatMessageV2(content=prompt))
        
        response = await self.client.chat(
            model=model,
            messages=messages,
        )
        return response.message.content[0].text