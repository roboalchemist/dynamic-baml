# Dynamic BAML 🚀

**Dynamic BAML** is a Python library that enables you to extract structured data from text using Large Language Models (LLMs) with dynamically generated schemas. Built on top of [BoundaryML](https://www.boundaryml.com/), it provides a high-level Python interface for BAML (Boundary Augmented Markup Language) with automatic schema generation.

Define your desired output structure as a simple Python dictionary, and Dynamic BAML handles the rest!

## ✨ Features

- 🎯 **Schema-First Approach**: Define output structure with Python dictionaries
- 🔄 **Dynamic BAML Generation**: Automatically converts schemas to BAML code
- 🌐 **Multi-Provider Support**: Works with OpenAI, Anthropic, Ollama, and OpenRouter
- 🛡️ **Type Safety**: Ensures structured, validated outputs
- 🔧 **Easy Integration**: Simple API with comprehensive error handling
- 📊 **Complex Types**: Support for nested objects, enums, arrays, and optional fields
- ⚡ **Performance**: Efficient temporary project management and cleanup

## 🚀 Quick Start

### Installation

```bash
pip install dynamic-baml
```

### Basic Usage

```python
from dynamic_baml import call_with_schema

# Define your desired output structure
schema = {
    "name": "string",
    "age": "int", 
    "email": "string",
    "is_active": "bool"
}

# Extract structured data from text
text = "John Doe is 30 years old, email: john@example.com, currently active user"

result = call_with_schema(
    prompt_text=f"Extract user information from: {text}",
    schema_dict=schema,
    options={"provider": "openai", "model": "gpt-4"}
)

print(result)
# Output: {"name": "John Doe", "age": 30, "email": "john@example.com", "is_active": True}
```

## 📋 Table of Contents

- [Installation & Setup](#installation--setup)
- [Core Concepts](#core-concepts)
- [Schema Types](#schema-types)
- [Provider Configuration](#provider-configuration)
- [Advanced Usage](#advanced-usage)
- [Error Handling](#error-handling)
- [Examples](#examples)
- [API Reference](#api-reference)

## 🛠️ Installation & Setup

### Requirements

- Python 3.8+
- BAML CLI from BoundaryML: `npm install -g @boundaryml/baml`
  - This provides the core BAML compiler and runtime
  - Learn more at [docs.boundaryml.com](https://docs.boundaryml.com/)

### Provider Setup

#### OpenAI
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

#### Anthropic
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

#### Ollama (Local)
```bash
# Install and start Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull gemma3:1b
```

#### OpenRouter
```bash
export OPENROUTER_API_KEY="your-openrouter-api-key"
```

## 🧠 Core Concepts

### Schema Dictionary
Define your desired output structure using Python dictionaries:

```python
schema = {
    "field_name": "field_type",
    "nested_object": {
        "sub_field": "string"
    },
    "optional_field": {"type": "string", "optional": True}
}
```

### BAML Generation
Dynamic BAML automatically converts your schema to BAML code:

```python
# Your schema:
{"name": "string", "age": "int"}

# Generated BAML:
class UserInfo {
  name string
  age int
}
```

## 📊 Schema Types

### Basic Types

```python
schema = {
    "text": "string",        # Text data
    "number": "int",        # Integer
    "price": "float",       # Decimal number
    "active": "bool"        # True/False
}
```

### Arrays

```python
schema = {
    "tags": ["string"],     # Array of strings
    "scores": ["int"],      # Array of integers
    "ratings": ["float"]    # Array of floats
}
```

### Enums

```python
schema = {
    "status": {
        "type": "enum",
        "values": ["draft", "published", "archived"]
    },
    "priority": {
        "type": "enum", 
        "values": ["low", "medium", "high", "urgent"]
    }
}
```

### Nested Objects

```python
schema = {
    "user": {
        "name": "string",
        "email": "string",
        "profile": {
            "bio": "string",
            "avatar_url": "string"
        }
    },
    "metadata": {
        "created_at": "string",
        "updated_at": "string"
    }
}
```

### Optional Fields

```python
schema = {
    "name": "string",                              # Required
    "email": {"type": "string", "optional": True}, # Optional
    "phone": {"type": "string", "optional": True}  # Optional
}
```

## ⚙️ Provider Configuration

### OpenAI

```python
options = {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.1,
    "max_tokens": 2000,
    "timeout": 60
}
```

### Anthropic

```python
options = {
    "provider": "anthropic", 
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 0.1,
    "max_tokens": 2000,
    "timeout": 60
}
```

### Ollama (Local)

```python
options = {
    "provider": "ollama",
    "model": "gemma3:1b",
    "base_url": "http://localhost:11434",  # Optional
    "temperature": 0.1,
    "timeout": 120
}
```

### OpenRouter

```python
options = {
    "provider": "openrouter",
    "model": "google/gemini-2.0-flash-exp",
    "temperature": 0.1,
    "max_tokens": 2000,
    "timeout": 60
}
```

## 🔄 Advanced Usage

### Safe Calling (No Exceptions)

```python
from dynamic_baml import call_with_schema_safe

result = call_with_schema_safe(
    prompt_text="Extract data from this text...",
    schema_dict=schema,
    options=options
)

if result["success"]:
    data = result["data"]
    print(f"Extracted: {data}")
else:
    print(f"Error: {result['error']}")
    print(f"Error type: {result['error_type']}")
```

### Custom Prompting

```python
# Build effective prompts for better extraction
prompt = f"""
Please extract the following information from the text below:

REQUIRED FIELDS:
- name: Person's full name
- age: Person's age as a number
- email: Valid email address

TEXT TO ANALYZE:
{input_text}

Please be accurate and only extract information that is clearly stated.
"""

result = call_with_schema(prompt, schema, options)
```

### Batch Processing

```python
def process_documents(documents, schema, options):
    results = []
    for doc in documents:
        try:
            result = call_with_schema(
                f"Extract information from: {doc['content']}", 
                schema, 
                options
            )
            results.append({"doc_id": doc["id"], "data": result})
        except Exception as e:
            results.append({"doc_id": doc["id"], "error": str(e)})
    return results
```

## 🚨 Error Handling

### Exception Types

```python
from dynamic_baml.exceptions import (
    DynamicBAMLError,           # Base exception
    SchemaGenerationError,      # Schema conversion failed
    BAMLCompilationError,       # BAML code compilation failed
    LLMProviderError,          # LLM provider call failed
    ResponseParsingError,       # Response parsing failed
    ConfigurationError,         # Provider configuration invalid
    TimeoutError               # Request timeout
)

try:
    result = call_with_schema(prompt, schema, options)
except SchemaGenerationError as e:
    print(f"Schema error: {e.message}")
    print(f"Invalid schema: {e.schema_dict}")
except LLMProviderError as e:
    print(f"Provider error: {e.message}")
    print(f"Provider: {e.provider}")
except ResponseParsingError as e:
    print(f"Parsing error: {e.message}")
    print(f"Raw response: {e.raw_response}")
```

### Error Recovery

```python
def robust_extraction(text, schema, providers):
    """Try multiple providers for reliable extraction."""
    for provider_opts in providers:
        try:
            return call_with_schema(text, schema, provider_opts)
        except LLMProviderError:
            continue  # Try next provider
        except Exception as e:
            print(f"Unexpected error with {provider_opts['provider']}: {e}")
    
    raise Exception("All providers failed")

# Usage
providers = [
    {"provider": "openai", "model": "gpt-4"},
    {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
    {"provider": "ollama", "model": "gemma3:1b"}
]

result = robust_extraction(text, schema, providers)
```

## 📚 Examples

See the [examples/](examples/) directory for comprehensive examples:

- [Basic Usage](examples/basic_usage.py)
- [Complex Schemas](examples/complex_schemas.py) 
- [Multi-Provider Setup](examples/multi_provider.py)
- [Error Handling](examples/error_handling.py)
- [Batch Processing](examples/batch_processing.py)
- [Real-World Use Cases](examples/real_world.py)

## 📖 API Reference

### Core Functions

#### `call_with_schema(prompt_text, schema_dict, options=None) -> dict`

Extract structured data using a schema.

**Parameters:**
- `prompt_text` (str): Text prompt to send to the LLM
- `schema_dict` (dict): Schema definition dictionary
- `options` (dict, optional): Provider configuration options

**Returns:**
- `dict`: Extracted data matching the schema structure

**Raises:**
- `DynamicBAMLError`: Base exception for all errors
- `SchemaGenerationError`: Schema conversion failed
- `LLMProviderError`: Provider call failed
- `ResponseParsingError`: Response parsing failed

#### `call_with_schema_safe(prompt_text, schema_dict, options=None) -> dict`

Safe version that returns structured results instead of raising exceptions.

**Returns:**
```python
{
    "success": bool,
    "data": dict,      # Present if success=True
    "error": str,      # Present if success=False
    "error_type": str  # Present if success=False
}
```

### Schema Generator

#### `DictToBAMLGenerator.generate_schema(schema_dict, schema_name) -> str`

Generate BAML schema code from dictionary.

**Parameters:**
- `schema_dict` (dict): Schema definition
- `schema_name` (str): Name for the generated schema

**Returns:**
- `str`: Valid BAML schema code

### Provider Factory

#### `LLMProviderFactory.create_provider(options) -> LLMProvider`

Create provider instance based on options.

#### `LLMProviderFactory.get_available_providers() -> List[str]`

Get list of currently available providers.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🙏 Acknowledgments

Dynamic BAML is built on top of [BoundaryML](https://www.boundaryml.com/) and the powerful [BAML language](https://docs.boundaryml.com/). We extend our gratitude to the BoundaryML team for creating the foundational technology that makes structured LLM outputs possible.

**About BoundaryML:**
- 🔗 **Website**: [boundaryml.com](https://www.boundaryml.com/)
- 📚 **BAML Documentation**: [docs.boundaryml.com](https://docs.boundaryml.com/)
- 🛠️ **BAML CLI**: `npm install -g @boundaryml/baml`

Dynamic BAML provides a Python-friendly interface and automatic schema generation on top of the robust BAML foundation.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Documentation](https://dynamic-baml.readthedocs.io)
- 🐛 [Issue Tracker](https://github.com/yourusername/dynamic-baml/issues)
- 💬 [Discussions](https://github.com/yourusername/dynamic-baml/discussions)

## 🏆 Why Dynamic BAML?

### Traditional Approach
```python
# Complex manual prompt engineering
prompt = """
Extract user data and format as JSON with these exact fields:
- name (string)
- age (integer) 
- email (string)
- is_active (boolean)

Text: "John Doe is 30 years old..."

Please ensure the output is valid JSON with no extra text.
"""

response = llm.call(prompt)
data = json.loads(response)  # Hope it's valid JSON!
```

### Dynamic BAML Approach
```python
# Clean, type-safe schema definition
schema = {
    "name": "string",
    "age": "int", 
    "email": "string",
    "is_active": "bool"
}

data = call_with_schema(
    "Extract user info from: John Doe is 30 years old...",
    schema
)  # Guaranteed structured output!
```

**Benefits:**
- ✅ **Type Safety**: Guaranteed schema compliance
- ✅ **No JSON Parsing**: Direct structured output  
- ✅ **Better Prompts**: Optimized prompt engineering
- ✅ **Error Handling**: Comprehensive error management
- ✅ **Multi-Provider**: Easy provider switching
- ✅ **Complex Types**: Enums, nested objects, arrays

---

**Made with ❤️ by the Dynamic BAML Team** 