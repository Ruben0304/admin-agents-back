-- Migración para agregar soporte de proveedores dinámicos
-- Ejecutar en PostgreSQL

BEGIN;

-- Agregar nuevas columnas a la tabla providers
ALTER TABLE providers ADD COLUMN is_dynamic BOOLEAN DEFAULT false;
ALTER TABLE providers ADD COLUMN python_code TEXT;
ALTER TABLE providers ADD COLUMN required_dependencies JSON;
ALTER TABLE providers ADD COLUMN config_schema JSON;
ALTER TABLE providers ADD COLUMN validation_code TEXT;

-- Actualizar proveedores existentes para marcarlos como no dinámicos
UPDATE providers SET is_dynamic = false WHERE is_dynamic IS NULL;

-- Crear índice para mejorar el performance de consultas de proveedores dinámicos
CREATE INDEX idx_providers_is_dynamic ON providers(is_dynamic) WHERE is_dynamic = true;

-- Insertar algunos proveedores dinámicos de ejemplo (opcional)

-- Ejemplo: OpenAI Dynamic Provider
INSERT INTO providers (
    name, 
    display_name, 
    icon_url, 
    base_url, 
    is_active, 
    is_dynamic,
    python_code,
    config_schema,
    required_dependencies,
    validation_code,
    created_at
) VALUES (
    'openai_dynamic',
    'OpenAI (Dynamic)',
    'https://openai.com/favicon.ico',
    'https://api.openai.com/v1',
    true,
    true,
    'import asyncio
from typing import Optional
import openai

def _initialize_client():
    """Initialize the OpenAI client"""
    self.client = openai.OpenAI(api_key=api_key)

async def _chat_sync(model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
    """Synchronous chat with OpenAI"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    response = await asyncio.to_thread(
        self.client.chat.completions.create,
        model=model,
        messages=messages,
        max_tokens=max_tokens or 1000,
        temperature=temperature or 0.7
    )
    
    return response.choices[0].message.content

async def _chat_streaming(model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
    """Streaming chat with OpenAI"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    response = await asyncio.to_thread(
        self.client.chat.completions.create,
        model=model,
        messages=messages,
        max_tokens=max_tokens or 1000,
        temperature=temperature or 0.7,
        stream=True
    )
    
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content
    
    return full_response',
    '{
        "api_key": {
            "type": "string",
            "required": true,
            "description": "OpenAI API key"
        },
        "max_tokens": {
            "type": "integer",
            "default": 1000,
            "description": "Maximum tokens per response"
        },
        "temperature": {
            "type": "float",
            "default": 0.7,
            "description": "Sampling temperature"
        }
    }',
    '["openai"]',
    'def validate():
    """Validate OpenAI configuration"""
    if not api_key or not api_key.startswith(''sk-''):
        return False, ''Invalid OpenAI API key format''
    return True, ''Valid configuration''',
    NOW()
);

-- Ejemplo: Anthropic Dynamic Provider
INSERT INTO providers (
    name, 
    display_name, 
    icon_url, 
    base_url, 
    is_active, 
    is_dynamic,
    python_code,
    config_schema,
    required_dependencies,
    validation_code,
    created_at
) VALUES (
    'anthropic_dynamic',
    'Anthropic Claude (Dynamic)',
    'https://anthropic.com/favicon.ico',
    'https://api.anthropic.com/v1',
    true,
    true,
    'import asyncio
from typing import Optional
import anthropic

def _initialize_client():
    """Initialize the Anthropic client"""
    self.client = anthropic.AsyncAnthropic(api_key=api_key)

async def _chat_sync(model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
    """Synchronous chat with Anthropic Claude"""
    response = await self.client.messages.create(
        model=model,
        max_tokens=max_tokens or 1000,
        messages=[{"role": "user", "content": prompt}],
        system=system_prompt
    )
    
    return response.content[0].text

async def _chat_streaming(model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
    """Streaming chat with Anthropic Claude"""
    full_response = ""
    async with self.client.messages.stream(
        model=model,
        max_tokens=max_tokens or 1000,
        messages=[{"role": "user", "content": prompt}],
        system=system_prompt
    ) as stream:
        async for text in stream.text_stream:
            full_response += text
    
    return full_response',
    '{
        "api_key": {
            "type": "string",
            "required": true,
            "description": "Anthropic API key"
        },
        "max_tokens": {
            "type": "integer",
            "default": 1000,
            "description": "Maximum tokens per response"
        }
    }',
    '["anthropic"]',
    'def validate():
    """Validate Anthropic configuration"""
    if not api_key or not api_key.startswith(''sk-ant-''):
        return False, ''Invalid Anthropic API key format''
    return True, ''Valid configuration''',
    NOW()
);

-- Agregar algunos modelos de ejemplo para los proveedores dinámicos

-- Modelos OpenAI
INSERT INTO models (name, display_name, provider_id, max_tokens, supports_streaming, supports_system_prompt, cost_per_token, is_active, created_at)
SELECT 'gpt-3.5-turbo', 'GPT-3.5 Turbo', p.id, 4000, true, true, '$0.002/1K tokens', true, NOW()
FROM providers p WHERE p.name = 'openai_dynamic';

INSERT INTO models (name, display_name, provider_id, max_tokens, supports_streaming, supports_system_prompt, cost_per_token, is_active, created_at)
SELECT 'gpt-4', 'GPT-4', p.id, 8000, true, true, '$0.03/1K tokens', true, NOW()
FROM providers p WHERE p.name = 'openai_dynamic';

INSERT INTO models (name, display_name, provider_id, max_tokens, supports_streaming, supports_system_prompt, cost_per_token, is_active, created_at)
SELECT 'gpt-4-turbo', 'GPT-4 Turbo', p.id, 128000, true, true, '$0.01/1K tokens', true, NOW()
FROM providers p WHERE p.name = 'openai_dynamic';

-- Modelos Anthropic
INSERT INTO models (name, display_name, provider_id, max_tokens, supports_streaming, supports_system_prompt, cost_per_token, is_active, created_at)
SELECT 'claude-3-haiku-20240307', 'Claude 3 Haiku', p.id, 200000, true, true, '$0.25/1M tokens', true, NOW()
FROM providers p WHERE p.name = 'anthropic_dynamic';

INSERT INTO models (name, display_name, provider_id, max_tokens, supports_streaming, supports_system_prompt, cost_per_token, is_active, created_at)
SELECT 'claude-3-sonnet-20240229', 'Claude 3 Sonnet', p.id, 200000, true, true, '$3/1M tokens', true, NOW()
FROM providers p WHERE p.name = 'anthropic_dynamic';

INSERT INTO models (name, display_name, provider_id, max_tokens, supports_streaming, supports_system_prompt, cost_per_token, is_active, created_at)
SELECT 'claude-3-opus-20240229', 'Claude 3 Opus', p.id, 200000, true, true, '$15/1M tokens', true, NOW()
FROM providers p WHERE p.name = 'anthropic_dynamic';

COMMIT;

-- Verificar que las columnas se agregaron correctamente
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'providers' 
AND column_name IN ('is_dynamic', 'python_code', 'config_schema', 'required_dependencies', 'validation_code');

-- Verificar proveedores dinámicos insertados
SELECT id, name, display_name, is_dynamic, 
       CASE WHEN python_code IS NOT NULL THEN 'Present' ELSE 'NULL' END as code_status,
       CASE WHEN config_schema IS NOT NULL THEN 'Present' ELSE 'NULL' END as schema_status
FROM providers 
WHERE is_dynamic = true;

-- Verificar modelos para proveedores dinámicos
SELECT m.name as model_name, m.display_name, p.name as provider_name, p.display_name as provider_display
FROM models m
JOIN providers p ON m.provider_id = p.id
WHERE p.is_dynamic = true
ORDER BY p.name, m.name;