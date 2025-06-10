"""
BAML compilation and execution engine.
"""

import json
import re
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from .exceptions import BAMLCompilationError, ResponseParsingError
from .types import ResponseData


class BAMLExecutor:
    """Handles BAML schema compilation and response parsing."""
    
    def __init__(self):
        self.compiled_schemas = {}
    
    def compile_schema(self, baml_code: str, schema_name: str) -> 'CompiledSchema':
        """
        Compile BAML schema code into executable form.
        
        Args:
            baml_code: Generated BAML schema code
            schema_name: Name of the main schema class
            
        Returns:
            Compiled schema object for parsing responses
        """
        try:
            # For now, we'll use a simplified approach without the full BAML compiler
            # Parse the BAML code to understand the structure
            parsed_schema = self._parse_baml_schema(baml_code, schema_name)
            
            compiled_schema = CompiledSchema(
                schema_name=schema_name,
                baml_code=baml_code,
                parsed_structure=parsed_schema
            )
            
            # Cache the compiled schema
            self.compiled_schemas[schema_name] = compiled_schema
            
            return compiled_schema
            
        except Exception as e:
            raise BAMLCompilationError(
                f"Failed to compile BAML schema '{schema_name}': {str(e)}",
                baml_code
            ) from e
    
    def parse_response(self, compiled_schema: 'CompiledSchema', 
                      raw_response: str, schema_name: str) -> ResponseData:
        """
        Parse LLM response using compiled BAML schema.
        
        Args:
            compiled_schema: Compiled schema for parsing
            raw_response: Raw response text from LLM
            schema_name: Name of the schema to use
            
        Returns:
            Structured data matching the schema
        """
        try:
            # First try to extract JSON from the response
            json_data = self._extract_json_from_response(raw_response)
            
            if json_data:
                # Validate and transform the JSON data according to schema
                parsed_data = self._validate_against_schema(
                    json_data, 
                    compiled_schema.parsed_structure
                )
                return parsed_data
            
            # If no JSON found, try to parse as structured text
            parsed_data = self._parse_structured_text(
                raw_response, 
                compiled_schema.parsed_structure
            )
            
            return parsed_data
            
        except Exception as e:
            raise ResponseParsingError(
                f"Failed to parse response for schema '{schema_name}': {str(e)}",
                raw_response,
                schema_name
            ) from e
    
    def _parse_baml_schema(self, baml_code: str, schema_name: str) -> Dict[str, Any]:
        """Parse BAML code to understand the schema structure."""
        schema_structure = {}
        
        # Extract class definitions
        class_pattern = r'class\s+(\w+)\s*\{\s*([^}]+)\s*\}'
        classes = re.findall(class_pattern, baml_code, re.MULTILINE | re.DOTALL)
        
        for class_name, class_body in classes:
            fields = {}
            
            # Extract field definitions
            field_pattern = r'(\w+):\s*([^?\n]+)(\?)?'
            field_matches = re.findall(field_pattern, class_body)
            
            for field_name, field_type, optional_marker in field_matches:
                fields[field_name] = {
                    "type": field_type.strip(),
                    "optional": bool(optional_marker)
                }
            
            schema_structure[class_name] = fields
        
        # Extract enum definitions
        enum_pattern = r'enum\s+(\w+)\s*\{\s*([^}]+)\s*\}'
        enums = re.findall(enum_pattern, baml_code, re.MULTILINE | re.DOTALL)
        
        for enum_name, enum_body in enums:
            values = [
                value.strip() 
                for value in enum_body.split('\n') 
                if value.strip()
            ]
            schema_structure[enum_name] = {
                "_type": "enum",
                "values": values
            }
        
        return schema_structure
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract JSON object from LLM response text."""
        # Try to find JSON blocks
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',
            r'```\s*(\{.*?\})\s*```',
            r'(\{.*?\})',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # Try to parse the entire response as JSON
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            return None
    
    def _validate_against_schema(self, data: Dict[str, Any], 
                                schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and transform data according to schema structure."""
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        # For now, return the data as-is with basic validation
        # In a full implementation, this would check types, enums, etc.
        return data
    
    def _parse_structured_text(self, text: str, 
                              schema: Dict[str, Any]) -> Dict[str, Any]:
        """Parse structured text response when no JSON is found."""
        # This is a simplified parser - in practice, this would be more sophisticated
        result = {}
        
        # Try to extract key-value pairs from text
        lines = text.split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key and value:
                    result[key] = value
        
        return result


class CompiledSchema:
    """Represents a compiled BAML schema."""
    
    def __init__(self, schema_name: str, baml_code: str, parsed_structure: Dict[str, Any]):
        self.schema_name = schema_name
        self.baml_code = baml_code
        self.parsed_structure = parsed_structure
        self.id = str(uuid.uuid4())
    
    def get_main_class_structure(self) -> Dict[str, Any]:
        """Get the structure of the main schema class."""
        return self.parsed_structure.get(self.schema_name, {}) 