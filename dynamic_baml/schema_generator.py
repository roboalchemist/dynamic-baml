"""
Dynamic BAML schema generator from dictionary definitions.
"""

from typing import Any, Dict, List, Union, Tuple
from .exceptions import SchemaGenerationError
from .types import SchemaDict, ComplexSchemaField


class DictToBAMLGenerator:
    """Generates BAML schema code from dictionary definitions."""
    
    def __init__(self):
        self.indent_level = 0
        self.generated_classes = set()
    
    def generate_schema(self, schema_dict: SchemaDict, schema_name: str) -> str:
        """
        Generate complete BAML schema code from dictionary.
        
        Args:
            schema_dict: Dictionary defining the schema structure
            schema_name: Name for the main schema class
            
        Returns:
            Valid BAML schema code as string (classes and enums only)
        """
        try:
            self.generated_classes.clear()
            self.indent_level = 0
            
            # Generate the main class and any nested classes/enums
            baml_code = self._generate_class(schema_dict, schema_name)
            
            return baml_code
            
        except Exception as e:
            raise SchemaGenerationError(
                f"Failed to generate BAML schema: {str(e)}", 
                schema_dict
            ) from e
    
    def _generate_class(self, schema_dict: Dict[str, Any], class_name: str) -> str:
        """Generate a BAML class definition from dictionary."""
        if class_name in self.generated_classes:
            return ""
        
        self.generated_classes.add(class_name)
        
        lines = [f"class {class_name} {{"]
        
        for field_name, field_def in schema_dict.items():
            # Skip None values gracefully
            if field_def is None:
                continue
                
            field_type, optional = self._parse_field_definition(field_def, field_name)
            
            if optional:
                lines.append(f"  {field_name} {field_type}?")
            else:
                lines.append(f"  {field_name} {field_type}")
        
        lines.append("}")
        
        # Generate any nested classes first (before the main class)
        nested_classes = []
        for field_name, field_def in schema_dict.items():
            # Skip None values in nested class generation too
            if field_def is None:
                continue
                
            nested_class_code = self._generate_nested_classes(field_def, field_name)
            if nested_class_code:
                nested_classes.append(nested_class_code)
        
        # Combine nested classes with main class
        result = "\n".join(nested_classes)
        if nested_classes:
            result += "\n\n"
        result += "\n".join(lines)
        
        return result
    
    def _parse_field_definition(self, field_def: Any, field_name: str) -> Tuple[str, bool]:
        """
        Parse field definition and return (type_string, is_optional).
        
        Args:
            field_def: Field definition from dictionary
            field_name: Name of the field
            
        Returns:
            Tuple of (BAML type string, is_optional)
        """
        optional = False
        
        # Handle optional field definitions
        if isinstance(field_def, dict) and "optional" in field_def:
            optional = field_def.get("optional", False)
            if "type" in field_def:
                field_def = field_def["type"]
        
        # Handle enum definitions
        if isinstance(field_def, dict) and field_def.get("type") == "enum":
            enum_name = f"{field_name.title()}Enum"
            return enum_name, optional
        
        # Handle basic types
        if isinstance(field_def, str):
            return self._map_basic_type(field_def), optional
        
        # Handle array types
        if isinstance(field_def, list) and len(field_def) == 1:
            element_type = self._map_basic_type(field_def[0])
            return f"{element_type}[]", optional
        
        # Handle nested object types
        if isinstance(field_def, dict):
            nested_class_name = f"{field_name.title()}Class"
            return nested_class_name, optional
        
        raise SchemaGenerationError(f"Unknown field definition type: {type(field_def)}")
    
    def _map_basic_type(self, type_str: str) -> str:
        """Map Python type strings to BAML types."""
        type_mapping = {
            "string": "string",
            "str": "string",
            "int": "int",
            "integer": "int", 
            "float": "float",
            "double": "float",
            "bool": "bool",
            "boolean": "bool"
        }
        
        return type_mapping.get(type_str, "string")  # Default to string
    
    def _generate_nested_classes(self, field_def: Any, field_name: str) -> str:
        """Generate nested class definitions for complex field types."""
        result = ""
        
        # Generate enum classes
        if isinstance(field_def, dict) and field_def.get("type") == "enum":
            enum_name = f"{field_name.title()}Enum"
            values = field_def.get("values", [])
            result += f"enum {enum_name} {{\n"
            for value in values:
                # Convert to uppercase for BAML enum format
                enum_value = value.upper().replace("-", "_").replace(" ", "_")
                result += f"  {enum_value}\n"
            result += "}\n"
        
        # Generate nested object classes
        elif isinstance(field_def, dict) and "type" not in field_def:
            # This is a nested object definition
            nested_class_name = f"{field_name.title()}Class"
            result += self._generate_class(field_def, nested_class_name)
        
        # Handle optional field with nested definition
        elif isinstance(field_def, dict) and "type" in field_def and field_def["type"] not in ["enum"]:
            # Check if the type itself is a nested object
            type_def = field_def["type"]
            if isinstance(type_def, dict):
                nested_class_name = f"{field_name.title()}Class"
                result += self._generate_class(type_def, nested_class_name)
        
        return result 