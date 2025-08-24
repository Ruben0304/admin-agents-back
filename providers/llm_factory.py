from typing import Optional, Dict, Type
from .llm_provider import LLMProvider
from .google import GeminiProvider
from .cohere import CohereProvider

class LLMFactory:
    _providers: Dict[str, Type[LLMProvider]] = {
        "gemini": GeminiProvider,
        "cohere": CohereProvider,
    }
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]):
        """Register a new LLM provider"""
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(cls, provider_name: str, api_key: Optional[str] = None) -> LLMProvider:
        """Create an LLM provider instance"""
        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Provider '{provider_name}' not found. Available providers: {available}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(api_key=api_key)
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available provider names"""
        return list(cls._providers.keys())

async def chat_with_llm(
    provider_name: str, 
    model: str, 
    prompt: str, 
    system_prompt: Optional[str] = None,
    streaming: bool = False, 
    api_key: Optional[str] = None
) -> str:
    """Convenient function to chat with any LLM provider"""
    provider = LLMFactory.create_provider(provider_name, api_key)
    return await provider.chat(model, prompt, system_prompt, streaming)

async def main():
    # Ejemplo usando la factory
    print("Proveedores disponibles:", LLMFactory.get_available_providers())
    
    # Chat con Gemini
    response = await chat_with_llm("gemini", "gemini-2.5-pro", "Hola, ¿cómo estás?")
    print(f"Respuesta: {response}")
    
    # Chat con system prompt
    print("\nCon system prompt:")
    response_with_system = await chat_with_llm(
        "gemini", 
        "gemini-2.5-pro", 
        "¿Cuál es tu función?", 
        system_prompt="Eres un asistente especializado en programación."
    )
    print(f"Respuesta: {response_with_system}")
    
    # Chat con streaming
    print("\nCon streaming:")
    response_streaming = await chat_with_llm("gemini", "gemini-2.5-pro", "Cuéntame un chiste", streaming=True)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())