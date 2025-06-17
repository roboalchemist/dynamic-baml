import os
import pytest
import base64
import mimetypes
from baml_py import BamlRuntime, Image, ClientRegistry
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict, Any
import enum
import types
import sys
from types import ModuleType

# Import the dynamic BAML library
from dynamic_baml import call_with_schema, call_with_schema_safe

load_dotenv()

# Define the enums and classes at module level for BAML runtime
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

def image_to_base64(image_path):
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = 'application/octet-stream'
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return mime_type, encoded_string

@pytest.mark.asyncio
@pytest.mark.parametrize("provider", ["openrouter", "ollama"])
async def test_analyze_person_truly_dynamic(provider):
    """Test image analysis using truly dynamic BAML with schema defined as dictionary."""
    
    # Define the schema as a pure dictionary
    person_schema = {
        "age": "int",
        "gender": {
            "type": "enum",
            "values": ["male", "female", "other"]
        },
        "hair_color": {
            "type": "enum", 
            "values": ["black", "brown", "blonde", "red", "gray", "white", "other"]
        },
        "description": "string"
    }
    
    # Set up provider options
    if provider == "ollama":
        options = {
            "provider": "ollama",
            "model": "gemma3:4b"
        }
    else:  # openrouter
        options = {
            "provider": "openrouter",
            "model": "google/gemini-2.5-pro-preview"
        }
    
    # For text-based testing, we'll use a descriptive prompt
    # (The current dynamic BAML doesn't support image inputs yet)
    prompt = """
    Analyze this person and provide their details:
    - A young woman with long blonde hair
    - Appears to be in her mid-20s
    - Wearing casual clothing
    
    Extract:
    - Their approximate age (as an integer)
    - Their gender (male, female, or other)
    - Their hair color
    - A brief description
    
    Respond with a JSON object matching the required schema.
    """
    
    # Call with the dynamic schema
    result = call_with_schema_safe(prompt, person_schema, options)
    
    # Verify the result
    assert result["success"], f"Failed to analyze: {result.get('error')}"
    data = result["data"]
    
    # Validate the response structure
    assert isinstance(data["age"], int)
    assert data["gender"] in ["MALE", "FEMALE", "OTHER"]
    assert data["hair_color"] in ["BLACK", "BROWN", "BLONDE", "RED", "GRAY", "WHITE", "OTHER"]
    assert isinstance(data["description"], str)

# Also test the existing approach for comparison
@pytest.mark.asyncio
async def test_analyze_person_with_baml_runtime():
    """Test using BamlRuntime directly with programmatic schema."""
    
    # Define BAML schema as string
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
      client TestClient
      prompt #"
        Analyze the image and extract the person's information.
        
        You must respond with a JSON object that has EXACTLY these fields:
        - age: (integer) the person's estimated age
        - gender: (string) must be exactly "Male", "Female", or "Other"
        - hair_color: (string) must be exactly one of "Black", "Brown", "Blonde", "Red", "Gray", "White", or "Other"
        - description: (string) a brief description of the person
        
        Do not include any other fields. The field names must match exactly.
        
        Image:
        {{ image }}
      "#
    }
    
    client<llm> TestClient {
      provider openai-generic
      options {
        model "gemma3:4b"
        base_url "http://localhost:11434/v1"
      }
    }
    """
    
    # Create runtime from files with client config included
    runtime = BamlRuntime.from_files(
        root_path=os.path.dirname(__file__),
        files={"schema.baml": baml_schema},
        env_vars=dict(os.environ)
    )
    
    # Test with first image
    image_path = os.path.join(os.path.dirname(__file__), 'test-data', 'person1.jpg')
    media_type, base64_data = image_to_base64(image_path)
    image = Image.from_base64(media_type, base64_data)
    
    ctx = runtime.create_context_manager()
    result = await runtime.call_function(
        "AnalyzePerson",
        {"image": image},
        ctx,
        None,  # tb
        None,  # cr
        []     # collectors
    )
    
    # Cast result to Person type
    # Use the current module for cast_to
    current_module = sys.modules[__name__]
    
    person = result.cast_to(
        current_module,  # enum_module
        current_module,  # class_module
        current_module,  # partial_class_module (same as class_module)
        False  # allow_partials
    )
    
    assert isinstance(person, Person)
    assert isinstance(person.age, int)
    assert isinstance(person.gender, Gender)
    assert isinstance(person.hair_color, HairColor)
    assert isinstance(person.description, str) 