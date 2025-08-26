from typing import Optional, Dict, Type, Any
from .llm_provider import LLMProvider
from .google import GeminiProvider
from .cohere import CohereProvider
from .dynamic_provider import DynamicProvider, dynamic_provider_manager

class LLMFactory:
    _providers: Dict[str, Type[LLMProvider]] = {
        "gemini": GeminiProvider,
        "cohere": CohereProvider,
    }
    
    # Store dynamic provider configurations
    _dynamic_providers: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]):
        """Register a new LLM provider"""
        cls._providers[name] = provider_class
    
    @classmethod
    def register_dynamic_provider(cls, name: str, provider_config: Dict[str, Any]):
        """Register a dynamic provider configuration"""
        cls._dynamic_providers[name] = provider_config
    
    @classmethod
    def create_provider(cls, provider_name: str, api_key: Optional[str] = None, config_vars: Optional[Dict[str, Any]] = None, db_session=None) -> LLMProvider:
        """Create an LLM provider instance (static or dynamic)"""
        
        # Check if it's a dynamic provider
        if provider_name in cls._dynamic_providers:
            provider_config = cls._dynamic_providers[provider_name]
            
            # Merge API key and config variables
            merged_config = config_vars.copy() if config_vars else {}
            if api_key:
                merged_config['api_key'] = api_key
            
            # Get provider_id from database if db_session is provided
            provider_id = None
            if db_session:
                try:
                    from repositories import get_provider_by_name
                    provider = get_provider_by_name(db_session, provider_name)
                    if provider:
                        provider_id = provider.id
                        print(f"DEBUG: Found provider_id {provider_id} for registered dynamic provider {provider_name}")
                except Exception as e:
                    print(f"DEBUG: Could not get provider_id for registered provider: {e}")
            
            return dynamic_provider_manager.create_provider_from_db(
                provider_config, 
                merged_config,
                db_session=db_session,
                provider_id=provider_id
            )
        
        # Check static providers
        if provider_name not in cls._providers:
            available_static = ", ".join(cls._providers.keys())
            available_dynamic = ", ".join(cls._dynamic_providers.keys())
            available = f"Static: {available_static}; Dynamic: {available_dynamic}"
            raise ValueError(f"Provider '{provider_name}' not found. Available providers: {available}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(api_key=api_key)
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available provider names (static and dynamic)"""
        static_providers = list(cls._providers.keys())
        dynamic_providers = list(cls._dynamic_providers.keys())
        return static_providers + dynamic_providers
    
    @classmethod
    def load_dynamic_providers_from_db(cls, db_session):
        """Load dynamic providers from database at startup"""
        from repositories import get_all_providers
        
        providers = get_all_providers(db_session)
        for provider in providers:
            if provider.is_dynamic and provider.is_active:
                cls.register_dynamic_provider(provider.name, {
                    'name': provider.name,
                    'display_name': provider.display_name,
                    'python_code': provider.python_code,
                    'config_schema': provider.config_schema,
                    'required_dependencies': provider.required_dependencies,
                    'validation_code': provider.validation_code,
                })
    
    @classmethod
    def validate_dynamic_provider_code(cls, code: str) -> tuple[bool, str]:
        """Validate dynamic provider code"""
        return dynamic_provider_manager.validate_provider_code(code)
    
    @classmethod
    def get_code_template(cls, provider_type: str = "openai") -> str:
        """Get code template for creating new providers"""
        return dynamic_provider_manager.get_code_template(provider_type)

async def chat_with_llm(
    provider_name: str, 
    model: str, 
    prompt: str, 
    system_prompt: Optional[str] = None,
    streaming: bool = False, 
    api_key: Optional[str] = None,
    config_vars: Optional[Dict[str, Any]] = None,
    db_session = None
) -> str:
    """Convenient function to chat with any LLM provider (static or dynamic)"""
    
    # If config_vars contains 'python_code', this is a dynamic provider
    if config_vars and 'python_code' in config_vars:
        # Create a dynamic provider directly
        merged_config = config_vars.copy()
        if api_key:
            merged_config['api_key'] = api_key
        
        # Get provider_id from database if db_session is provided
        provider_id = None
        if db_session:
            try:
                from repositories import get_provider_by_name
                provider = get_provider_by_name(db_session, provider_name)
                if provider:
                    provider_id = provider.id
                    print(f"DEBUG: Found provider_id {provider_id} for provider {provider_name}")
            except Exception as e:
                print(f"DEBUG: Could not get provider_id: {e}")
            
        provider_data = {
            "name": provider_name,
            "python_code": config_vars['python_code'],
            "validation_code": config_vars.get('validation_code')
        }
        
        provider = dynamic_provider_manager.create_provider_from_db(
            provider_data,
            merged_config,
            db_session=db_session,
            provider_id=provider_id
        )
        return await provider.chat(model, prompt, system_prompt, streaming)
    
    # Otherwise use the factory as normal (pass db_session for registered dynamic providers)
    provider = LLMFactory.create_provider(provider_name, api_key, config_vars, db_session)
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