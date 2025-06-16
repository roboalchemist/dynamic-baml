"""
Comprehensive test suite for BAML Executor functionality.

Tests the BAMLExecutor and CompiledSchema classes that handle
BAML schema compilation and response parsing.
"""

import pytest
import json
import uuid
from unittest.mock import patch, MagicMock
from unittest import TestCase

from dynamic_baml.baml_executor import BAMLExecutor, CompiledSchema
from dynamic_baml.exceptions import BAMLCompilationError, ResponseParsingError


class TestBAMLExecutor(TestCase):
    """Test cases for BAMLExecutor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = BAMLExecutor()
        self.sample_baml_code = """
class Person {
    name: string
    age: int
    email: string?
}

enum Status {
    active
    inactive
    pending
}
"""
    
    def test_init(self):
        """Test BAMLExecutor initialization."""
        executor = BAMLExecutor()
        self.assertEqual(executor.compiled_schemas, {})
    
    def test_compile_schema_success(self):
        """Test successful schema compilation."""
        schema_name = "Person"
        
        compiled_schema = self.executor.compile_schema(self.sample_baml_code, schema_name)
        
        # Verify the compiled schema
        self.assertIsInstance(compiled_schema, CompiledSchema)
        self.assertEqual(compiled_schema.schema_name, schema_name)
        self.assertEqual(compiled_schema.baml_code, self.sample_baml_code)
        
        # Verify it's cached
        self.assertIn(schema_name, self.executor.compiled_schemas)
        self.assertEqual(self.executor.compiled_schemas[schema_name], compiled_schema)
    
    def test_compile_schema_with_exception(self):
        """Test schema compilation with parsing exception."""
        # Mock the _parse_baml_schema method to raise an exception
        with patch.object(self.executor, '_parse_baml_schema', side_effect=ValueError("Parse error")):
            with self.assertRaises(BAMLCompilationError) as cm:
                self.executor.compile_schema(self.sample_baml_code, "Person")
            
            self.assertIn("Failed to compile BAML schema 'Person'", str(cm.exception))
            self.assertIn("Parse error", str(cm.exception))
    
    def test_parse_response_with_json(self):
        """Test parsing response with valid JSON."""
        # First compile a schema
        compiled_schema = self.executor.compile_schema(self.sample_baml_code, "Person")
        
        # Mock response with JSON
        json_response = '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
        
        result = self.executor.parse_response(compiled_schema, json_response, "Person")
        
        expected = {"name": "John Doe", "age": 30, "email": "john@example.com"}
        self.assertEqual(result, expected)
    
    def test_parse_response_with_json_blocks(self):
        """Test parsing response with JSON in code blocks."""
        compiled_schema = self.executor.compile_schema(self.sample_baml_code, "Person")
        
        # Response with JSON in markdown code block
        response_with_block = '''
Here's the extracted data:

```json
{
    "name": "Jane Smith",
    "age": 25,
    "email": "jane@example.com"
}
```

That's the result.
'''
        
        result = self.executor.parse_response(compiled_schema, response_with_block, "Person")
        
        expected = {"name": "Jane Smith", "age": 25, "email": "jane@example.com"}
        self.assertEqual(result, expected)
    
    def test_parse_response_structured_text_fallback(self):
        """Test parsing response that falls back to structured text parsing."""
        compiled_schema = self.executor.compile_schema(self.sample_baml_code, "Person")
        
        # Response without JSON
        text_response = """
Name: Bob Wilson
Age: 35
Email: bob@example.com
Status: active
"""
        
        result = self.executor.parse_response(compiled_schema, text_response, "Person")
        
        # Should extract key-value pairs
        self.assertIn("name", result)
        self.assertIn("age", result)
        self.assertIn("email", result)
    
    def test_parse_response_with_exception(self):
        """Test parse response with exception handling."""
        compiled_schema = self.executor.compile_schema(self.sample_baml_code, "Person")
        
        # Mock methods to raise exceptions
        with patch.object(self.executor, '_extract_json_from_response', side_effect=ValueError("JSON error")):
            with self.assertRaises(ResponseParsingError) as cm:
                self.executor.parse_response(compiled_schema, "invalid", "Person")
            
            self.assertIn("Failed to parse response for schema 'Person'", str(cm.exception))
    
    def test_parse_baml_schema_classes(self):
        """Test parsing BAML schema with class definitions."""
        baml_code = """
class User {
    id: int
    username: string
    active: bool?
}

class Profile {
    bio: string
    website: string?
}
"""
        
        result = self.executor._parse_baml_schema(baml_code, "User")
        
        # Check User class structure
        self.assertIn("User", result)
        user_fields = result["User"]
        self.assertEqual(user_fields["id"]["type"], "int")
        self.assertEqual(user_fields["username"]["type"], "string")
        self.assertEqual(user_fields["active"]["type"], "bool")
        self.assertTrue(user_fields["active"]["optional"])
        
        # Check Profile class structure
        self.assertIn("Profile", result)
        profile_fields = result["Profile"]
        self.assertEqual(profile_fields["bio"]["type"], "string")
        self.assertEqual(profile_fields["website"]["type"], "string")
        self.assertTrue(profile_fields["website"]["optional"])
    
    def test_parse_baml_schema_enums(self):
        """Test parsing BAML schema with enum definitions."""
        baml_code = """
enum Priority {
    low
    medium
    high
    critical
}

enum Type {
    task
    bug
    feature
}
"""
        
        result = self.executor._parse_baml_schema(baml_code, "Priority")
        
        # Check Priority enum
        self.assertIn("Priority", result)
        priority_enum = result["Priority"]
        self.assertEqual(priority_enum["_type"], "enum")
        self.assertIn("low", priority_enum["values"])
        self.assertIn("medium", priority_enum["values"])
        self.assertIn("high", priority_enum["values"])
        self.assertIn("critical", priority_enum["values"])
        
        # Check Type enum
        self.assertIn("Type", result)
        type_enum = result["Type"]
        self.assertEqual(type_enum["_type"], "enum")
        self.assertIn("task", type_enum["values"])
        self.assertIn("bug", type_enum["values"])
        self.assertIn("feature", type_enum["values"])
    
    def test_extract_json_from_response_various_formats(self):
        """Test JSON extraction from various response formats."""
        # Test case 1: JSON in ```json block
        response1 = '''
Here's the data:
```json
{"name": "Test", "value": 123}
```
Done.
'''
        result1 = self.executor._extract_json_from_response(response1)
        self.assertEqual(result1, {"name": "Test", "value": 123})
        
        # Test case 2: JSON in generic ``` block
        response2 = '''
```
{"status": "success", "count": 5}
```
'''
        result2 = self.executor._extract_json_from_response(response2)
        self.assertEqual(result2, {"status": "success", "count": 5})
        
        # Test case 3: Plain JSON
        response3 = '{"simple": "json", "works": true}'
        result3 = self.executor._extract_json_from_response(response3)
        self.assertEqual(result3, {"simple": "json", "works": True})
        
        # Test case 4: JSON embedded in text
        response4 = 'The result is {"embedded": "json"} in this text.'
        result4 = self.executor._extract_json_from_response(response4)
        self.assertEqual(result4, {"embedded": "json"})
        
        # Test case 5: No valid JSON
        response5 = 'This has no JSON content at all.'
        result5 = self.executor._extract_json_from_response(response5)
        self.assertIsNone(result5)
        
        # Test case 6: Invalid JSON
        response6 = '{"invalid": json, "missing": quotes}'
        result6 = self.executor._extract_json_from_response(response6)
        self.assertIsNone(result6)
    
    def test_validate_against_schema_success(self):
        """Test successful schema validation."""
        data = {"name": "Test", "age": 25}
        schema = {"name": {"type": "string"}, "age": {"type": "int"}}
        
        result = self.executor._validate_against_schema(data, schema)
        self.assertEqual(result, data)
    
    def test_validate_against_schema_invalid_data_type(self):
        """Test schema validation with invalid data type."""
        invalid_data = "not a dictionary"
        schema = {"name": {"type": "string"}}
        
        with self.assertRaises(ValueError) as cm:
            self.executor._validate_against_schema(invalid_data, schema)
        
        self.assertIn("Data must be a dictionary", str(cm.exception))
    
    def test_parse_structured_text_various_formats(self):
        """Test structured text parsing with various formats."""
        schema = {"name": {"type": "string"}, "age": {"type": "int"}}
        
        # Test case 1: Simple key-value pairs
        text1 = """
Name: Alice
Age: 30
City: New York
"""
        result1 = self.executor._parse_structured_text(text1, schema)
        self.assertEqual(result1["name"], "Alice")
        self.assertEqual(result1["age"], "30")
        self.assertEqual(result1["city"], "New York")
        
        # Test case 2: Mixed format
        text2 = """
The name is: Bob
Age: 25
Location: Boston
Status: Active
"""
        result2 = self.executor._parse_structured_text(text2, schema)
        self.assertIn("the name is", result2)
        self.assertIn("age", result2)
        
        # Test case 3: No structured content
        text3 = "This is just plain text without any structure"
        result3 = self.executor._parse_structured_text(text3, schema)
        self.assertEqual(result3, {})
        
        # Test case 4: Empty lines and whitespace
        text4 = """

Name:   Charlie   
Age:    40   

Email:  charlie@example.com  

"""
        result4 = self.executor._parse_structured_text(text4, schema)
        self.assertEqual(result4["name"], "Charlie")
        self.assertEqual(result4["age"], "40")
        self.assertEqual(result4["email"], "charlie@example.com")


class TestCompiledSchema(TestCase):
    """Test cases for CompiledSchema class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.schema_name = "TestSchema"
        self.baml_code = "class TestSchema { name: string }"
        self.parsed_structure = {
            "TestSchema": {
                "name": {"type": "string", "optional": False}
            }
        }
    
    def test_init(self):
        """Test CompiledSchema initialization."""
        compiled_schema = CompiledSchema(
            self.schema_name, 
            self.baml_code, 
            self.parsed_structure
        )
        
        self.assertEqual(compiled_schema.schema_name, self.schema_name)
        self.assertEqual(compiled_schema.baml_code, self.baml_code)
        self.assertEqual(compiled_schema.parsed_structure, self.parsed_structure)
        
        # Check that ID is generated
        self.assertIsInstance(compiled_schema.id, str)
        # Verify it's a valid UUID format
        uuid.UUID(compiled_schema.id)  # This will raise if invalid
    
    def test_get_main_class_structure_exists(self):
        """Test getting main class structure when it exists."""
        compiled_schema = CompiledSchema(
            self.schema_name, 
            self.baml_code, 
            self.parsed_structure
        )
        
        result = compiled_schema.get_main_class_structure()
        expected = {"name": {"type": "string", "optional": False}}
        self.assertEqual(result, expected)
    
    def test_get_main_class_structure_missing(self):
        """Test getting main class structure when schema doesn't exist."""
        compiled_schema = CompiledSchema(
            "NonExistentSchema", 
            self.baml_code, 
            self.parsed_structure
        )
        
        result = compiled_schema.get_main_class_structure()
        self.assertEqual(result, {})


class TestBAMLExecutorIntegration(TestCase):
    """Integration tests for BAMLExecutor with complex scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = BAMLExecutor()
    
    def test_complex_schema_compilation_and_parsing(self):
        """Test end-to-end compilation and parsing with complex schema."""
        complex_baml = """
class Product {
    id: int
    name: string
    price: float
    category: Category
    tags: string[]
    available: bool?
}

class Category {
    name: string
    description: string?
}

enum ProductStatus {
    in_stock
    out_of_stock
    discontinued
}
"""
        
        # Compile the schema
        compiled_schema = self.executor.compile_schema(complex_baml, "Product")
        
        # Test with JSON response
        json_response = '''
{
    "id": 123,
    "name": "Laptop",
    "price": 999.99,
    "category": {"name": "Electronics", "description": "Tech products"},
    "tags": ["computer", "work", "portable"],
    "available": true
}
'''
        
        result = self.executor.parse_response(compiled_schema, json_response, "Product")
        
        self.assertEqual(result["id"], 123)
        self.assertEqual(result["name"], "Laptop")
        self.assertEqual(result["price"], 999.99)
        self.assertIsInstance(result["category"], dict)
        self.assertIsInstance(result["tags"], list)
    
    def test_multiple_schemas_caching(self):
        """Test that multiple compiled schemas are properly cached."""
        schema1_code = "class User { name: string }"
        schema2_code = "class Product { title: string }"
        
        # Compile multiple schemas
        compiled1 = self.executor.compile_schema(schema1_code, "User")
        compiled2 = self.executor.compile_schema(schema2_code, "Product")
        
        # Verify both are cached
        self.assertIn("User", self.executor.compiled_schemas)
        self.assertIn("Product", self.executor.compiled_schemas)
        
        # Verify they're different objects
        self.assertNotEqual(compiled1.id, compiled2.id)
        self.assertNotEqual(compiled1.baml_code, compiled2.baml_code)
    
    def test_error_propagation(self):
        """Test that errors are properly propagated with context."""
        # Test compilation error by mocking _parse_baml_schema to raise an exception
        with patch.object(self.executor, '_parse_baml_schema', side_effect=ValueError("Invalid BAML syntax")):
            with self.assertRaises(BAMLCompilationError) as cm:
                self.executor.compile_schema("invalid baml", "InvalidSchema")
            
            self.assertIn("InvalidSchema", str(cm.exception))
        
        # Test parsing error with valid schema but bad response handling
        valid_schema = self.executor.compile_schema("class Test { name: string }", "Test")
        
        # Mock validation to raise an error
        with patch.object(self.executor, '_validate_against_schema', side_effect=ValueError("Validation failed")):
            with patch.object(self.executor, '_extract_json_from_response', return_value={"name": "test"}):
                with self.assertRaises(ResponseParsingError) as cm:
                    self.executor.parse_response(valid_schema, '{"name": "test"}', "Test")
                
                self.assertIn("Test", str(cm.exception))


if __name__ == "__main__":
    # Run all tests
    import unittest
    unittest.main() 