#!/usr/bin/env python3
"""
Basic Usage Example for Dynamic BAML

This example demonstrates the simplest use case:
- Define a schema with basic types
- Extract structured data from unstructured text
- Handle results
"""

from dynamic_baml import call_with_schema, call_with_schema_safe
import os

def basic_extraction():
    """Simple data extraction example."""
    
    # Define what we want to extract
    schema = {
        "name": "string",
        "age": "int",
        "email": "string",
        "is_active": "bool"
    }
    
    # Sample text to analyze
    text = """
    John Doe is a 30-year-old software engineer. His email address is 
    john.doe@techcorp.com and he is currently an active employee.
    """
    
    # Extract structured data
    options = {"provider": "openai", "model": "gpt-4"}
    
    try:
        result = call_with_schema(
            prompt_text=f"Extract user information from the following text: {text}",
            schema_dict=schema,
            options=options
        )
        
        print("✅ Extraction successful!")
        print(f"Name: {result['name']}")
        print(f"Age: {result['age']}")
        print(f"Email: {result['email']}")
        print(f"Active: {result['is_active']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def safe_extraction():
    """Example using safe calling (no exceptions)."""
    
    schema = {
        "product": "string",
        "price": "float",
        "in_stock": "bool",
        "category": "string"
    }
    
    text = """
    The iPhone 15 Pro costs $999.99 and is currently available for purchase.
    It belongs to the smartphones category.
    """
    
    options = {"provider": "openai", "model": "gpt-4"}
    
    result = call_with_schema_safe(
        prompt_text=f"Extract product information: {text}",
        schema_dict=schema,
        options=options
    )
    
    if result["success"]:
        data = result["data"]
        print("✅ Safe extraction successful!")
        print(f"Product: {data['product']}")
        print(f"Price: ${data['price']}")
        print(f"In Stock: {data['in_stock']}")
        print(f"Category: {data['category']}")
    else:
        print(f"❌ Extraction failed: {result['error']}")
        print(f"Error type: {result['error_type']}")

def multiple_providers_example():
    """Example showing how to try multiple providers."""
    
    schema = {
        "title": "string",
        "author": "string",
        "year": "int",
        "pages": "int"
    }
    
    text = """
    "The Great Gatsby" was written by F. Scott Fitzgerald in 1925.
    The novel is 180 pages long and is considered a classic of American literature.
    """
    
    # Try multiple providers in order of preference
    providers = [
        {"provider": "openai", "model": "gpt-4"},
        {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
        {"provider": "ollama", "model": "gemma3:1b"}
    ]
    
    for provider_options in providers:
        result = call_with_schema_safe(
            prompt_text=f"Extract book information: {text}",
            schema_dict=schema,
            options=provider_options
        )
        
        if result["success"]:
            data = result["data"]
            print(f"✅ Success with {provider_options['provider']}!")
            print(f"Title: {data['title']}")
            print(f"Author: {data['author']}")
            print(f"Year: {data['year']}")
            print(f"Pages: {data['pages']}")
            break
        else:
            print(f"❌ Failed with {provider_options['provider']}: {result['error']}")

if __name__ == "__main__":
    print("=== Dynamic BAML Basic Usage Examples ===\n")
    
    print("1. Basic Extraction:")
    basic_extraction()
    
    print("\n2. Safe Extraction (No Exceptions):")
    safe_extraction()
    
    print("\n3. Multiple Providers:")
    multiple_providers_example() 