# Dynamic BAML Distribution Guide

This document outlines the distribution-ready structure of the Dynamic BAML package and provides instructions for building, testing, and publishing.

## Package Structure

The package follows Python packaging best practices as outlined in the Python Package Repository Structure Guide:

```
dynamic_baml/
├── README.md              # Package documentation
├── LICENSE                # MIT License
├── setup.py              # Distribution configuration
├── pyproject.toml        # Modern Python project configuration
├── requirements.txt      # Core dependencies
├── MANIFEST.in           # Distribution file manifest
├── Makefile             # Build automation
├── .gitignore           # Git ignore patterns
├── dynamic_baml/        # Main package directory
│   ├── __init__.py
│   ├── core.py
│   ├── providers.py
│   ├── schema_generator.py
│   ├── baml_executor.py
│   ├── exceptions.py
│   ├── types.py
│   ├── py.typed
│   └── baml/           # BAML schema files (package data)
│       ├── client.py
│       └── main.baml
├── tests/               # Test suite
│   ├── context.py       # Test import helper
│   ├── test_core.py
│   ├── test_providers.py
│   ├── test_schema_generator.py
│   ├── test_baml_executor.py
│   └── test_exceptions.py
├── examples/            # Usage examples
│   ├── basic_usage.py
│   ├── complex_schemas.py
│   ├── multi_provider.py
│   ├── error_handling.py
│   └── real_world.py
└── docs/               # Documentation
    ├── conf.py
    └── index.rst
```

## Key Features

### Distribution Configuration

- **setup.py**: Traditional setuptools configuration for maximum compatibility
- **pyproject.toml**: Modern Python project configuration
- **requirements.txt**: Core runtime dependencies
- **MANIFEST.in**: Specifies files to include in distribution
- **Package data**: BAML files included as package data within dynamic_baml/

### Testing Infrastructure

- **tests/context.py**: Proper import handling for tests as recommended in the guide
- **98.83% test coverage** with 178 passing tests
- **pytest configuration** in pyproject.toml

### Documentation

- **Sphinx-ready docs/** directory with conf.py
- **README.md** with comprehensive examples and API documentation
- **Type hints** throughout the codebase with py.typed marker

### Build Automation

The included Makefile provides common development tasks:

```bash
make help       # Show available commands
make init       # Install development dependencies
make test       # Run tests with coverage
make clean      # Remove build artifacts
make build      # Build distribution packages
make docs       # Build documentation
make lint       # Run code quality checks
make format     # Format code with black
```

## Development Workflow

### Initial Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd dynamic_baml

# Set up development environment
make dev-setup
```

### Running Tests

```bash
# Run unit tests with coverage (default)
make test

# Run integration tests with actual gemma3:1b model
make test-integration

# Run all tests (unit + integration)
make test-all

# Run specific test file
pytest tests/test_core.py

# Run with verbose output
pytest -v tests/
```

#### Integration Tests

Integration tests use the actual Ollama gemma3:1b model to verify real-world functionality:

**Prerequisites:**
```bash
# Install and start Ollama
ollama serve

# Pull the gemma3:1b model (small, fast model)
ollama pull gemma3:1b
```

**Running Integration Tests:**
```bash
# Automated script with model checking
./test_integration.sh

# Or manually with pytest
pytest tests/test_integration.py -m integration -v
```

The integration tests verify:
- Basic string and type extraction
- Complex nested objects and arrays  
- Enum validation and optional fields
- Real-world scenarios (email parsing, etc.)
- Error handling and timeouts
- Model availability and consistency

### Building for Distribution

```bash
# Clean and build distribution packages
make build

# The build artifacts will be in dist/:
# - dynamic_baml-0.1.0.tar.gz (source distribution)
# - dynamic_baml-0.1.0-py3-none-any.whl (wheel)
```

### Publishing to PyPI

```bash
# Test on TestPyPI first (recommended)
make upload REPO=testpypi

# Publish to PyPI
make upload
```

## Package Installation

### From PyPI (once published)

```bash
pip install dynamic_baml
```

### From Source

```bash
# Development installation
pip install -e .

# Production installation
pip install .

# With development dependencies
pip install -e .[dev,docs]
```

## Quality Assurance

### Code Quality

- **98.83% test coverage** maintained
- **Type hints** throughout the codebase
- **Comprehensive error handling** with custom exception hierarchy
- **Multi-provider support** with fallback mechanisms

### Testing Strategy

- **Unit tests** for all core functionality
- **Integration tests** with mock providers
- **Error condition testing** for robust error handling
- **Performance tests** for batch processing

### Dependencies

#### Core Runtime Dependencies
- `baml-py>=0.89.0` - BAML language support
- `httpx>=0.24.0` - HTTP client for API calls
- `pydantic>=2.0.0` - Data validation and serialization
- `pyyaml>=6.0.0` - YAML configuration support

#### Development Dependencies
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `pytest-asyncio>=0.21.0` - Async testing support
- `black>=22.0.0` - Code formatting
- `flake8>=5.0.0` - Code linting
- `mypy>=1.0.0` - Type checking

## Features

### Core Capabilities

- **Dynamic Schema Generation**: Create BAML schemas from Python data structures
- **Multi-Provider Support**: OpenAI, Anthropic, Ollama, OpenRouter, and more
- **Type Safety**: Full type hints and runtime validation
- **Error Handling**: Comprehensive exception hierarchy
- **Batch Processing**: Optimized for high-throughput applications

### Advanced Features

- **Provider Failover**: Automatic fallback between providers
- **Retry Mechanisms**: Configurable retry logic with exponential backoff
- **Caching**: Optional response caching for improved performance
- **Monitoring**: Built-in logging and metrics collection
- **Configuration**: Flexible YAML-based configuration system

## License

This package is licensed under the MIT License. See the LICENSE file for details.

## Support

For issues, feature requests, or contributions, please visit the project repository. 