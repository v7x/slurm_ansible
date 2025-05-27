# SLURM Ansible Module Tests

This directory contains comprehensive tests for the SLURM Ansible modules, specifically focusing on the `SacctmgrHelper` class.

## Test Structure

The test suite follows Ansible testing best practices and is organized as follows:

```
tests/
├── unit/                           # Unit tests
│   ├── module_utils/              # Tests for module utilities
│   │   └── test_sacctmgr_helper.py # SacctmgrHelper unit tests
│   └── conftest.py                # Pytest configuration and fixtures
├── integration/                   # Integration tests
│   └── targets/
│       └── sacctmgr_helper/       # SacctmgrHelper integration tests
│           ├── tasks/main.yml     # Test playbook
│           ├── meta/main.yml      # Test metadata
│           └── library/           # Test modules
│               ├── sacctmgr_test.py
│               └── sacctmgr_show.py
├── requirements.txt               # Python test dependencies
├── run_tests.sh                  # Test runner script
└── README.md                     # This file
```

## Test Types

### 1. Unit Tests

Unit tests focus on testing individual components in isolation using mocks and stubs.

**Location**: `tests/unit/module_utils/test_sacctmgr_helper.py`

**Coverage**:
- Class initialization and configuration
- Command and entity validation
- Command building logic
- Subprocess execution handling
- JSON parsing
- Error handling and edge cases
- Convenience methods

**Features**:
- Comprehensive mocking of external dependencies
- Test isolation with fixtures
- Coverage reporting
- Fast execution (no external dependencies)

### 2. Integration Tests

Integration tests verify the actual interaction with SLURM commands in a real environment.

**Location**: `tests/integration/targets/sacctmgr_helper/`

**Coverage**:
- Real sacctmgr command execution
- SLURM environment interaction
- End-to-end functionality
- Permission handling
- Error scenarios with real commands

**Requirements**:
- Working SLURM environment
- `sacctmgr` command available
- Appropriate permissions for SLURM operations

### 3. Sanity Tests

Sanity tests ensure code quality and Ansible module standards compliance.

**Coverage**:
- Code style and formatting
- Import validation
- Documentation standards
- Ansible module conventions

## Running Tests

### Quick Start

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests (unit + sanity)
./tests/run_tests.sh

# Run with coverage
./tests/run_tests.sh -c
```

### Detailed Usage

#### Using the Test Runner Script

The `run_tests.sh` script provides a convenient way to run different test types:

```bash
# Run only unit tests
./tests/run_tests.sh -u

# Run only integration tests (requires SLURM)
./tests/run_tests.sh -i

# Run all tests including integration
./tests/run_tests.sh -i

# Run with coverage and verbose output
./tests/run_tests.sh -c -v

# Skip sanity tests
./tests/run_tests.sh --no-sanity

# Show help
./tests/run_tests.sh -h
```

#### Using pytest Directly

For more control over unit test execution:

```bash
# Run all unit tests
python -m pytest tests/unit/

# Run specific test file
python -m pytest tests/unit/module_utils/test_sacctmgr_helper.py

# Run with coverage
python -m pytest tests/unit/ --cov=module_utils --cov-report=html

# Run specific test method
python -m pytest tests/unit/module_utils/test_sacctmgr_helper.py::TestSacctmgrHelper::test_validate_command_valid

# Run with verbose output
python -m pytest tests/unit/ -v

# Run tests matching a pattern
python -m pytest tests/unit/ -k "test_validate"
```

#### Using ansible-test

For integration and sanity tests:

```bash
# Run integration tests
cd tests/integration
ansible-test integration sacctmgr_helper

# Run sanity tests
ansible-test sanity --python 3.8

# Run with verbose output
ansible-test integration sacctmgr_helper -v
```

## Test Environment Setup

### For Unit Tests

Unit tests only require Python dependencies:

```bash
pip install -r tests/requirements.txt
```

### For Integration Tests

Integration tests require a working SLURM environment:

1. **Install SLURM**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install slurm-wlm slurm-wlm-basic-plugins
   
   # CentOS/RHEL
   sudo yum install slurm slurm-slurmd slurm-slurmctld
   ```

2. **Configure SLURM**: Ensure SLURM is properly configured with:
   - Running slurmctld daemon
   - Accessible sacctmgr command
   - Appropriate user permissions

3. **Verify Setup**:
   ```bash
   sacctmgr show cluster
   ```

### CI/CD Environment

For automated testing environments:

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run tests that don't require SLURM
./tests/run_tests.sh --no-integration

# Or run all tests if SLURM is available
./tests/run_tests.sh -i
```

## Test Configuration

### Pytest Configuration

The `tests/unit/conftest.py` file provides:
- Common fixtures for mocking
- Test markers for categorization
- Automatic mock cleanup
- Path configuration for imports

### Integration Test Configuration

The `tests/integration/targets/sacctmgr_helper/meta/main.yml` file specifies:
- Test dependencies
- Environment requirements
- Test tags and skip conditions

## Writing New Tests

### Unit Test Guidelines

1. **Use fixtures** for common setup:
   ```python
   def test_my_feature(self, helper, mock_subprocess_success):
       # Test implementation
   ```

2. **Mock external dependencies**:
   ```python
   @patch('subprocess.run')
   def test_command_execution(self, mock_run, helper):
       mock_run.return_value = mock_subprocess_success
       # Test implementation
   ```

3. **Test both success and failure cases**:
   ```python
   def test_success_case(self, helper):
       # Test successful execution
   
   def test_failure_case(self, helper):
       # Test error handling
   ```

4. **Use descriptive test names**:
   ```python
   def test_validate_command_with_invalid_input_should_fail(self, helper):
       # Test implementation
   ```

### Integration Test Guidelines

1. **Check for SLURM availability**:
   ```yaml
   - name: Check if sacctmgr is available
     command: which sacctmgr
     register: sacctmgr_check
     failed_when: false
   ```

2. **Use cleanup blocks**:
   ```yaml
   - name: Test block
     block:
       # Test tasks
     rescue:
       # Error handling
     always:
       # Cleanup tasks
   ```

3. **Test with appropriate permissions**:
   ```yaml
   - name: Create test resource
     sacctmgr_test:
       command: add
       entity: account
       options: "name=test_account"
     register: result
     failed_when: false  # Don't fail if permissions insufficient
   ```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: pip install -r tests/requirements.txt
      - name: Run unit tests
        run: ./tests/run_tests.sh -u -c
      - name: Upload coverage
        uses: codecov/codecov-action@v1

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install SLURM
        run: |
          sudo apt-get update
          sudo apt-get install slurm-wlm
      - name: Configure SLURM
        run: |
          # SLURM configuration steps
      - name: Run integration tests
        run: ./tests/run_tests.sh -i
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure the module_utils path is correctly added to sys.path
2. **SLURM not available**: Integration tests will be skipped automatically
3. **Permission errors**: Some integration tests require SLURM admin permissions
4. **Mock issues**: Use the provided fixtures for consistent mocking

### Debug Tips

1. **Use verbose output**: Add `-v` flag to see detailed test output
2. **Run specific tests**: Use pytest's `-k` flag to run specific test patterns
3. **Check coverage**: Use coverage reports to identify untested code paths
4. **Examine logs**: Integration tests provide detailed command output

## Contributing

When adding new tests:

1. Follow the existing test structure and naming conventions
2. Add both positive and negative test cases
3. Update this documentation if adding new test types
4. Ensure tests are isolated and don't depend on external state
5. Add appropriate test markers and documentation 