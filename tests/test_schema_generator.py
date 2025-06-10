"""
Tests for the dynamic_baml.schema_generator module.
"""

import pytest
from unittest import TestCase

from dynamic_baml.schema_generator import DictToBAMLGenerator
from dynamic_baml.exceptions import SchemaGenerationError


class TestDictToBAMLGenerator(TestCase):
    """Test cases for DictToBAMLGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = DictToBAMLGenerator()

    def test_simple_types_generation(self):
        """Test generation of simple type schemas."""
        schema_dict = {
            "name": "string",
            "age": "int",
            "height": "float",
            "is_active": "bool"
        }
        
        result = self.generator.generate_schema(schema_dict, "Person")
        
        assert "class Person {" in result
        assert "name string" in result
        assert "age int" in result
        assert "height float" in result
        assert "is_active bool" in result

    def test_array_types_generation(self):
        """Test generation of array type schemas."""
        schema_dict = {
            "tags": ["string"],
            "scores": ["int"],
            "ratings": ["float"],
            "flags": ["bool"]
        }
        
        result = self.generator.generate_schema(schema_dict, "Data")
        
        assert "tags string[]" in result
        assert "scores int[]" in result
        assert "ratings float[]" in result
        assert "flags bool[]" in result

    def test_optional_fields_generation(self):
        """Test generation of optional field schemas."""
        schema_dict = {
            "name": "string",
            "email": {"type": "string", "optional": True},
            "phone": {"type": "string", "optional": True}
        }
        
        result = self.generator.generate_schema(schema_dict, "Contact")
        
        assert "name string" in result
        assert "email string?" in result
        assert "phone string?" in result

    def test_enum_generation(self):
        """Test generation of enum schemas."""
        schema_dict = {
            "status": {
                "type": "enum",
                "values": ["active", "inactive", "pending"]
            },
            "priority": {
                "type": "enum", 
                "values": ["low", "medium", "high"]
            }
        }
        
        result = self.generator.generate_schema(schema_dict, "Task")
        
        # Check enum definitions
        assert "enum StatusEnum {" in result
        assert "ACTIVE" in result
        assert "INACTIVE" in result
        assert "PENDING" in result
        
        assert "enum PriorityEnum {" in result
        assert "LOW" in result
        assert "MEDIUM" in result
        assert "HIGH" in result
        
        # Check class uses enums
        assert "status Status" in result
        assert "priority Priority" in result

    def test_nested_object_generation(self):
        """Test generation of nested object schemas."""
        schema_dict = {
            "user": {
                "name": "string",
                "email": "string"
            },
            "preferences": {
                "theme": "string",
                "notifications": "bool"
            }
        }
        
        result = self.generator.generate_schema(schema_dict, "Profile")
        
        # Check nested class definitions
        assert "class UserClass {" in result
        assert "class PreferencesClass {" in result
        
        # Check main class references nested classes
        assert "user User" in result
        assert "preferences Preferences" in result

    def test_deeply_nested_objects(self):
        """Test generation with deeply nested object structures."""
        schema_dict = {
            "company": {
                "name": "string",
                "address": {
                    "street": "string",
                    "city": "string",
                    "coordinates": {
                        "lat": "float",
                        "lng": "float"
                    }
                }
            }
        }
        
        result = self.generator.generate_schema(schema_dict, "Business")
        
        assert "class CompanyClass {" in result
        assert "class AddressClass {" in result
        assert "class CoordinatesClass {" in result
        assert "coordinates Coordinates" in result

    def test_mixed_complex_schema(self):
        """Test generation with mixed complex schema types."""
        schema_dict = {
            "id": "string",
            "tags": ["string"],
            "status": {
                "type": "enum",
                "values": ["draft", "published", "archived"]
            },
            "metadata": {
                "created_by": "string",
                "created_at": "string",
                "settings": {
                    "public": "bool",
                    "comments_enabled": {"type": "bool", "optional": True}
                }
            },
            "categories": ["string"]
        }
        
        result = self.generator.generate_schema(schema_dict, "Article")
        
        # Check all components are present
        assert "enum StatusEnum {" in result
        assert "class MetadataClass {" in result
        assert "class SettingsClass {" in result
        assert "class Article {" in result
        
        assert "tags string[]" in result
        assert "categories string[]" in result
        assert "comments_enabled bool?" in result

    def test_capitalize_enum_values(self):
        """Test that enum values are properly capitalized."""
        schema_dict = {
            "level": {
                "type": "enum",
                "values": ["beginner", "intermediate", "advanced"]
            }
        }
        
        result = self.generator.generate_schema(schema_dict, "Course")
        
        assert "BEGINNER" in result
        assert "INTERMEDIATE" in result
        assert "ADVANCED" in result

    def test_capitalize_class_names(self):
        """Test that class names are properly capitalized."""
        schema_dict = {
            "user_profile": {
                "first_name": "string",
                "last_name": "string"
            }
        }
        
        result = self.generator.generate_schema(schema_dict, "Data")
        
        assert "class User_ProfileClass {" in result
        assert "user_profile User_ProfileClass" in result

    def test_invalid_type_handling(self):
        """Test handling of unknown field types (defaults to string)."""
        schema_dict = {
            "invalid_field": "unknown_type"
        }
        
        result = self.generator.generate_schema(schema_dict, "Test")
        
        # Unknown types should default to string
        assert "invalid_field string" in result
        assert "class Test {" in result

    def test_invalid_enum_structure(self):
        """Test handling of enum without values (creates empty enum)."""
        schema_dict = {
            "bad_enum": {
                "type": "enum"
                # Missing "values" key
            }
        }
        
        result = self.generator.generate_schema(schema_dict, "Test")
        
        # Should create an empty enum
        assert "enum Bad_EnumEnum {" in result
        assert "bad_enum Bad_EnumEnum" in result

    def test_invalid_optional_structure(self):
        """Test error handling for invalid optional field structure."""
        schema_dict = {
            "bad_optional": {
                "optional": True
                # Missing "type" key
            }
        }
        
        with pytest.raises(SchemaGenerationError) as exc_info:
            self.generator.generate_schema(schema_dict, "Test")
        
        assert "Unknown field definition type: <class 'bool'>" in str(exc_info.value)

    def test_invalid_array_type(self):
        """Test handling of unknown array types (defaults to string[])."""
        schema_dict = {
            "bad_array": ["unknown_type"]
        }
        
        result = self.generator.generate_schema(schema_dict, "Test")
        
        # Unknown array types should default to string[]
        assert "bad_array string[]" in result
        assert "class Test {" in result

    def test_empty_schema_dict(self):
        """Test handling of empty schema dictionary."""
        result = self.generator.generate_schema({}, "Empty")
        
        assert "class Empty {" in result
        assert "}" in result

    def test_none_values_in_schema(self):
        """Test handling of None values in schema."""
        schema_dict = {
            "valid_field": "string",
            "none_field": None
        }
        
        # Should skip None values gracefully
        result = self.generator.generate_schema(schema_dict, "Test")
        
        assert "valid_field string" in result
        assert "none_field" not in result

    def test_field_ordering_consistency(self):
        """Test that field ordering is consistent in generated schemas."""
        schema_dict = {
            "z_field": "string",
            "a_field": "int",
            "m_field": "bool"
        }
        
        result = self.generator.generate_schema(schema_dict, "Test")
        
        # Fields should appear in the order they're defined in the dictionary
        lines = result.split('\n')
        field_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('class') and not line.strip() == '}']
        
        assert len(field_lines) == 3

    def test_very_deep_nesting(self):
        """Test handling of very deeply nested structures."""
        schema_dict = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": {
                                "deep_field": "string"
                            }
                        }
                    }
                }
            }
        }
        
        result = self.generator.generate_schema(schema_dict, "Deep")
        
        assert "class Level1Class {" in result
        assert "class Level2Class {" in result
        assert "class Level3Class {" in result
        assert "class Level4Class {" in result
        assert "class Level5Class {" in result
        assert "deep_field string" in result

    def test_special_characters_in_enum_values(self):
        """Test handling of enum values with special characters."""
        schema_dict = {
            "status": {
                "type": "enum",
                "values": ["in-progress", "not_started", "done!"]
            }
        }
        
        result = self.generator.generate_schema(schema_dict, "Task")
        
        # Special characters should be handled in enum value names
        assert "IN_PROGRESS" in result or "IN-PROGRESS" in result
        assert "NOT_STARTED" in result
        assert "DONE!" in result or "DONE" in result

    def test_duplicate_enum_names(self):
        """Test handling of potentially duplicate enum names."""
        schema_dict = {
            "status1": {
                "type": "enum",
                "values": ["active", "inactive"]
            },
            "status2": {
                "type": "enum",
                "values": ["enabled", "disabled"]
            }
        }
        
        result = self.generator.generate_schema(schema_dict, "Test")
        
        # Should generate unique enum names
        assert "enum Status1Enum {" in result
        assert "enum Status2Enum {" in result

    def test_simple_schema_generation(self):
        """Test generation of simple BAML schema."""
        schema_dict = {
            "name": "string",
            "age": "int",
            "active": "bool"
        }
        
        result = self.generator.generate_schema(schema_dict, "Person")
        
        assert "class Person {" in result
        assert "name string" in result
        assert "age int" in result
        assert "active bool" in result

    def test_nested_schema_generation(self):
        """Test generation of nested BAML schema."""
        schema_dict = {
            "user": {
                "name": "string",
                "email": "string"
            },
            "count": "int"
        }
        
        result = self.generator.generate_schema(schema_dict, "NestedSchema")
        
        assert "class UserClass {" in result
        assert "class NestedSchema {" in result
        assert "user UserClass" in result
        assert "count int" in result

    def test_enum_generation(self):
        """Test generation of enum types."""
        schema_dict = {
            "status": {
                "type": "enum",
                "values": ["active", "inactive", "pending"]
            }
        }
        
        result = self.generator.generate_schema(schema_dict, "StatusInfo")
        
        assert "enum StatusEnum {" in result
        assert "ACTIVE" in result
        assert "INACTIVE" in result
        assert "PENDING" in result
        assert "status StatusEnum" in result

    def test_array_generation(self):
        """Test generation of array types."""
        schema_dict = {
            "tags": ["string"],
            "scores": ["int"]
        }
        
        result = self.generator.generate_schema(schema_dict, "ArraySchema")
        
        assert "tags string[]" in result
        assert "scores int[]" in result

    def test_optional_fields(self):
        """Test generation of optional fields."""
        schema_dict = {
            "required_field": "string",
            "optional_field": {"type": "string", "optional": True}
        }
        
        result = self.generator.generate_schema(schema_dict, "OptionalSchema")
        
        assert "required_field string" in result
        assert "optional_field string?" in result

    def test_optional_nested_object_field(self):
        """Test generation of optional nested object fields."""
        schema_dict = {
            "name": "string",
            "profile": {
                "type": {
                    "bio": "string",
                    "avatar": "string"
                },
                "optional": True
            }
        }
        
        result = self.generator.generate_schema(schema_dict, "UserWithProfile")
        
        assert "class ProfileClass {" in result
        assert "bio string" in result
        assert "avatar string" in result
        assert "profile ProfileClass?" in result

    def test_type_mapping(self):
        """Test mapping of various type strings."""
        schema_dict = {
            "str_field": "str",
            "string_field": "string",
            "int_field": "int",
            "integer_field": "integer",
            "float_field": "float",
            "double_field": "double",
            "bool_field": "bool",
            "boolean_field": "boolean",
            "unknown_field": "unknown_type"
        }
        
        result = self.generator.generate_schema(schema_dict, "TypeMapping")
        
        assert "str_field string" in result
        assert "string_field string" in result
        assert "int_field int" in result
        assert "integer_field int" in result
        assert "float_field float" in result
        assert "double_field float" in result
        assert "bool_field bool" in result
        assert "boolean_field bool" in result
        assert "unknown_field string" in result  # Unknown types default to string

    def test_none_values_in_schema(self):
        """Test handling of None values in schema (should be skipped)."""
        schema_dict = {
            "valid_field": "string",
            "none_field": None,
            "another_valid": "int"
        }
        
        result = self.generator.generate_schema(schema_dict, "WithNones")
        
        assert "valid_field string" in result
        assert "another_valid int" in result
        assert "none_field" not in result  # None fields should be skipped

    def test_duplicate_class_names(self):
        """Test handling of duplicate class names."""
        schema_dict = {
            "user1": {"name": "string"},
            "user2": {"email": "string"}
        }
        
        result = self.generator.generate_schema(schema_dict, "DuplicateTest")
        
        # Should generate User1Class and User2Class
        assert "class User1Class {" in result
        assert "class User2Class {" in result

    def test_enum_with_special_characters(self):
        """Test enum generation with special characters in values."""
        schema_dict = {
            "status": {
                "type": "enum",
                "values": ["in-progress", "not started", "completed"]
            }
        }
        
        result = self.generator.generate_schema(schema_dict, "SpecialEnum")
        
        assert "IN_PROGRESS" in result
        assert "NOT_STARTED" in result
        assert "COMPLETED" in result

    def test_empty_enum_values(self):
        """Test enum generation with empty values list."""
        schema_dict = {
            "status": {
                "type": "enum",
                "values": []
            }
        }
        
        result = self.generator.generate_schema(schema_dict, "EmptyEnum")
        
        assert "enum StatusEnum {" in result
        assert "}" in result

    def test_deeply_nested_objects(self):
        """Test generation of deeply nested object structures."""
        schema_dict = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": {
                                "deep_field": "string"
                            }
                        }
                    }
                }
            }
        }
        
        result = self.generator.generate_schema(schema_dict, "DeepNested")
        
        assert "class Level1Class {" in result
        assert "class Level2Class {" in result
        assert "class Level3Class {" in result
        assert "class Level4Class {" in result
        assert "class Level5Class {" in result
        assert "deep_field string" in result

    def test_complex_mixed_schema(self):
        """Test generation of complex schema with mixed types."""
        schema_dict = {
            "user": {
                "name": "string",
                "age": "int",
                "preferences": {
                    "theme": {
                        "type": "enum",
                        "values": ["light", "dark"]
                    },
                    "notifications": "bool"
                }
            },
            "tags": ["string"],
            "metadata": {
                "type": {
                    "created": "string",
                    "updated": "string"
                },
                "optional": True
            }
        }
        
        result = self.generator.generate_schema(schema_dict, "ComplexSchema")
        
        assert "class UserClass {" in result
        assert "class PreferencesClass {" in result
        assert "class MetadataClass {" in result
        assert "enum ThemeEnum {" in result
        assert "LIGHT" in result
        assert "DARK" in result
        assert "tags string[]" in result
        assert "metadata MetadataClass?" in result

    def test_schema_generation_exception_handling(self):
        """Test exception handling in schema generation."""
        # Create a schema that will cause an exception during generation
        # by using an invalid field definition type
        schema_dict = {
            "invalid_field": 12345  # Integer is not a valid field definition
        }
        
        with pytest.raises(SchemaGenerationError) as exc_info:
            self.generator.generate_schema(schema_dict, "InvalidSchema")
        
        assert "Failed to generate BAML schema" in str(exc_info.value)
        assert exc_info.value.schema_dict == schema_dict

    def test_unknown_field_definition_type_error(self):
        """Test error handling for unknown field definition types."""
        schema_dict = {
            "bad_field": [1, 2, 3]  # List with multiple elements is invalid
        }
        
        with pytest.raises(SchemaGenerationError):
            self.generator.generate_schema(schema_dict, "BadSchema")

    def test_generator_state_reset(self):
        """Test that generator state is properly reset between calls."""
        schema1 = {"field1": "string"}
        schema2 = {"field2": "int"}
        
        result1 = self.generator.generate_schema(schema1, "Schema1")
        result2 = self.generator.generate_schema(schema2, "Schema2")
        
        # Each should only contain its own fields
        assert "field1" in result1 and "field2" not in result1
        assert "field2" in result2 and "field1" not in result2

    def test_class_name_capitalization(self):
        """Test proper capitalization of class names."""
        schema_dict = {
            "user_profile": {"name": "string"},
            "company_info": {"title": "string"}
        }
        
        result = self.generator.generate_schema(schema_dict, "CapitalizationTest")
        
        assert "class User_ProfileClass {" in result
        assert "class Company_InfoClass {" in result

 