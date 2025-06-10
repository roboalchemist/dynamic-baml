"""
Integration tests for dynamic_baml with actual running models.

These tests require:
1. Ollama running locally (ollama serve)
2. gemma3:1b model available (ollama pull gemma3:1b)

Run these tests with: pytest tests/test_integration.py -m integration
"""

import pytest
import json
import time
from unittest import TestCase

from dynamic_baml import call_with_schema, call_with_schema_safe
from dynamic_baml.exceptions import (
    DynamicBAMLError, LLMProviderError, TimeoutError
)
from dynamic_baml.providers import LLMProviderFactory


class TestIntegrationOllamaGemma3(TestCase):
    """Integration tests with actual Ollama Gemma3:1b model."""

    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures and check if Ollama is available."""
        cls.ollama_options = {
            "provider": "ollama",
            "model": "gemma3:1b",
            "temperature": 0.1,
            "timeout": 60
        }
        
        # Check if Ollama is available
        factory = LLMProviderFactory()
        try:
            provider = factory.create_provider(cls.ollama_options)
            if not provider.is_available():
                pytest.skip("Ollama is not running - skipping integration tests")
        except Exception as e:
            pytest.skip(f"Cannot connect to Ollama: {e}")

    @pytest.mark.integration
    def test_basic_string_extraction(self):
        """Test basic string field extraction with real model."""
        schema = {
            "name": "string",
            "city": "string"
        }
        
        prompt = "Extract person info: John Smith lives in San Francisco"
        
        result = call_with_schema(prompt, schema, self.ollama_options)
        
        # Verify structure
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertIn("city", result)
        
        # Verify data types
        self.assertIsInstance(result["name"], str)
        self.assertIsInstance(result["city"], str)
        
        # Basic content verification (should be close to expected)
        self.assertTrue(len(result["name"]) > 0)
        self.assertTrue(len(result["city"]) > 0)

    @pytest.mark.integration
    def test_mixed_types_extraction(self):
        """Test extraction with multiple data types."""
        schema = {
            "name": "string",
            "age": "int",
            "price": "float",
            "active": "bool"
        }
        
        prompt = "Parse: Sarah Johnson, age 28, subscription $19.99 per month, account is active"
        
        result = call_with_schema(prompt, schema, self.ollama_options)
        
        # Verify structure and types
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["name"], str)
        self.assertIsInstance(result["age"], int)
        self.assertIsInstance(result["price"], float)
        self.assertIsInstance(result["active"], bool)
        
        # Verify reasonable values
        self.assertTrue(10 <= result["age"] <= 100)  # Reasonable age range
        self.assertTrue(0 <= result["price"] <= 1000)  # Reasonable price range

    @pytest.mark.integration
    def test_array_extraction(self):
        """Test extraction of array fields."""
        schema = {
            "person": "string",
            "skills": ["string"],
            "scores": ["int"]
        }
        
        prompt = "Employee profile: Mike Chen has skills in Python, JavaScript, SQL and test scores 85, 92, 78"
        
        result = call_with_schema(prompt, schema, self.ollama_options)
        
        # Verify structure
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["person"], str)
        self.assertIsInstance(result["skills"], list)
        self.assertIsInstance(result["scores"], list)
        
        # Verify array contents
        self.assertTrue(len(result["skills"]) > 0)
        self.assertTrue(len(result["scores"]) > 0)
        
        # Verify array element types
        for skill in result["skills"]:
            self.assertIsInstance(skill, str)
        for score in result["scores"]:
            self.assertIsInstance(score, int)

    @pytest.mark.integration
    def test_nested_object_extraction(self):
        """Test extraction with nested objects."""
        schema = {
            "user": {
                "name": "string",
                "age": "int"
            },
            "address": {
                "street": "string",
                "city": "string"
            }
        }
        
        prompt = "User data: Alice Brown, 32 years old, lives at 123 Oak Street in Portland"
        
        result = call_with_schema(prompt, schema, self.ollama_options)
        
        # Verify top-level structure
        self.assertIsInstance(result, dict)
        self.assertIn("user", result)
        self.assertIn("address", result)
        
        # Verify nested structures
        user = result["user"]
        address = result["address"]
        
        self.assertIsInstance(user, dict)
        self.assertIsInstance(address, dict)
        
        # Verify nested field types
        self.assertIsInstance(user["name"], str)
        self.assertIsInstance(user["age"], int)
        self.assertIsInstance(address["street"], str)
        self.assertIsInstance(address["city"], str)

    @pytest.mark.integration
    def test_enum_extraction(self):
        """Test extraction with enum fields."""
        schema = {
            "product": "string",
            "category": {
                "type": "enum",
                "values": ["electronics", "clothing", "books", "food"]
            },
            "priority": {
                "type": "enum", 
                "values": ["low", "medium", "high", "urgent"]
            }
        }
        
        prompt = "Product info: iPhone 15 is an electronics item with high priority"
        
        result = call_with_schema(prompt, schema, self.ollama_options)
        
        # Verify structure
        self.assertIsInstance(result, dict)
        self.assertIn("product", result)
        self.assertIn("category", result)
        self.assertIn("priority", result)
        
        # Verify enum values are valid (handle both string and enum object formats)
        valid_categories = ["electronics", "clothing", "books", "food", "ELECTRONICS", "CLOTHING", "BOOKS", "FOOD"]
        valid_priorities = ["low", "medium", "high", "urgent", "LOW", "MEDIUM", "HIGH", "URGENT"]
        
        # Check if it's an enum object or string
        if hasattr(result["category"], 'value'):
            category_value = result["category"].value.lower()
        else:
            category_value = str(result["category"]).lower()
            
        if hasattr(result["priority"], 'value'):
            priority_value = result["priority"].value.lower()
        else:
            priority_value = str(result["priority"]).lower()
        
        self.assertIn(category_value, ["electronics", "clothing", "books", "food"])
        self.assertIn(priority_value, ["low", "medium", "high", "urgent"])

    @pytest.mark.integration
    def test_optional_fields_extraction(self):
        """Test extraction with optional fields."""
        schema = {
            "name": "string",
            "email": {"type": "string", "optional": True},
            "phone": {"type": "string", "optional": True},
            "age": "int"
        }
        
        prompt = "Contact: Bob Wilson, age 45, email: bob@example.com"
        
        result = call_with_schema(prompt, schema, self.ollama_options)
        
        # Verify required fields
        self.assertIn("name", result)
        self.assertIn("age", result)
        self.assertIsInstance(result["name"], str)
        self.assertIsInstance(result["age"], int)
        
        # Optional fields may or may not be present
        if "email" in result:
            self.assertIsInstance(result["email"], (str, type(None)))
        if "phone" in result:
            self.assertIsInstance(result["phone"], (str, type(None)))

    @pytest.mark.integration
    def test_safe_call_success(self):
        """Test safe call that returns structured result instead of raising exceptions."""
        schema = {
            "name": "string",
            "age": "int"
        }
        
        prompt = "Person: Carol Davis is 29 years old"
        
        result = call_with_schema_safe(prompt, schema, self.ollama_options)
        
        # Verify safe call structure
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertIn("data", result)
        
        # Verify extracted data
        data = result["data"]
        self.assertIsInstance(data, dict)
        self.assertIn("name", data)
        self.assertIn("age", data)

    @pytest.mark.integration
    def test_timeout_handling(self):
        """Test timeout handling with very short timeout."""
        schema = {
            "summary": "string",
            "details": ["string"]
        }
        
        # Very complex prompt that might take longer to process
        prompt = """
        Analyze this complex scenario and provide detailed insights:
        A multinational corporation is expanding into 15 new markets across
        Asia, Europe, and South America while simultaneously launching 3 new
        product lines, restructuring their supply chain, implementing new
        sustainability initiatives, dealing with regulatory changes in each
        market, managing currency fluctuations, and coordinating with 200+
        local partners across different time zones and languages.
        """
        
        timeout_options = self.ollama_options.copy()
        timeout_options["timeout"] = 1  # Very short timeout
        
        # This should either succeed quickly or timeout
        try:
            result = call_with_schema(prompt, schema, timeout_options)
            # If it succeeds, verify the structure
            self.assertIsInstance(result, dict)
        except TimeoutError:
            # Timeout is expected with such a short timeout
            pass

    @pytest.mark.integration
    def test_model_availability_check(self):
        """Test checking if the gemma3:1b model is actually available."""
        factory = LLMProviderFactory()
        provider = factory.create_provider(self.ollama_options)
        
        # Test basic availability
        self.assertTrue(provider.is_available())
        
        # Test that we can make a simple call
        simple_response = provider.call(
            "Say 'Hello World' exactly as written", 
            self.ollama_options
        )
        
        self.assertIsInstance(simple_response, str)
        self.assertTrue(len(simple_response.strip()) > 0)

    @pytest.mark.integration
    def test_real_world_email_parsing(self):
        """Test realistic email parsing scenario."""
        schema = {
            "sender": "string",
            "subject": "string", 
            "priority": {
                "type": "enum",
                "values": ["low", "medium", "high", "urgent"]
            },
            "action_items": ["string"],
            "due_date": {"type": "string", "optional": True}
        }
        
        email_text = """
        From: project.manager@company.com
        Subject: Q4 Budget Review - Action Required
        
        Hi Team,
        
        We need to complete the Q4 budget review by December 15th. Please:
        1. Review your department's spending
        2. Submit variance reports
        3. Prepare cost projections for next quarter
        4. Schedule team meetings for budget discussion
        
        This is high priority due to the upcoming board meeting.
        
        Thanks,
        Sarah
        """
        
        result = call_with_schema(
            f"Extract email details from: {email_text}", 
            schema, 
            self.ollama_options
        )
        
        # Verify structure
        self.assertIn("sender", result)
        self.assertIn("subject", result)
        self.assertIn("priority", result)
        self.assertIn("action_items", result)
        
        # Verify types
        self.assertIsInstance(result["sender"], str)
        self.assertIsInstance(result["subject"], str)
        
        # Handle enum value comparison
        if hasattr(result["priority"], 'value'):
            priority_value = result["priority"].value.lower()
        else:
            priority_value = str(result["priority"]).lower()
        self.assertIn(priority_value, ["low", "medium", "high", "urgent"])
        self.assertIsInstance(result["action_items"], list)
        
        # Verify content quality
        self.assertTrue(len(result["action_items"]) > 0)
        for item in result["action_items"]:
            self.assertIsInstance(item, str)
            self.assertTrue(len(item.strip()) > 0)

    @pytest.mark.integration
    def test_batch_processing_consistency(self):
        """Test that multiple calls with same input produce consistent results."""
        schema = {
            "city": "string",
            "population_category": {
                "type": "enum", 
                "values": ["small", "medium", "large", "major"]
            }
        }
        
        prompt = "City info: San Francisco has about 900,000 residents"
        
        results = []
        for i in range(3):
            result = call_with_schema(prompt, schema, self.ollama_options)
            results.append(result)
            time.sleep(1)  # Small delay between calls
        
        # All results should have the same structure
        for result in results:
            self.assertIn("city", result)
            self.assertIn("population_category", result)
            self.assertIsInstance(result["city"], str)
            
            # Handle enum value comparison
            if hasattr(result["population_category"], 'value'):
                category_value = result["population_category"].value.lower()
            else:
                category_value = str(result["population_category"]).lower()
            self.assertIn(category_value, ["small", "medium", "large", "major"])
        
        # Results should be reasonably consistent
        cities = [r["city"] for r in results]
        categories = [r["population_category"] for r in results]
        
        # At least some consistency in extracted values
        self.assertTrue(len(set(cities)) <= 2)  # Should be similar city names
        self.assertTrue(len(set(categories)) <= 2)  # Should be similar categorizations


if __name__ == "__main__":
    # Run integration tests only
    pytest.main([
        __file__, 
        "-m", "integration", 
        "-v",
        "--tb=short"
    ]) 