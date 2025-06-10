"""
Core implementation of the Dynamic BAML library using real BoundaryML.
"""

import os
import tempfile
import uuid
import subprocess
import sys
import importlib.util
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from .exceptions import (
    DynamicBAMLError,
    SchemaGenerationError,
    BAMLCompilationError,
    LLMProviderError,
    ResponseParsingError,
)
from .types import SchemaDict, ResponseData, ProviderOptions, CallResult
from .schema_generator import DictToBAMLGenerator


def call_with_schema(
    prompt_text: str,
    schema_dict: SchemaDict,
    options: Optional[ProviderOptions] = None
) -> ResponseData:
    """
    Execute an LLM call with dynamic BAML schema generation and response parsing.
    
    This function:
    1. Generates BAML schema code from the dictionary
    2. Creates a temporary BAML project
    3. Generates the BAML client using baml-cli
    4. Imports and calls the generated function
    
    Args:
        prompt_text: The prompt to send to the LLM
        schema_dict: Dictionary defining the desired response structure
        options: Configuration options for LLM provider and model
        
    Returns:
        Structured data matching the input schema dictionary
        
    Raises:
        DynamicBAMLError: For any errors during processing
    """
    if options is None:
        options = {"provider": "ollama", "model": "gemma3:1b"}
    
    try:
        # Generate unique schema name
        schema_name = f"DynamicSchema_{uuid.uuid4().hex[:8]}"
        function_name = f"Extract{schema_name}"
        
        # Step 1: Generate BAML schema from dictionary
        generator = DictToBAMLGenerator()
        baml_code = generator.generate_schema(schema_dict, schema_name)
        
        # Step 2: Create BAML function for extraction
        client_config = _get_client_config(options)
        baml_function = _generate_baml_function(
            function_name, 
            schema_name, 
            client_config,
            prompt_text
        )
        
        full_baml_code = baml_code + "\n\n" + baml_function
        
        # Step 3: Create temporary BAML project and generate client
        with _temporary_baml_project(full_baml_code, function_name) as (project_dir, client_module):
            # Step 4: Call the generated function
            extract_function = getattr(client_module.b, function_name)
            result = extract_function(input_text=prompt_text)
            
            # Convert Pydantic model to dictionary
            if hasattr(result, 'model_dump'):
                return result.model_dump()
            elif hasattr(result, 'dict'):
                return result.dict()
            else:
                return dict(result)
        
    except Exception as e:
        if isinstance(e, DynamicBAMLError):
            raise
        else:
            raise DynamicBAMLError(f"Unexpected error: {str(e)}", "unknown") from e


def call_with_schema_safe(
    prompt_text: str,
    schema_dict: SchemaDict,
    options: Optional[ProviderOptions] = None
) -> CallResult:
    """
    Safe version of call_with_schema that returns structured results instead of raising.
    
    Args:
        prompt_text: The prompt to send to the LLM
        schema_dict: Dictionary defining the desired response structure
        options: Configuration options for LLM provider and model
        
    Returns:
        CallResult with success flag and either data or error information
    """
    try:
        data = call_with_schema(prompt_text, schema_dict, options)
        return {
            "success": True,
            "data": data
        }
    except DynamicBAMLError as e:
        return {
            "success": False,
            "error": e.message,
            "error_type": e.error_type
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": "unknown"
        }


def _get_client_config(options: ProviderOptions) -> str:
    """Generate BAML client configuration based on options."""
    provider = options.get("provider", "ollama").lower()
    
    if provider == "ollama":
        return "MyOllama"
    elif provider == "openai":
        return "MyOpenAI"
    elif provider == "anthropic":
        return "MyAnthropic"
    else:
        # Default to Ollama
        return "MyOllama"


def _generate_baml_function(function_name: str, schema_name: str, client_config: str, prompt_text: str) -> str:
    """Generate BAML function definition."""
    return f"""
function {function_name}(input_text: string) -> {schema_name} {{
  client {client_config}
  prompt #"
    {prompt_text}
    
    INPUT TEXT:
    ---
    {{{{ input_text }}}}
    ---
    
    {{{{ ctx.output_format }}}}
  "#
}}
"""


class _TemporaryBAMLProject:
    """Context manager for temporary BAML projects."""
    
    def __init__(self, baml_code: str, function_name: str):
        self.baml_code = baml_code
        self.function_name = function_name
        self.project_dir = None
        self.client_module = None
    
    def __enter__(self):
        # Create temporary directory
        self.project_dir = Path(tempfile.mkdtemp(prefix="dynamic_baml_"))
        
        try:
            # Create baml_src directory
            baml_src_dir = self.project_dir / "baml_src"
            baml_src_dir.mkdir()
            
            # Write the BAML code
            (baml_src_dir / "schema.baml").write_text(self.baml_code)
            
            # Write generators.baml
            generators_content = '''
generator target {
    output_type "python/pydantic"
    output_dir "../"
    version "0.89.0"
    default_client_mode sync
}
'''
            (baml_src_dir / "generators.baml").write_text(generators_content)
            
            # Write clients.baml (basic client configurations)
            clients_content = '''
client<llm> MyOllama {
  provider openai-generic
  options {
    model "gemma3:1b"
    base_url "http://localhost:11434/v1"
    api_key "dummy"
  }
}

client<llm> MyOpenAI {
  provider openai
  options {
    model "gpt-4o"
    api_key env.OPENAI_API_KEY
  }
}

client<llm> MyAnthropic {
  provider anthropic
  options {
    model "claude-3-5-sonnet-20241022"
    api_key env.ANTHROPIC_API_KEY
  }
}
'''
            (baml_src_dir / "clients.baml").write_text(clients_content)
            
            # Run baml-cli generate in the project directory
            result = subprocess.run(
                ["baml-cli", "generate"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = f"BAML generation failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
                raise BAMLCompilationError(
                    error_msg,
                    self.baml_code
                )
            
            # Import the generated client
            client_dir = self.project_dir / "baml_client"
            if not client_dir.exists():
                raise BAMLCompilationError(
                    "Generated baml_client directory not found",
                    self.baml_code
                )
            
            # Add to sys.path and import
            sys.path.insert(0, str(self.project_dir))
            
            try:
                import baml_client.sync_client as sync_client
                self.client_module = sync_client
            except ImportError as e:
                raise BAMLCompilationError(
                    f"Failed to import generated client: {str(e)}",
                    self.baml_code
                ) from e
            
            return self.project_dir, self.client_module
            
        except Exception as e:
            # Clean up on error
            if self.project_dir and self.project_dir.exists():
                shutil.rmtree(self.project_dir)
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up
        if self.project_dir and self.project_dir.exists():
            # Remove from sys.path
            if str(self.project_dir) in sys.path:
                sys.path.remove(str(self.project_dir))
            
            # Remove from sys.modules
            modules_to_remove = [
                name for name in sys.modules.keys() 
                if name.startswith('baml_client')
            ]
            for module_name in modules_to_remove:
                del sys.modules[module_name]
            
            # Remove directory
            shutil.rmtree(self.project_dir)


def _temporary_baml_project(baml_code: str, function_name: str):
    """Create a temporary BAML project context manager."""
    return _TemporaryBAMLProject(baml_code, function_name) 