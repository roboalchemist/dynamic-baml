#!/bin/bash

# Integration Test Runner for Dynamic BAML
# Tests with actual Ollama Gemma3:1b model

echo "🧪 Dynamic BAML Integration Tests"
echo "=================================="

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "❌ Ollama is not running!"
    echo "💡 Start Ollama: ollama serve"
    echo "💡 In another terminal run: ollama pull gemma3:1b"
    exit 1
fi

# Check if Ollama is accessible
if ! curl -s http://localhost:11434/api/version > /dev/null; then
    echo "❌ Cannot connect to Ollama API!"
    echo "💡 Make sure Ollama is running on port 11434"
    exit 1
fi

# Check if gemma3:1b model is available
echo "🔍 Checking if gemma3:1b model is available..."
if ! ollama list | grep -q "gemma3:1b"; then
    echo "❌ gemma3:1b model not found!"
    echo "💡 Pull the model: ollama pull gemma3:1b"
    echo "💡 This may take a few minutes for first download..."
    
    read -p "🤖 Would you like to pull gemma3:1b now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 Pulling gemma3:1b model..."
        ollama pull gemma3:1b
        if [ $? -ne 0 ]; then
            echo "❌ Failed to pull gemma3:1b model"
            exit 1
        fi
        echo "✅ Model downloaded successfully"
    else
        echo "❌ Integration tests require gemma3:1b model"
        exit 1
    fi
fi

echo "✅ gemma3:1b model is available"

# Test basic connectivity
echo "🔌 Testing Ollama connectivity..."
if curl -s -X POST http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d '{"model": "gemma3:1b", "prompt": "Hello", "stream": false}' | grep -q "response"; then
    echo "✅ Ollama is responding correctly"
else
    echo "❌ Ollama test call failed"
    exit 1
fi

# Run integration tests
echo ""
echo "🧪 Running Integration Tests..."
echo "================================"

# Run tests with integration marker
pytest tests/test_integration.py -m integration -v --tb=short --timeout=300

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✅ All integration tests passed!"
    echo "🎉 Dynamic BAML is working correctly with gemma3:1b"
else
    echo "❌ Some integration tests failed"
    echo "💡 Check the test output above for details"
fi

echo ""
echo "📋 Integration Test Summary:"
echo "- Model: gemma3:1b (local Ollama)"
echo "- Provider: Ollama (http://localhost:11434)"
echo "- Tests: Schema validation, type extraction, real-world scenarios"

exit $exit_code 