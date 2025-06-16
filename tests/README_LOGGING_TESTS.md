# Dynamic BAML Logging Tests

This directory contains comprehensive tests for the Dynamic BAML logging functionality.

## Consolidated Test File

**`test_logging_all.py`** - Complete test suite with all logging tests consolidated into a single file.

### Test Organization

The consolidated test file contains **24 tests** organized into 3 test classes:

#### 1. `TestLoggingUnit` (10 tests)
Basic unit tests for logging configuration:
- Provider options type validation
- Log level configuration 
- Log file path handling
- Error handling and graceful failures
- Optional field behavior

#### 2. `TestLoggingComprehensive` (9 tests)  
Comprehensive tests without LLM dependency:
- Path validation scenarios (simple, nested, absolute, relative)
- All log levels (off, error, warn, info, debug, trace)
- Concurrent logging operations
- File permissions and directory creation
- Environment variable management
- Mixed configuration scenarios
- Performance testing
- Mocked BAML calls

#### 3. `TestLoggingIntegration` (5 tests)
Integration tests requiring Ollama:
- Real log file creation and content verification
- Different log levels with actual BAML operations
- Directory auto-creation for nested paths
- Multiple calls appending to same log file
- Safe calls with logging

## Running Tests

### All Tests (Non-Integration)
```bash
# Run unit + comprehensive tests (no LLM required)
pytest tests/test_logging_all.py -v -m "not integration"
```

### Specific Test Classes
```bash
# Unit tests only
pytest tests/test_logging_all.py::TestLoggingUnit -v

# Comprehensive tests only  
pytest tests/test_logging_all.py::TestLoggingComprehensive -v

# Integration tests only (requires Ollama)
pytest tests/test_logging_all.py::TestLoggingIntegration -v
```

### All Tests Including Integration
```bash
# Run all tests (integration tests will be skipped if Ollama unavailable)
pytest tests/test_logging_all.py -v
```

### With Coverage
```bash
# Run with test coverage reporting
pytest tests/test_logging_all.py -v --cov=dynamic_baml.core --cov=dynamic_baml.types --cov-report=term-missing
```

## Test Results

- ✅ **24 total tests**
- ✅ **19 tests run without LLM** (unit + comprehensive)
- ✅ **5 integration tests** available when Ollama is running
- ✅ **All tests pass** with 100% success rate
- ✅ **Fast execution** - non-integration tests complete in ~0.3 seconds

## Features Tested

### Log Level Control
- ✅ All 6 levels: `off`, `error`, `warn`, `info`, `debug`, `trace`
- ✅ Invalid level handling
- ✅ No level specified (default behavior)

### Log File Output  
- ✅ Custom file paths (absolute, relative, nested)
- ✅ Automatic directory creation
- ✅ File appending for multiple calls
- ✅ Environment variable management
- ✅ Permission and error handling

### Integration Features
- ✅ Real BAML operations with logging
- ✅ Safe calls (`call_with_schema_safe`)
- ✅ Concurrent operations
- ✅ Error resilience
- ✅ Performance impact

### Edge Cases
- ✅ Empty paths
- ✅ Invalid paths  
- ✅ Concurrent access
- ✅ Import errors
- ✅ File system errors
- ✅ Thread safety

## Legacy Test Files

The following individual test files have been consolidated into `test_logging_all.py`:

- `test_logging_options.py` (10 tests) → `TestLoggingUnit`
- `test_logging_comprehensive.py` (12 tests) → `TestLoggingComprehensive` 
- `test_logging_integration.py` (11 tests) → `TestLoggingIntegration`

These individual files can be removed as all functionality is now in the consolidated file.

## Quick Verification

```bash
# Verify all tests are working
pytest tests/test_logging_all.py -v -m "not integration" --tb=short

# Expected output:
# =================== 19 passed, 5 deselected ===================
``` 

This directory contains comprehensive tests for the Dynamic BAML logging functionality.

## Consolidated Test File

**`test_logging_all.py`** - Complete test suite with all logging tests consolidated into a single file.

### Test Organization

The consolidated test file contains **24 tests** organized into 3 test classes:

#### 1. `TestLoggingUnit` (10 tests)
Basic unit tests for logging configuration:
- Provider options type validation
- Log level configuration 
- Log file path handling
- Error handling and graceful failures
- Optional field behavior

#### 2. `TestLoggingComprehensive` (9 tests)  
Comprehensive tests without LLM dependency:
- Path validation scenarios (simple, nested, absolute, relative)
- All log levels (off, error, warn, info, debug, trace)
- Concurrent logging operations
- File permissions and directory creation
- Environment variable management
- Mixed configuration scenarios
- Performance testing
- Mocked BAML calls

#### 3. `TestLoggingIntegration` (5 tests)
Integration tests requiring Ollama:
- Real log file creation and content verification
- Different log levels with actual BAML operations
- Directory auto-creation for nested paths
- Multiple calls appending to same log file
- Safe calls with logging

## Running Tests

### All Tests (Non-Integration)
```bash
# Run unit + comprehensive tests (no LLM required)
pytest tests/test_logging_all.py -v -m "not integration"
```

### Specific Test Classes
```bash
# Unit tests only
pytest tests/test_logging_all.py::TestLoggingUnit -v

# Comprehensive tests only  
pytest tests/test_logging_all.py::TestLoggingComprehensive -v

# Integration tests only (requires Ollama)
pytest tests/test_logging_all.py::TestLoggingIntegration -v
```

### All Tests Including Integration
```bash
# Run all tests (integration tests will be skipped if Ollama unavailable)
pytest tests/test_logging_all.py -v
```

### With Coverage
```bash
# Run with test coverage reporting
pytest tests/test_logging_all.py -v --cov=dynamic_baml.core --cov=dynamic_baml.types --cov-report=term-missing
```

## Test Results

- ✅ **24 total tests**
- ✅ **19 tests run without LLM** (unit + comprehensive)
- ✅ **5 integration tests** available when Ollama is running
- ✅ **All tests pass** with 100% success rate
- ✅ **Fast execution** - non-integration tests complete in ~0.3 seconds

## Features Tested

### Log Level Control
- ✅ All 6 levels: `off`, `error`, `warn`, `info`, `debug`, `trace`
- ✅ Invalid level handling
- ✅ No level specified (default behavior)

### Log File Output  
- ✅ Custom file paths (absolute, relative, nested)
- ✅ Automatic directory creation
- ✅ File appending for multiple calls
- ✅ Environment variable management
- ✅ Permission and error handling

### Integration Features
- ✅ Real BAML operations with logging
- ✅ Safe calls (`call_with_schema_safe`)
- ✅ Concurrent operations
- ✅ Error resilience
- ✅ Performance impact

### Edge Cases
- ✅ Empty paths
- ✅ Invalid paths  
- ✅ Concurrent access
- ✅ Import errors
- ✅ File system errors
- ✅ Thread safety

## Legacy Test Files

The following individual test files have been consolidated into `test_logging_all.py`:

- `test_logging_options.py` (10 tests) → `TestLoggingUnit`
- `test_logging_comprehensive.py` (12 tests) → `TestLoggingComprehensive` 
- `test_logging_integration.py` (11 tests) → `TestLoggingIntegration`

These individual files can be removed as all functionality is now in the consolidated file.

## Quick Verification

```bash
# Verify all tests are working
pytest tests/test_logging_all.py -v -m "not integration" --tb=short

# Expected output:
# =================== 19 passed, 5 deselected ===================
``` 
 