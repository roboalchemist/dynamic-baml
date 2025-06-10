#!/usr/bin/env python3
"""
Multi-Provider Example for Dynamic BAML

This example demonstrates how to use different LLM providers:
- OpenAI (GPT models)
- Anthropic (Claude models) 
- Ollama (Local models)
- OpenRouter (Multiple providers via API)
- Provider-specific configurations
- Fallback strategies
"""

from dynamic_baml import call_with_schema, call_with_schema_safe
import os
import time
import json


def openai_example():
    """Example using OpenAI provider."""
    print("🤖 OpenAI Provider Example")
    print("-" * 30)
    
    schema = {
        "summary": "string",
        "sentiment": {
            "type": "enum",
            "values": ["positive", "negative", "neutral"]
        },
        "key_points": ["string"],
        "confidence": "float"
    }
    
    text = """
    I'm absolutely thrilled with this new AI tool! It's incredibly intuitive and 
    has saved me hours of work. The documentation is comprehensive and the 
    support team is responsive. However, I wish the pricing was more transparent 
    and there were more customization options available.
    """
    
    options = {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.1,
        "max_tokens": 1000,
        "timeout": 30
    }
    
    try:
        result = call_with_schema(
            f"Analyze this customer feedback: {text}",
            schema,
            options
        )
        print("✅ OpenAI Analysis:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
    
    print()


def anthropic_example():
    """Example using Anthropic provider."""
    print("🧠 Anthropic Provider Example")
    print("-" * 30)
    
    schema = {
        "code_review": {
            "issues": [
                {
                    "type": {
                        "type": "enum",
                        "values": ["bug", "performance", "security", "style", "maintainability"]
                    },
                    "severity": {
                        "type": "enum",
                        "values": ["low", "medium", "high", "critical"]
                    },
                    "description": "string",
                    "line_number": {"type": "int", "optional": True},
                    "suggestion": "string"
                }
            ],
            "overall_rating": {
                "type": "enum",
                "values": ["poor", "fair", "good", "excellent"]
            },
            "summary": "string"
        }
    }
    
    code = """
    def process_user_data(data):
        password = data['password']
        email = data.get('email')
        
        # Store password in plain text
        user_record = {
            'email': email,
            'password': password,
            'created': time.time()
        }
        
        # No input validation
        db.save(user_record)
        
        return user_record
    """
    
    options = {
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        "temperature": 0.0,
        "max_tokens": 2000,
        "timeout": 45
    }
    
    try:
        result = call_with_schema(
            f"Review this Python code for issues:\n\n{code}",
            schema,
            options
        )
        print("✅ Anthropic Code Review:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Anthropic Error: {e}")
    
    print()


def ollama_example():
    """Example using Ollama local provider."""
    print("🏠 Ollama Local Provider Example")
    print("-" * 30)
    
    schema = {
        "recipe": {
            "name": "string",
            "cuisine": "string",
            "difficulty": {
                "type": "enum",
                "values": ["easy", "medium", "hard"]
            },
            "prep_time_minutes": "int",
            "cook_time_minutes": "int",
            "servings": "int",
            "ingredients": [
                {
                    "item": "string",
                    "amount": "string",
                    "unit": "string"
                }
            ],
            "instructions": ["string"],
            "dietary_tags": ["string"]
        }
    }
    
    text = """
    I want to make a simple pasta dish for 4 people. I have tomatoes, garlic, 
    olive oil, basil, and spaghetti. It should be something I can prepare 
    in about 30 minutes total, and I'm a beginner cook.
    """
    
    options = {
        "provider": "ollama",
        "model": "gemma3:1b",
        "base_url": "http://localhost:11434",  # Default Ollama URL
        "temperature": 0.2,
        "timeout": 120  # Local models might be slower
    }
    
    try:
        result = call_with_schema(
            f"Create a recipe based on these requirements: {text}",
            schema,
            options
        )
        print("✅ Ollama Recipe Generation:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Ollama Error: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        print("💡 And model is available: ollama pull gemma3:1b")
    
    print()


def openrouter_example():
    """Example using OpenRouter provider."""
    print("🌐 OpenRouter Provider Example")
    print("-" * 30)
    
    schema = {
        "translation": {
            "original_language": "string",
            "target_language": "string",
            "translated_text": "string",
            "confidence": "float",
            "notes": {
                "type": "string",
                "optional": True
            }
        },
        "linguistic_analysis": {
            "complexity": {
                "type": "enum",
                "values": ["simple", "moderate", "complex", "very_complex"]
            },
            "tone": {
                "type": "enum",
                "values": ["formal", "informal", "neutral", "technical"]
            },
            "cultural_notes": ["string"]
        }
    }
    
    text = """
    "¡Hola! ¿Cómo estás? Me llamo María y soy ingeniera de software. 
    ¿Te gustaría que trabajáramos juntos en este proyecto?"
    """
    
    options = {
        "provider": "openrouter",
        "model": "google/gemini-2.0-flash-exp",
        "temperature": 0.1,
        "max_tokens": 1500,
        "timeout": 60
    }
    
    try:
        result = call_with_schema(
            f"Translate this Spanish text to English and provide linguistic analysis: {text}",
            schema,
            options
        )
        print("✅ OpenRouter Translation:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ OpenRouter Error: {e}")
        print("💡 Make sure OPENROUTER_API_KEY is set")
    
    print()


def provider_comparison():
    """Compare the same task across multiple providers."""
    print("⚖️ Provider Comparison Example")
    print("-" * 30)
    
    schema = {
        "analysis": {
            "main_topic": "string",
            "key_insights": ["string"],
            "complexity_level": {
                "type": "enum",
                "values": ["basic", "intermediate", "advanced", "expert"]
            },
            "recommended_audience": ["string"]
        }
    }
    
    text = """
    Quantum computing represents a paradigm shift in computational capability, 
    leveraging quantum mechanical phenomena such as superposition and entanglement 
    to process information in fundamentally different ways than classical computers. 
    While still in early stages, quantum algorithms like Shor's and Grover's 
    demonstrate potential for exponential speedups in specific problem domains.
    """
    
    providers = [
        {"provider": "openai", "model": "gpt-4", "name": "OpenAI GPT-4"},
        {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022", "name": "Anthropic Claude"},
        {"provider": "ollama", "model": "gemma3:1b", "name": "Ollama Gemma3"},
        {"provider": "openrouter", "model": "google/gemini-2.0-flash-exp", "name": "OpenRouter Gemini"}
    ]
    
    results = {}
    
    for provider_config in providers:
        provider_name = provider_config.pop("name")
        print(f"Testing {provider_name}...")
        
        start_time = time.time()
        result = call_with_schema_safe(
            f"Analyze this technical text: {text}",
            schema,
            provider_config
        )
        end_time = time.time()
        
        if result["success"]:
            results[provider_name] = {
                "data": result["data"],
                "response_time": round(end_time - start_time, 2)
            }
            print(f"✅ {provider_name}: {results[provider_name]['response_time']}s")
        else:
            results[provider_name] = {
                "error": result["error"],
                "response_time": round(end_time - start_time, 2)
            }
            print(f"❌ {provider_name}: {result['error']}")
    
    print("\n📊 Comparison Results:")
    for provider, result in results.items():
        print(f"\n{provider}:")
        if "data" in result:
            print(f"  Topic: {result['data']['analysis']['main_topic']}")
            print(f"  Complexity: {result['data']['analysis']['complexity_level']}")
            print(f"  Insights: {len(result['data']['analysis']['key_insights'])} found")
        print(f"  Response Time: {result['response_time']}s")


def failover_strategy():
    """Demonstrate failover between providers."""
    print("🔄 Provider Failover Strategy")
    print("-" * 30)
    
    schema = {
        "task_completion": {
            "status": "string",
            "provider_used": "string",
            "attempts": "int",
            "data": {
                "summary": "string",
                "word_count": "int"
            }
        }
    }
    
    text = "This is a test document for failover demonstration."
    
    # Providers in order of preference (including invalid one for demo)
    provider_chain = [
        {"provider": "invalid_provider", "model": "test"},  # Will fail
        {"provider": "ollama", "model": "nonexistent:model"},  # Will likely fail
        {"provider": "openai", "model": "gpt-4"},  # Should work
        {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}  # Backup
    ]
    
    attempts = 0
    for provider_config in provider_chain:
        attempts += 1
        print(f"Attempt {attempts}: Trying {provider_config['provider']}...")
        
        result = call_with_schema_safe(
            f"Summarize and count words in: {text}",
            {"summary": "string", "word_count": "int"},
            provider_config
        )
        
        if result["success"]:
            final_result = {
                "task_completion": {
                    "status": "success",
                    "provider_used": provider_config["provider"],
                    "attempts": attempts,
                    "data": result["data"]
                }
            }
            print(f"✅ Success with {provider_config['provider']}!")
            print(json.dumps(final_result, indent=2))
            break
        else:
            print(f"❌ Failed: {result['error']}")
    else:
        print("❌ All providers failed!")


if __name__ == "__main__":
    print("=== Dynamic BAML Multi-Provider Examples ===\n")
    
    # Check for API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_openrouter = bool(os.getenv("OPENROUTER_API_KEY"))
    
    print("API Key Status:")
    print(f"  OpenAI: {'✅' if has_openai else '❌'}")
    print(f"  Anthropic: {'✅' if has_anthropic else '❌'}")
    print(f"  OpenRouter: {'✅' if has_openrouter else '❌'}")
    print(f"  Ollama: Assuming local installation")
    print()
    
    if has_openai:
        openai_example()
    
    if has_anthropic:
        anthropic_example()
    
    ollama_example()  # Always try Ollama
    
    if has_openrouter:
        openrouter_example()
    
    print("=" * 50)
    provider_comparison()
    
    print("\n" + "=" * 50)
    failover_strategy()
    
    print("\n✅ Multi-provider examples completed!") 