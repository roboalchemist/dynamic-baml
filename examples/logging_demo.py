#!/usr/bin/env python3
"""
Demonstration of Dynamic BAML logging functionality.

This script shows various ways to configure logging in Dynamic BAML,
including different log levels and file output options.

Note: This demo uses mocked LLM calls to demonstrate logging without 
requiring actual LLM access. In real usage, you would use actual providers.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from dynamic_baml import call_with_schema, call_with_schema_safe


def demo_logging_levels():
    """Demonstrate different logging levels."""
    print("🔍 Demonstrating Logging Levels")
    print("=" * 50)
    
    schema = {"name": "string", "age": "int", "city": "string"}
    prompt = "Extract: John Smith, 30 years old, lives in Boston"
    
    # Mock BAML to avoid needing real LLM
    with patch('dynamic_baml.core._temporary_baml_project') as mock_project:
        mock_client = MagicMock()
        mock_function = MagicMock()
        mock_function.return_value = MagicMock()
        mock_function.return_value.model_dump.return_value = {
            "name": "John Smith", "age": 30, "city": "Boston"
        }
        mock_client.b = MagicMock()
        setattr(mock_client.b, "ExtractDynamicSchema_12345678", mock_function)
        
        mock_project.return_value.__enter__.return_value = (Path("/tmp"), mock_client)
        mock_project.return_value.__exit__.return_value = None
        
        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = "12345678" * 4
            
            log_levels = ["off", "error", "warn", "info", "debug"]
            
            for level in log_levels:
                print(f"\n📊 Testing log level: {level}")
                
                options = {
                    "provider": "ollama",
                    "model": "gemma3:1b", 
                    "log_level": level
                }
                
                result = call_with_schema(prompt, schema, options)
                print(f"   ✅ Result: {result}")
                print(f"   📋 Log level '{level}' configured successfully")


def demo_log_file_output():
    """Demonstrate logging to files."""
    print("\n\n📁 Demonstrating Log File Output")
    print("=" * 50)
    
    # Create temporary directory for logs
    temp_dir = Path(tempfile.mkdtemp(prefix="baml_demo_"))
    
    try:
        schema = {"product": "string", "price": "float", "category": "string"}
        
        # Mock BAML execution
        with patch('dynamic_baml.core._temporary_baml_project') as mock_project:
            mock_client = MagicMock()
            mock_function = MagicMock()
            mock_function.return_value = MagicMock()
            mock_function.return_value.model_dump.return_value = {
                "product": "Laptop", "price": 999.99, "category": "Electronics"
            }
            mock_client.b = MagicMock()
            setattr(mock_client.b, "ExtractDynamicSchema_87654321", mock_function)
            
            mock_project.return_value.__enter__.return_value = (temp_dir, mock_client)
            mock_project.return_value.__exit__.return_value = None
            
            with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
                mock_uuid.return_value.hex = "87654321" * 4
                
                # Demo 1: Basic log file
                log_file_1 = temp_dir / "basic.log"
                options1 = {
                    "provider": "openai",
                    "model": "gpt-4",
                    "log_level": "info",
                    "log_file": str(log_file_1)
                }
                
                print(f"\n📝 Logging to: {log_file_1}")
                result1 = call_with_schema(
                    "Extract: MacBook Pro costs $1299 in Electronics category",
                    schema,
                    options1
                )
                print(f"   ✅ Result: {result1}")
                print(f"   📂 Log file created: {log_file_1.exists()}")
                
                # Demo 2: Nested directory
                nested_log = temp_dir / "logs" / "detailed" / "extraction.log"
                options2 = {
                    "provider": "anthropic",
                    "model": "claude-3-5-sonnet-20241022",
                    "log_level": "debug",
                    "log_file": str(nested_log)
                }
                
                print(f"\n📝 Logging to nested path: {nested_log}")
                result2 = call_with_schema(
                    "Extract: iPhone 15 costs $999 in Electronics category",
                    schema,
                    options2
                )
                print(f"   ✅ Result: {result2}")
                print(f"   📂 Nested directories created: {nested_log.parent.exists()}")
                print(f"   📂 Log file created: {nested_log.exists()}")
                
                # Demo 3: Multiple calls to same file
                options3 = {
                    "provider": "ollama",
                    "model": "gemma3:1b",
                    "log_level": "info", 
                    "log_file": str(log_file_1)  # Same file as first demo
                }
                
                print(f"\n📝 Appending to existing log: {log_file_1}")
                result3 = call_with_schema(
                    "Extract: Samsung Galaxy costs $899 in Electronics category",
                    schema,
                    options3
                )
                print(f"   ✅ Result: {result3}")
                print(f"   📄 Multiple entries in same log file")
                
                # Show environment variable setting
                print(f"\n🔧 Environment variable: DYNAMIC_BAML_LOG_FILE = {os.environ.get('DYNAMIC_BAML_LOG_FILE', 'Not set')}")
                
    finally:
        # Clean up
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Cleaned up temporary directory: {temp_dir}")


def demo_safe_calls_with_logging():
    """Demonstrate safe calls with logging configuration."""
    print("\n\n🛡️ Demonstrating Safe Calls with Logging")
    print("=" * 50)
    
    temp_dir = Path(tempfile.mkdtemp(prefix="baml_safe_demo_"))
    
    try:
        schema = {"name": "string", "sentiment": "string", "confidence": "float"}
        
        # Mock BAML execution
        with patch('dynamic_baml.core._temporary_baml_project') as mock_project:
            mock_client = MagicMock()
            mock_function = MagicMock()
            mock_function.return_value = MagicMock()
            mock_function.return_value.model_dump.return_value = {
                "name": "Alice", "sentiment": "positive", "confidence": 0.95
            }
            mock_client.b = MagicMock()
            setattr(mock_client.b, "ExtractDynamicSchema_abcdef12", mock_function)
            
            mock_project.return_value.__enter__.return_value = (temp_dir, mock_client)
            mock_project.return_value.__exit__.return_value = None
            
            with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
                mock_uuid.return_value.hex = "abcdef12" * 4
                
                log_file = temp_dir / "safe_calls.log"
                options = {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "log_level": "info",
                    "log_file": str(log_file)
                }
                
                # Safe call with logging
                result = call_with_schema_safe(
                    "Analyze: Alice seems very happy about the new features",
                    schema,
                    options
                )
                
                print(f"\n📊 Safe call result structure:")
                print(f"   Success: {result.get('success')}")
                if result.get('success'):
                    print(f"   Data: {result.get('data')}")
                else:
                    print(f"   Error: {result.get('error')}")
                    print(f"   Error Type: {result.get('error_type')}")
                
                print(f"   📂 Log file created: {log_file.exists()}")
                
    finally:
        # Clean up
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Cleaned up temporary directory: {temp_dir}")


def demo_combined_configurations():
    """Demonstrate various combinations of logging configurations."""
    print("\n\n⚙️ Demonstrating Combined Configurations")
    print("=" * 50)
    
    configs = [
        {
            "name": "OpenAI with Info Logging",
            "options": {"provider": "openai", "model": "gpt-4", "log_level": "info"},
            "description": "Log level only - output goes to terminal"
        },
        {
            "name": "Anthropic with File Logging",
            "options": {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022", "log_file": "/tmp/anthropic.log"},
            "description": "Log file only - uses default log level"
        },
        {
            "name": "Ollama with Debug to File",
            "options": {"provider": "ollama", "model": "gemma3:1b", "log_level": "debug", "log_file": "/tmp/debug.log"},
            "description": "Both log level and file specified"
        },
        {
            "name": "OpenRouter with Logging Disabled",
            "options": {"provider": "openrouter", "model": "google/gemini-2.0-flash-exp", "log_level": "off"},
            "description": "Logging completely disabled"
        },
        {
            "name": "Default Configuration",
            "options": {"provider": "ollama", "model": "gemma3:1b"},
            "description": "No logging options - uses BAML defaults"
        }
    ]
    
    schema = {"summary": "string", "word_count": "int"}
    
    # Mock BAML execution
    with patch('dynamic_baml.core._temporary_baml_project') as mock_project:
        mock_client = MagicMock()
        mock_function = MagicMock()
        mock_function.return_value = MagicMock()
        mock_function.return_value.model_dump.return_value = {
            "summary": "Configuration demo", "word_count": 15
        }
        mock_client.b = MagicMock()
        setattr(mock_client.b, "ExtractDynamicSchema_fedcba98", mock_function)
        
        mock_project.return_value.__enter__.return_value = (Path("/tmp"), mock_client)
        mock_project.return_value.__exit__.return_value = None
        
        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = "fedcba98" * 4
            
            for i, config in enumerate(configs, 1):
                print(f"\n{i}. {config['name']}")
                print(f"   📋 {config['description']}")
                print(f"   ⚙️  Options: {config['options']}")
                
                try:
                    result = call_with_schema(
                        "Summarize: This is a demonstration of logging configurations",
                        schema,
                        config['options']
                    )
                    print(f"   ✅ Success: {result}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")


def main():
    """Run all logging demonstrations."""
    print("🚀 Dynamic BAML Logging Functionality Demo")
    print("=" * 60)
    print("This demo shows how to configure logging in Dynamic BAML")
    print("=" * 60)
    
    try:
        demo_logging_levels()
        demo_log_file_output()
        demo_safe_calls_with_logging()
        demo_combined_configurations()
        
        print("\n\n🎉 Demo Complete!")
        print("=" * 50)
        print("📖 Key takeaways:")
        print("   • Use 'log_level' to control verbosity: off, error, warn, info, debug, trace")
        print("   • Use 'log_file' to redirect logs to a specific file")
        print("   • Both options can be used together or separately")
        print("   • Log directories are created automatically")
        print("   • Safe calls (call_with_schema_safe) also support logging")
        print("   • Logging configuration doesn't affect main functionality")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 