#!/usr/bin/env python3
"""
Error Handling Example for Dynamic BAML

This example demonstrates comprehensive error handling:
- Different exception types and their usage
- Error recovery strategies  
- Safe calling patterns
- Graceful degradation
- Retry mechanisms
"""

from dynamic_baml import call_with_schema, call_with_schema_safe
from dynamic_baml.exceptions import (
    DynamicBAMLError,
    SchemaGenerationError,
    BAMLCompilationError,
    LLMProviderError,
    ResponseParsingError,
    ConfigurationError,
    TimeoutError
)
import time
import json


def schema_error_example():
    """Demonstrate schema generation errors."""
    print("🔧 Schema Generation Error Example")
    print("-" * 40)
    
    # Invalid schema that will cause errors
    invalid_schemas = [
        # Unsupported type
        {"field": "unsupported_type"},
        
        # Invalid enum structure
        {"status": {"type": "enum", "values": []}},  # Empty values
        
        # Malformed nested structure
        {"nested": {"": "string"}},  # Empty key
        
        # Invalid array definition
        {"items": ["unsupported_nested_array_type"]}
    ]
    
    for i, schema in enumerate(invalid_schemas, 1):
        print(f"\nTest {i}: Invalid Schema")
        try:
            result = call_with_schema(
                "Test prompt",
                schema,
                {"provider": "openai", "model": "gpt-4"}
            )
            print(f"❌ Unexpectedly succeeded: {result}")
        except SchemaGenerationError as e:
            print(f"✅ Caught SchemaGenerationError: {e.message}")
            print(f"   Problem schema: {e.schema_dict}")
        except Exception as e:
            print(f"❓ Unexpected error: {type(e).__name__}: {e}")


def provider_error_example():
    """Demonstrate provider configuration errors."""
    print("\n🌐 Provider Configuration Error Example")
    print("-" * 40)
    
    schema = {"result": "string"}
    
    invalid_configs = [
        # Unknown provider
        {"provider": "unknown_provider"},
        
        # Missing API key (assuming not set)
        {"provider": "openai", "model": "gpt-4", "api_key": "invalid_key"},
        
        # Invalid model name
        {"provider": "openai", "model": "nonexistent-model"},
        
        # Missing required configuration
        {"provider": "openrouter"}  # Missing model
    ]
    
    for i, config in enumerate(invalid_configs, 1):
        print(f"\nTest {i}: Invalid Provider Config")
        try:
            result = call_with_schema(
                "Test prompt",
                schema,
                config
            )
            print(f"❌ Unexpectedly succeeded: {result}")
        except ConfigurationError as e:
            print(f"✅ Caught ConfigurationError: {e.message}")
            print(f"   Context: {e.context}")
        except LLMProviderError as e:
            print(f"✅ Caught LLMProviderError: {e.message}")
            print(f"   Provider: {e.provider}")
        except Exception as e:
            print(f"❓ Unexpected error: {type(e).__name__}: {e}")


def timeout_error_example():
    """Demonstrate timeout handling."""
    print("\n⏰ Timeout Error Example")
    print("-" * 40)
    
    schema = {
        "complex_analysis": {
            "summary": "string",
            "detailed_breakdown": ["string"],
            "recommendations": ["string"]
        }
    }
    
    # Very long prompt that might timeout
    long_text = "Analyze this text: " + "Very complex analysis request. " * 1000
    
    # Very short timeout to force timeout error
    options = {
        "provider": "openai",
        "model": "gpt-4",
        "timeout": 0.1  # Unreasonably short timeout
    }
    
    try:
        result = call_with_schema(long_text, schema, options)
        print(f"❌ Unexpectedly succeeded: {result}")
    except TimeoutError as e:
        print(f"✅ Caught TimeoutError: {e.message}")
        print(f"   Timeout duration: {e.timeout_duration}")
    except Exception as e:
        print(f"❓ Unexpected error: {type(e).__name__}: {e}")


def safe_calling_patterns():
    """Demonstrate safe calling patterns."""
    print("\n🛡️ Safe Calling Patterns")
    print("-" * 40)
    
    schema = {"analysis": "string", "confidence": "float"}
    
    # Test data that might cause various errors
    test_cases = [
        ("Valid case", "Analyze this text: Hello world", {"provider": "openai", "model": "gpt-4"}),
        ("Schema error", "Test", {"invalid": "schema"}),
        ("Provider error", "Test", {"provider": "invalid_provider"}),
        ("Timeout error", "Test", {"provider": "openai", "model": "gpt-4", "timeout": 0.001})
    ]
    
    for name, prompt, options in test_cases:
        print(f"\n{name}:")
        
        # Safe call method
        result = call_with_schema_safe(prompt, schema, options)
        
        if result["success"]:
            print(f"✅ Success: {result['data']}")
        else:
            print(f"❌ Error ({result['error_type']}): {result['error']}")


def retry_mechanism():
    """Demonstrate retry mechanisms for transient failures."""
    print("\n🔄 Retry Mechanism Example")
    print("-" * 40)
    
    def robust_call_with_retry(prompt, schema, options, max_retries=3, base_delay=1):
        """Call with exponential backoff retry."""
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    delay = base_delay * (2 ** (attempt - 1))
                    print(f"   Retrying in {delay}s... (attempt {attempt + 1})")
                    time.sleep(delay)
                
                result = call_with_schema(prompt, schema, options)
                if attempt > 0:
                    print(f"✅ Success on attempt {attempt + 1}")
                return result
                
            except TimeoutError as e:
                if attempt < max_retries:
                    print(f"⏰ Timeout on attempt {attempt + 1}: {e.message}")
                    continue
                else:
                    print(f"❌ Final timeout after {max_retries + 1} attempts")
                    raise
                    
            except LLMProviderError as e:
                if "rate limit" in str(e).lower() and attempt < max_retries:
                    print(f"🚦 Rate limit on attempt {attempt + 1}: {e.message}")
                    continue
                else:
                    print(f"❌ Provider error: {e.message}")
                    raise
                    
            except Exception as e:
                print(f"❌ Non-retryable error: {type(e).__name__}: {e}")
                raise
    
    schema = {"summary": "string"}
    
    # Example with short timeout to trigger retries
    options = {
        "provider": "openai", 
        "model": "gpt-4",
        "timeout": 5  # Short but not unreasonable
    }
    
    try:
        result = robust_call_with_retry(
            "Summarize: This is a test document for retry mechanism.",
            schema,
            options,
            max_retries=2
        )
        print(f"Final result: {result}")
    except Exception as e:
        print(f"Final failure: {type(e).__name__}: {e}")


def error_context_handling():
    """Demonstrate extracting useful context from errors."""
    print("\n🔍 Error Context Handling")
    print("-" * 40)
    
    def handle_dynamic_baml_error(error):
        """Extract and display useful error context."""
        
        error_info = {
            "type": type(error).__name__,
            "message": str(error),
            "context": {}
        }
        
        # Extract specific context based on error type
        if isinstance(error, SchemaGenerationError):
            error_info["context"]["schema"] = error.schema_dict
            
        elif isinstance(error, LLMProviderError):
            error_info["context"]["provider"] = error.provider
            if hasattr(error, 'status_code'):
                error_info["context"]["status_code"] = error.status_code
                
        elif isinstance(error, ResponseParsingError):
            error_info["context"]["raw_response"] = error.raw_response
            if hasattr(error, 'expected_schema'):
                error_info["context"]["expected_schema"] = error.expected_schema
                
        elif isinstance(error, TimeoutError):
            error_info["context"]["timeout_duration"] = error.timeout_duration
            
        elif isinstance(error, ConfigurationError):
            error_info["context"]["config_context"] = error.context
        
        return error_info
    
    # Test various error scenarios
    error_scenarios = [
        ("Schema Error", "test", {"invalid": "schema"}, {"provider": "openai"}),
        ("Provider Error", "test", {"result": "string"}, {"provider": "invalid"}),
        ("Config Error", "test", {"result": "string"}, {"provider": "openai"})  # Missing model
    ]
    
    for scenario_name, prompt, schema, options in error_scenarios:
        print(f"\n{scenario_name}:")
        try:
            result = call_with_schema(prompt, schema, options)
            print(f"❌ Unexpectedly succeeded: {result}")
        except DynamicBAMLError as e:
            error_info = handle_dynamic_baml_error(e)
            print(f"✅ Caught {error_info['type']}")
            print(f"   Message: {error_info['message']}")
            if error_info['context']:
                print(f"   Context: {json.dumps(error_info['context'], indent=4)}")


def graceful_degradation():
    """Demonstrate graceful degradation strategies."""
    print("\n🎯 Graceful Degradation Example")
    print("-" * 40)
    
    def extract_with_fallback(text, preferred_schema, fallback_schema, options):
        """Try complex extraction, fall back to simpler one if needed."""
        
        print("Attempting complex extraction...")
        result = call_with_schema_safe(
            f"Complex analysis: {text}",
            preferred_schema,
            options
        )
        
        if result["success"]:
            print("✅ Complex extraction successful")
            return result["data"], "complex"
        
        print(f"❌ Complex extraction failed: {result['error']}")
        print("Falling back to simple extraction...")
        
        fallback_result = call_with_schema_safe(
            f"Simple extraction: {text}",
            fallback_schema,
            options
        )
        
        if fallback_result["success"]:
            print("✅ Simple extraction successful")
            return fallback_result["data"], "simple"
        
        print(f"❌ All extractions failed: {fallback_result['error']}")
        return None, "failed"
    
    # Complex schema that might fail
    complex_schema = {
        "detailed_analysis": {
            "sentiment": {"type": "enum", "values": ["positive", "negative", "neutral"]},
            "key_themes": ["string"],
            "emotional_indicators": ["string"],
            "confidence_scores": {
                "sentiment": "float",
                "theme_relevance": "float"
            },
            "recommendations": ["string"]
        }
    }
    
    # Simple fallback schema
    simple_schema = {
        "summary": "string",
        "sentiment": {"type": "enum", "values": ["positive", "negative", "neutral"]}
    }
    
    text = "I love this product! It's amazing and works perfectly."
    options = {"provider": "openai", "model": "gpt-4"}
    
    result, extraction_type = extract_with_fallback(
        text, complex_schema, simple_schema, options
    )
    
    if result:
        print(f"\n📊 Final result ({extraction_type} extraction):")
        print(json.dumps(result, indent=2))
    else:
        print("\n❌ All extraction attempts failed")


if __name__ == "__main__":
    print("=== Dynamic BAML Error Handling Examples ===\n")
    
    schema_error_example()
    provider_error_example()
    timeout_error_example()
    safe_calling_patterns()
    retry_mechanism()
    error_context_handling()
    graceful_degradation()
    
    print("\n✅ Error handling examples completed!") 