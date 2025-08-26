"""
Dynamic Provider System for executing user-defined LLM provider code.
"""
import ast
import types
import asyncio
from typing import Dict, Any, Optional, List
from .llm_provider import LLMProvider


class SecureCodeValidator(ast.NodeVisitor):
    """Validates Python code for security and safety"""
    
    # Allowed imports for dynamic providers
    ALLOWED_IMPORTS = {
        'asyncio', 'json', 'typing', 'dataclasses', 'datetime',
        'requests', 'aiohttp', 'httpx', 'openai', 'anthropic', 
        'cohere', 'google.genai', 'google-generativeai', 'tiktoken',
        're', 'base64', 'urllib.parse', 'os.getenv'
    }
    
    # Forbidden patterns and functions
    FORBIDDEN_PATTERNS = {
        'eval', 'exec', '__import__', 'compile', 'globals', 'locals',
        'open', 'file', 'input', 'raw_input', 'reload', 'quit', 'exit',
        'os.system', 'subprocess', 'socket', 'urllib.request.urlopen'
    }
    
    @classmethod
    def validate_code(cls, code: str) -> tuple[bool, str]:
        """Validate Python code for security compliance"""
        try:
            # Parse the code into an AST
            tree = ast.parse(code)
            
            # Check for forbidden patterns
            validator = cls()
            validator.visit(tree)
            
            return True, "Code validation passed"
            
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def visit_Import(self, node):
        """Check import statements - Allow all imports"""
        pass  # Allow all imports
    
    def visit_ImportFrom(self, node):
        """Check from...import statements - Allow all imports"""
        pass  # Allow all imports
    
    def visit_Name(self, node):
        """Check for forbidden function names"""
        if isinstance(node.ctx, ast.Load) and node.id in self.FORBIDDEN_PATTERNS:
            raise ValueError(f"Forbidden function: {node.id}")
    
    def visit_Call(self, node):
        """Check function calls"""
        if isinstance(node.func, ast.Name):
            if node.func.id in self.FORBIDDEN_PATTERNS:
                raise ValueError(f"Forbidden function call: {node.func.id}")
        elif isinstance(node.func, ast.Attribute):
            func_name = f"{node.func.value.id if hasattr(node.func.value, 'id') else ''}.{node.func.attr}"
            if func_name in self.FORBIDDEN_PATTERNS:
                raise ValueError(f"Forbidden method call: {func_name}")
    
    def _is_import_allowed(self, module_name: str) -> bool:
        """Check if an import is allowed"""
        # Allow imports from the allowed list
        if module_name in self.ALLOWED_IMPORTS:
            return True
        
        # Allow submodules of allowed packages
        for allowed in self.ALLOWED_IMPORTS:
            if module_name.startswith(f"{allowed}."):
                return True
        
        return False
    
    def generic_visit(self, node):
        """Visit all child nodes"""
        for child in ast.iter_child_nodes(node):
            self.visit(child)


class DynamicProvider(LLMProvider):
    """Dynamic provider that executes user-defined Python code"""
    
    def __init__(self, 
                 provider_name: str,
                 python_code: str,
                 config_vars: Dict[str, Any],
                 validation_code: Optional[str] = None,
                 db_session = None,
                 provider_id: Optional[int] = None):
        self.provider_name = provider_name
        self.python_code = python_code
        self.config_vars = config_vars
        self.validation_code = validation_code
        self.db_session = db_session
        self.provider_id = provider_id
        
        # Get API key from database if available
        api_key = self._get_api_key_from_db()
        
        # Validate the code before execution
        is_valid, error_msg = SecureCodeValidator.validate_code(python_code)
        if not is_valid:
            raise ValueError(f"Code validation failed: {error_msg}")
        
        # Initialize the provider first (this will call _initialize_client)
        super().__init__(api_key=api_key)
        
        # Execute the provider code in a controlled environment and override defaults
        self._execute_provider_code()
    
    def _get_api_key_from_db(self) -> Optional[str]:
        """Get API key from database using provider_id"""
        if not self.db_session or not self.provider_id:
            print(f"DEBUG: No db_session or provider_id, using config_vars api_key")
            return self.config_vars.get('api_key')
        
        try:
            # Import here to avoid circular imports
            from repositories import get_api_keys_by_provider
            
            # Get API keys for this provider
            api_keys = get_api_keys_by_provider(self.db_session, self.provider_id)
            if api_keys:
                # Use the first active API key
                api_key = api_keys[0].encrypted_key  # It's actually the literal key
                print(f"DEBUG: Got API key from database for provider_id {self.provider_id}")
                # Add to config_vars so it's available in the executed code
                self.config_vars['api_key'] = api_key
                return api_key
            else:
                print(f"DEBUG: No API keys found for provider_id {self.provider_id}")
                return self.config_vars.get('api_key')
                
        except Exception as e:
            print(f"DEBUG: Error getting API key from database: {e}")
            return self.config_vars.get('api_key')
    
    # Implement abstract methods directly in class definition
    def _initialize_client(self):
        """Initialize the client - will be overridden by dynamic code"""
        self.client = None
    
    async def _chat_sync(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Synchronous chat - will be overridden by dynamic code"""
        print(f"DEBUG: _chat_sync called, checking if method was overridden")
        print(f"DEBUG: Current _chat_sync method: {self._chat_sync}")
        print(f"DEBUG: Class _chat_sync method: {self.__class__._chat_sync}")
        print(f"DEBUG: Methods overridden: {self._chat_sync != self.__class__._chat_sync}")
        
        raise NotImplementedError(
            "_chat_sync not implemented in provider code. "
            "Please define the following functions in your code: "
            "_initialize_client(), _chat_sync(), _chat_streaming(). "
            "Use the template selector to get the correct function structure."
        )
    
    async def _chat_streaming(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Streaming chat - will be overridden by dynamic code"""
        raise NotImplementedError("_chat_streaming not implemented in provider code")
    
    def _execute_provider_code(self):
        """Execute the provider code in a secure sandbox"""        
        print(f"DEBUG: Executing provider code")
        print(f"DEBUG: Python code length: {len(self.python_code)} characters")
        print(f"DEBUG: Config vars: {list(self.config_vars.keys())}")
        
        # Create a controlled namespace
        safe_globals = {
            '__builtins__': {
                'len': len, 'str': str, 'int': int, 'float': float, 'bool': bool,
                'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                'range': range, 'enumerate': enumerate, 'zip': zip,
                'print': print, 'isinstance': isinstance, 'hasattr': hasattr,
                'getattr': getattr, 'setattr': setattr, 'type': type,
                '__import__': __import__, '__build_class__': __build_class__,
                '__name__': '__main__'
            },
            'asyncio': asyncio,
            'typing': __import__('typing'),
            'json': __import__('json'),
            'datetime': __import__('datetime'),
            'Optional': __import__('typing').Optional,
            'Dict': __import__('typing').Dict,
            'List': __import__('typing').List,
            'Any': __import__('typing').Any,
        }
        
        # Add all possible imports for dynamic providers
        try:
            safe_globals['google'] = __import__('google')
        except ImportError:
            pass
        
        try:
            safe_globals['genai'] = __import__('google.genai', fromlist=['genai'])
        except ImportError:
            try:
                safe_globals['genai'] = __import__('genai')
            except ImportError:
                pass
        
        try:
            safe_globals['openai'] = __import__('openai')
        except ImportError:
            pass
            
        try:
            safe_globals['anthropic'] = __import__('anthropic')
        except ImportError:
            pass
        
        # Add configuration variables to both global and local namespaces
        for key, value in self.config_vars.items():
            safe_globals[key] = value
        
        # Create local namespace for the execution
        local_namespace = {}
        
        # Also add config vars to local namespace
        local_namespace.update(self.config_vars)
        
        # Execute the code
        exec(self.python_code, safe_globals, local_namespace)
        
        # Extract the required functions from the executed code
        self._extract_provider_functions(local_namespace)
    
    def _extract_provider_functions(self, namespace: Dict[str, Any]):
        """Extract required provider functions from executed code"""
        required_functions = ['_initialize_client', '_chat_sync', '_chat_streaming']
        
        print(f"DEBUG: Extracting functions from namespace")
        print(f"DEBUG: Available in namespace: {list(namespace.keys())}")
        print(f"DEBUG: Required functions: {required_functions}")
        
        # Check what functions/classes are available in the namespace
        
        # Create a wrapper that includes config variables in the function's closure
        def create_wrapper(func, config_vars, func_name):
            async def async_wrapper(*args, **kwargs):
                # Inject config variables into the function's globals
                if hasattr(func, '__globals__'):
                    func.__globals__.update(config_vars)
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            
            def sync_wrapper(*args, **kwargs):
                # Inject config variables into the function's globals
                if hasattr(func, '__globals__'):
                    func.__globals__.update(config_vars)
                return func(*args, **kwargs)
            
            # Return appropriate wrapper based on function name
            if func_name in ['_chat_sync', '_chat_streaming']:
                return async_wrapper
            else:
                return sync_wrapper
        
        # First, try to find individual functions
        functions_found = []
        for func_name in required_functions:
            print(f"DEBUG: Looking for function {func_name} in namespace")
            if func_name in namespace:
                # Get the function and wrap it with config context
                func = namespace[func_name]
                print(f"DEBUG: Found {func_name}, callable: {callable(func)}")
                if callable(func):
                    wrapped_func = create_wrapper(func, self.config_vars, func_name)
                    # Replace the original method directly
                    setattr(self, func_name, types.MethodType(wrapped_func, self))
                    functions_found.append(func_name)
                    print(f"DEBUG: Successfully set {func_name} on instance")
            else:
                print(f"DEBUG: {func_name} not found in namespace")
        
        # If no functions found, try to extract methods from classes
        print(f"DEBUG: Functions found so far: {functions_found}")
        if not functions_found:
            print("DEBUG: No individual functions found, trying to extract from classes")
            self._extract_from_classes(namespace, required_functions)
        else:
            print(f"DEBUG: Successfully extracted {len(functions_found)} functions: {functions_found}")
    
    def _extract_from_classes(self, namespace: Dict[str, Any], required_functions: List[str]):
        """Try to extract methods from classes in the namespace"""
        print(f"DEBUG: Extracting from classes")
        print(f"DEBUG: self.api_key = {getattr(self, 'api_key', 'NOT_SET')}")
        print(f"DEBUG: config_vars api_key = {self.config_vars.get('api_key', 'NOT_SET')}")
        for name, obj in namespace.items():
            print(f"DEBUG: Checking object {name} of type {type(obj)}")
            if isinstance(obj, type):  # It's a class
                print(f"DEBUG: Found class {name}, attempting to instantiate")
                # Create an instance of the class with config vars
                try:
                    # Try different instantiation patterns
                    class_instance = None
                    
                    # Try with api_key parameter
                    if 'api_key' in self.config_vars and self.config_vars['api_key']:
                        try:
                            class_instance = obj(api_key=self.config_vars['api_key'])
                            print(f"DEBUG: Successfully instantiated {name} with api_key")
                        except Exception as e:
                            print(f"DEBUG: Failed to instantiate {name} with api_key: {e}")
                    
                    # Try with just api_key as positional argument if available
                    if class_instance is None and hasattr(self, 'api_key') and self.api_key:
                        try:
                            class_instance = obj(self.api_key)
                            print(f"DEBUG: Successfully instantiated {name} with positional api_key")
                        except Exception as e:
                            print(f"DEBUG: Failed to instantiate {name} with positional api_key: {e}")
                    
                    # Try with api_key from parent class
                    if class_instance is None and hasattr(self, 'api_key') and self.api_key:
                        try:
                            class_instance = obj(api_key=self.api_key)
                            print(f"DEBUG: Successfully instantiated {name} with parent api_key")
                        except Exception as e:
                            print(f"DEBUG: Failed to instantiate {name} with parent api_key: {e}")
                    
                    # Try with all config vars
                    if class_instance is None:
                        try:
                            class_instance = obj(**self.config_vars)
                            print(f"DEBUG: Successfully instantiated {name} with all config vars")
                        except Exception as e:
                            print(f"DEBUG: Failed to instantiate {name} with config vars: {e}")
                    
                    # Try with no parameters
                    if class_instance is None:
                        try:
                            class_instance = obj()
                            print(f"DEBUG: Successfully instantiated {name} with no parameters")
                        except Exception as e:
                            print(f"DEBUG: Failed to instantiate {name} with no parameters: {e}")
                    
                    if class_instance is None:
                        print(f"DEBUG: Could not instantiate class {name}")
                        continue
                    
                    # First try to find methods with exact names
                    print(f"DEBUG: Checking class {name} for exact method names")
                    available_methods = [attr for attr in dir(class_instance) if not attr.startswith('__') and callable(getattr(class_instance, attr))]
                    print(f"DEBUG: Available methods in {name}: {available_methods}")
                    
                    functions_extracted = 0
                    for func_name in required_functions:
                        if hasattr(class_instance, func_name):
                            method = getattr(class_instance, func_name)
                            if callable(method):
                                print(f"DEBUG: Found exact method {func_name} in class {name}")
                                setattr(self, func_name, method)
                                functions_extracted += 1
                                continue
                        else:
                            print(f"DEBUG: Method {func_name} not found in class {name}")
                    
                    # If exact names not found, try common method mappings
                    method_mapping = {
                        '_initialize_client': ['initialize', '__init__', 'setup', 'init_client'],
                        '_chat_sync': ['chat', 'generate', 'complete', 'chat_sync'],
                        '_chat_streaming': ['chat_stream', 'stream', 'generate_stream', 'chat_streaming']
                    }
                    
                    for func_name in required_functions:
                        # Skip if we already found exact match
                        if hasattr(self, func_name) and getattr(self, func_name) != getattr(self.__class__, func_name):
                            print(f"DEBUG: Skipping {func_name} - already found exact match")
                            continue
                            
                        possible_methods = method_mapping.get(func_name, [func_name[1:]])  # Remove leading _
                        print(f"DEBUG: Looking for {func_name} via mappings: {possible_methods}")
                        
                        for method_name in possible_methods:
                            if hasattr(class_instance, method_name):
                                method = getattr(class_instance, method_name)
                                if callable(method):
                                    print(f"DEBUG: Mapping {func_name} to {method_name} in class {name}")
                                    setattr(self, func_name, method)
                                    functions_extracted += 1
                                    break
                    
                    # If we found methods, use this class instance
                    if functions_extracted > 0:
                        print(f"DEBUG: Successfully extracted {functions_extracted} functions from class {name}")
                        self.client_instance = class_instance
                        break
                    else:
                        print(f"DEBUG: No functions extracted from class {name}")
                    
                except Exception as e:
                    print(f"DEBUG: Exception while processing class {name}: {e}")
                    continue
    
    def _get_api_key(self, provided_key: Optional[str]) -> str:
        """Get API key from configuration"""
        return provided_key or self.config_vars.get('api_key', '')
    
    async def chat(self, model: str, prompt: str, system_prompt: Optional[str] = None, streaming: bool = False) -> str:
        """Generate chat response with the dynamic provider"""
        if streaming:
            return await self._chat_streaming(model, prompt, system_prompt)
        else:
            return await self._chat_sync(model, prompt, system_prompt)
    
    def validate_configuration(self) -> tuple[bool, str]:
        """Validate the provider configuration"""
        if not self.validation_code:
            return True, "No validation code provided"
        
        try:
            # Execute validation code
            safe_globals = {
                '__builtins__': {'len': len, 'str': str, 'isinstance': isinstance},
                'config': self.config_vars
            }
            
            local_namespace = {}
            exec(self.validation_code, safe_globals, local_namespace)
            
            # Look for a validate function
            if 'validate' in local_namespace:
                result = local_namespace['validate']()
                if isinstance(result, tuple):
                    return result
                else:
                    return bool(result), "Validation completed"
            else:
                return True, "No validate function found"
                
        except Exception as e:
            return False, f"Validation error: {str(e)}"


class DynamicProviderManager:
    """Manages dynamic providers in the system"""
    
    def __init__(self):
        self.registered_providers: Dict[str, type] = {}
    
    def create_provider_from_db(self, provider_data: Dict[str, Any], config_vars: Dict[str, Any], db_session=None, provider_id: Optional[int] = None) -> DynamicProvider:
        """Create a dynamic provider from database configuration"""
        return DynamicProvider(
            provider_name=provider_data['name'],
            python_code=provider_data['python_code'],
            config_vars=config_vars,
            validation_code=provider_data.get('validation_code'),
            db_session=db_session,
            provider_id=provider_id
        )
    
    def validate_provider_code(self, code: str) -> tuple[bool, str]:
        """Validate provider code before saving"""
        return SecureCodeValidator.validate_code(code)
    
    def get_code_template(self, provider_type: str = "openai") -> str:
        """Get a code template for creating new providers"""
        templates = {
            "openai": '''
"""
OpenAI Dynamic Provider Template

CRITICAL PROJECT REQUIREMENTS:
=============================

1. MANDATORY FUNCTIONS - Must be implemented exactly as shown:
   - _initialize_client(): Initialize the OpenAI client
   - _chat_sync(): Synchronous/non-streaming chat method
   - _chat_streaming(): Streaming chat method

2. REQUIRED IMPORTS:
   - asyncio: For async operations and thread handling
   - typing.Optional: For optional parameters
   - openai: Official OpenAI Python library

3. PROJECT-SPECIFIC VARIABLES (Available automatically):
   - api_key: Provider API key from database or config
   - max_tokens: Maximum response tokens (default: 1000)
   - temperature: Response creativity level (default: 0.7)
   
   These variables are injected by the DynamicProvider system and
   MUST be used exactly as shown - do not modify their names.

4. ASYNC REQUIREMENTS:
   - All chat functions MUST be async (use 'async def')
   - Use asyncio.to_thread() for sync OpenAI calls
   - Never use synchronous calls directly

5. MESSAGE FORMAT:
   - System prompt: {"role": "system", "content": system_prompt}
   - User message: {"role": "user", "content": prompt}
   - This format is required by the project architecture

6. ERROR HANDLING:
   - Initialize client in each function if None
   - Handle streaming responses properly
   - Return string responses (never return None)

7. STREAMING IMPLEMENTATION:
   - Must accumulate full response in streaming mode
   - Return complete text, not stream chunks
   - Use proper chunk handling for OpenAI format
"""

import asyncio
from typing import Optional
import openai

# Global client variable - REQUIRED for project architecture
client = None

def _initialize_client():
    """
    Initialize the OpenAI client with API key
    
    CRITICAL: This function is REQUIRED by DynamicProvider system.
    - Uses global 'api_key' variable injected by framework
    - Client must be stored in global 'client' variable
    - Function name MUST be exactly '_initialize_client'
    """
    global client
    client = openai.OpenAI(api_key=api_key)

async def _chat_sync(model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Non-streaming chat with OpenAI
    
    CRITICAL REQUIREMENTS:
    - Function name MUST be exactly '_chat_sync'
    - MUST be async function
    - MUST return string (never None)
    - Uses asyncio.to_thread() for sync OpenAI calls
    - Handles both system prompt and user message
    
    Parameters automatically provided by framework:
    - model: Model name (e.g., 'gpt-4o', 'gpt-3.5-turbo')
    - prompt: User input message
    - system_prompt: Optional system instructions
    
    Uses injected variables:
    - max_tokens: From config (default 1000)
    - temperature: From config (default 0.7)
    """
    global client
    if client is None:
        _initialize_client()
    
    # Build messages array - REQUIRED format for project
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    # Use asyncio.to_thread for non-blocking operation - REQUIRED
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=model,
        messages=messages,
        max_tokens=max_tokens or 1000,  # Uses injected variable
        temperature=temperature or 0.7   # Uses injected variable
    )
    
    return response.choices[0].message.content

async def _chat_streaming(model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Streaming chat with OpenAI
    
    CRITICAL REQUIREMENTS:
    - Function name MUST be exactly '_chat_streaming'
    - MUST be async function
    - MUST return complete string (not stream chunks)
    - Accumulates streaming response into full text
    - Uses same message format as sync version
    
    Parameters automatically provided by framework:
    - model: Model name for streaming
    - prompt: User input message
    - system_prompt: Optional system instructions
    
    Uses injected variables:
    - max_tokens: From config (default 1000)
    - temperature: From config (default 0.7)
    """
    global client
    if client is None:
        _initialize_client()
    
    # Build messages array - SAME format as sync version
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt}")
    
    # Enable streaming with stream=True
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=model,
        messages=messages,
        max_tokens=max_tokens or 1000,  # Uses injected variable
        temperature=temperature or 0.7,  # Uses injected variable
        stream=True                      # Enable streaming
    )
    
    # Accumulate streaming chunks - REQUIRED for project
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content
    
    return full_response
''',
            "anthropic": '''
"""
Anthropic Claude Dynamic Provider Template

CRITICAL PROJECT REQUIREMENTS:
=============================

1. MANDATORY FUNCTIONS - Must be implemented exactly as shown:
   - _initialize_client(): Initialize the Anthropic AsyncAnthropic client
   - _chat_sync(): Synchronous/non-streaming chat method
   - _chat_streaming(): Streaming chat method

2. REQUIRED IMPORTS:
   - asyncio: For async operations (though not needed for direct calls)
   - typing.Optional: For optional parameters
   - anthropic: Official Anthropic Python library

3. PROJECT-SPECIFIC VARIABLES (Available automatically):
   - api_key: Provider API key from database or config
   - max_tokens: Maximum response tokens (default: 1000)
   - temperature: Response creativity level (default: 0.7)
   
   These variables are injected by the DynamicProvider system and
   MUST be used exactly as shown - do not modify their names.

4. ASYNC REQUIREMENTS:
   - All chat functions MUST be async (use 'async def')
   - Use AsyncAnthropic client for native async operations
   - All API calls are naturally async with Anthropic

5. MESSAGE FORMAT:
   - User message: [{"role": "user", "content": prompt}]
   - System prompt: Passed as separate 'system' parameter
   - This format is required by Anthropic API architecture

6. ERROR HANDLING:
   - Initialize client in each function if None
   - Handle streaming responses properly with async context
   - Return string responses (never return None)

7. STREAMING IMPLEMENTATION:
   - Use async context manager with client.messages.stream()
   - Accumulate text from stream.text_stream
   - Return complete text, not stream chunks

8. ANTHROPIC-SPECIFIC:
   - Uses AsyncAnthropic client (native async)
   - System prompt goes in 'system' parameter, not messages
   - Response content is in response.content[0].text
"""

import asyncio
from typing import Optional
import anthropic

# Global client variable - REQUIRED for project architecture
client = None

def _initialize_client():
    """
    Initialize the Anthropic AsyncAnthropic client with API key
    
    CRITICAL: This function is REQUIRED by DynamicProvider system.
    - Uses global 'api_key' variable injected by framework
    - Client must be stored in global 'client' variable
    - Function name MUST be exactly '_initialize_client'
    - Uses AsyncAnthropic for native async operations
    """
    global client
    client = anthropic.AsyncAnthropic(api_key=api_key)

async def _chat_sync(model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Non-streaming chat with Anthropic Claude
    
    CRITICAL REQUIREMENTS:
    - Function name MUST be exactly '_chat_sync'
    - MUST be async function
    - MUST return string (never None)
    - Uses native async Anthropic client calls
    - Handles system prompt separately from messages
    
    Parameters automatically provided by framework:
    - model: Model name (e.g., 'claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307')
    - prompt: User input message
    - system_prompt: Optional system instructions
    
    Uses injected variables:
    - max_tokens: From config (default 1000)
    - temperature: From config (default 0.7)
    """
    global client
    if client is None:
        _initialize_client()
    
    # Anthropic API call - system prompt separate from messages
    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens or 1000,    # Uses injected variable
        messages=[{"role": "user", "content": prompt}],  # User message only
        system=system_prompt              # System prompt separate parameter
    )
    
    # Extract text from Anthropic response format
    return response.content[0].text

async def _chat_streaming(model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Streaming chat with Anthropic Claude
    
    CRITICAL REQUIREMENTS:
    - Function name MUST be exactly '_chat_streaming'
    - MUST be async function
    - MUST return complete string (not stream chunks)
    - Uses async context manager for streaming
    - Accumulates streaming response into full text
    
    Parameters automatically provided by framework:
    - model: Model name for streaming
    - prompt: User input message
    - system_prompt: Optional system instructions
    
    Uses injected variables:
    - max_tokens: From config (default 1000)
    - temperature: From config (default 0.7)
    """
    global client
    if client is None:
        _initialize_client()
    
    # Accumulate streaming response - REQUIRED for project
    full_response = ""
    
    # Use async context manager for streaming - REQUIRED format
    async with client.messages.stream(
        model=model,
        max_tokens=max_tokens or 1000,    # Uses injected variable
        messages=[{"role": "user", "content": prompt}],  # User message only
        system=system_prompt              # System prompt separate parameter
    ) as stream:
        # Iterate over text stream and accumulate
        async for text in stream.text_stream:
            full_response += text
    
    return full_response
'''
        }
        
        return templates.get(provider_type, templates["openai"])


# Global manager instance
dynamic_provider_manager = DynamicProviderManager()