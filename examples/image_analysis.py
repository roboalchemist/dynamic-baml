#!/usr/bin/env python3
"""
Example of using dynamic-baml with images for multimodal AI analysis.

This example demonstrates:
1. Analyzing images with OpenRouter (cloud-based)
2. Analyzing images with Ollama (local)
3. Using BamlRuntime for more complex schemas
4. Error handling and fallback strategies
"""

import os
import base64
import mimetypes
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
from baml_py import BamlRuntime, Image
from pydantic import BaseModel
import enum

# Import dynamic BAML
from dynamic_baml import call_with_schema, call_with_schema_safe

# Load environment variables
load_dotenv()


def image_to_base64(image_path: str) -> tuple[str, str]:
    """Convert an image file to base64 encoding."""
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'
    
    with open(image_path, 'rb') as f:
        base64_data = base64.b64encode(f.read()).decode('utf-8')
    
    return mime_type, base64_data


def analyze_image_simple(image_path: str):
    """Simple image analysis using dynamic schema (text-based prompt)."""
    print(f"\n🔍 Analyzing {image_path} with simple dynamic schema...")
    
    # Define a simple schema for person analysis
    person_schema = {
        "age": "int",
        "gender": {"type": "enum", "values": ["male", "female", "other"]},
        "hair_color": {"type": "enum", "values": ["black", "brown", "blonde", "red", "gray", "white", "other"]},
        "description": "string"
    }
    
    # Since dynamic BAML doesn't support image inputs directly yet,
    # we'll use a text-based prompt describing what we want
    prompt = f"""
    Analyze the following image and extract information about the person.
    
    Provide:
    - age: estimated age as an integer
    - gender: one of male, female, or other
    - hair_color: one of black, brown, blonde, red, gray, white, or other
    - description: a brief description of the person
    
    Note: This is a demonstration. In a real scenario with image support,
    the image would be passed directly to the model.
    
    For this demo, assume you're analyzing a person with:
    - Appears to be in their 30s
    - Female presenting
    - Brown hair
    - Professional appearance
    """
    
    # Try with OpenRouter first
    if os.getenv("OPENROUTER_API_KEY"):
        try:
            result = call_with_schema(
                prompt_text=prompt,
                schema_dict=person_schema,
                options={
                    "provider": "openrouter",
                    "model": "google/gemini-2.5-flash-preview-05-20",
                    "temperature": 0.1
                }
            )
            print(f"✅ OpenRouter Analysis Result:")
            print(f"   Age: {result['age']}")
            print(f"   Gender: {result['gender']}")
            print(f"   Hair Color: {result['hair_color']}")
            print(f"   Description: {result['description']}")
            return result
        except Exception as e:
            print(f"❌ OpenRouter failed: {e}")
    
    # Fallback to Ollama
    print("🔄 Trying with Ollama...")
    try:
        result = call_with_schema(
            prompt_text=prompt,
            schema_dict=person_schema,
            options={
                "provider": "ollama",
                "model": "gemma2:2b",
                "temperature": 0.1
            }
        )
        print(f"✅ Ollama Analysis Result:")
        print(f"   Age: {result['age']}")
        print(f"   Gender: {result['gender']}")
        print(f"   Hair Color: {result['hair_color']}")
        print(f"   Description: {result['description']}")
        return result
    except Exception as e:
        print(f"❌ Ollama failed: {e}")
        return None


# Define enums and classes for BamlRuntime approach
class Gender(enum.Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"

class HairColor(enum.Enum):
    Black = "Black"
    Brown = "Brown"
    Blonde = "Blonde"
    Red = "Red"
    Gray = "Gray"
    White = "White"
    Other = "Other"

class Person(BaseModel):
    age: int
    gender: Gender
    hair_color: HairColor
    description: str


async def analyze_image_with_baml_runtime(image_path: str):
    """Advanced image analysis using BamlRuntime with actual image support."""
    print(f"\n🔬 Analyzing {image_path} with BamlRuntime (actual image support)...")
    
    # Convert image to base64
    mime_type, base64_data = image_to_base64(image_path)
    image = Image.from_base64(mime_type, base64_data)
    
    # Define BAML schema with proper image support
    baml_schema = """
    enum Gender {
      Male
      Female
      Other
    }
    
    enum HairColor {
      Black
      Brown
      Blonde
      Red
      Gray
      White
      Other
    }
    
    class Person {
      age int
      gender Gender
      hair_color HairColor
      description string
    }
    
    function AnalyzePerson(image: image) -> Person {
      client ImageAnalysisClient
      prompt #"
        Analyze this image and extract information about the person.
        
        You must respond with a JSON object that has EXACTLY these fields:
        - age: (integer) the person's estimated age - MUST be a number only, like 25 or 30
        - gender: (string) must be exactly "Male", "Female", or "Other"
        - hair_color: (string) must be exactly one of "Black", "Brown", "Blonde", "Red", "Gray", "White", or "Other"
        - description: (string) a brief description of the person
        
        Important: The age field MUST be an integer number only. Do not include text like "approximately" or ranges.
        
        Image: {{ image }}
      "#
    }
    
    // Fallback client configuration
    client<llm> ImageAnalysisClient {
      provider fallback
      options {
        strategy [OllamaVision, OpenRouterVision]
      }
    }
    
    client<llm> OllamaVision {
      provider openai-generic
      options {
        model "llava:latest"
        base_url "http://localhost:11434/v1"
      }
    }
    
    client<llm> OpenRouterVision {
      provider openai-generic
      options {
        model "google/gemini-2.5-flash-preview-05-20"
        base_url "https://openrouter.ai/api/v1"
        api_key env.OPENROUTER_API_KEY
      }
    }
    """
    
    try:
        # Create runtime
        runtime = BamlRuntime.from_files(
            root_path=os.path.dirname(__file__),
            files={"schema.baml": baml_schema},
            env_vars=dict(os.environ)
        )
        
        # Call the function
        ctx = runtime.create_context_manager()
        result = await runtime.call_function(
            "AnalyzePerson",
            {"image": image},
            ctx,
            None,  # tb
            None,  # cr
            []     # collectors
        )
        
        # Cast to Person type
        import sys
        current_module = sys.modules[__name__]
        person = result.cast_to(
            current_module,  # enum_module
            current_module,  # class_module
            current_module,  # partial_class_module
            False  # allow_partials
        )
        
        print(f"✅ BamlRuntime Analysis Result:")
        print(f"   Age: {person.age}")
        print(f"   Gender: {person.gender.value}")
        print(f"   Hair Color: {person.hair_color.value}")
        print(f"   Description: {person.description}")
        return person
        
    except Exception as e:
        print(f"❌ BamlRuntime analysis failed: {e}")
        return None


def main():
    """Run the image analysis examples."""
    print("=" * 60)
    print("Dynamic BAML Image Analysis Examples")
    print("=" * 60)
    
    # Check for test images
    test_images_dir = Path(__file__).parent.parent / "tests" / "test-data"
    if not test_images_dir.exists():
        print("⚠️  Test images directory not found.")
        print("   Please ensure test images are available in tests/test-data/")
        return
    
    # Get first available test image
    test_images = list(test_images_dir.glob("*.jpg")) + list(test_images_dir.glob("*.png"))
    if not test_images:
        print("⚠️  No test images found in tests/test-data/")
        return
    
    test_image = str(test_images[0])
    print(f"\n📸 Using test image: {test_image}")
    
    # Example 1: Simple dynamic schema (text-based)
    result1 = analyze_image_simple(test_image)
    
    # Example 2: BamlRuntime with actual image support
    # Note: This requires vision models to be available
    print("\n" + "=" * 40)
    print("Note: BamlRuntime example requires vision-capable models.")
    print("Make sure you have either:")
    print("- Ollama with llava model installed")
    print("- OpenRouter API key set")
    print("=" * 40)
    
    # Run async example
    import asyncio
    asyncio.run(analyze_image_with_baml_runtime(test_image))
    
    print("\n✨ Examples completed!")
    print("\nKey Takeaways:")
    print("1. Dynamic BAML currently works best with text-based prompts")
    print("2. For actual image support, use BamlRuntime with vision models")
    print("3. Always implement fallback strategies for robustness")
    print("4. Consider both cloud (OpenRouter) and local (Ollama) options")


if __name__ == "__main__":
    main() 