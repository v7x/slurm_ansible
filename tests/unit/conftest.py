#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Pytest configuration for unit tests.
Provides common fixtures and setup for all unit tests.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add module_utils to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'module_utils'))

from ansible.module_utils.basic import AnsibleModule


@pytest.fixture
def mock_ansible_module():
    """
    Create a mock AnsibleModule for testing.
    
    Returns:
        Mock: A mock AnsibleModule instance with common methods mocked
    """
    module = Mock(spec=AnsibleModule)
    module.fail_json = Mock(side_effect=Exception("Module failed"))
    module.exit_json = Mock()
    module.params = {}
    module.check_mode = False
    return module


@pytest.fixture
def mock_subprocess_success():
    """
    Create a mock subprocess result for successful command execution.
    
    Returns:
        Mock: A mock subprocess result with success indicators
    """
    result = Mock()
    result.returncode = 0
    result.stdout = "Command executed successfully"
    result.stderr = ""
    return result


@pytest.fixture
def mock_subprocess_failure():
    """
    Create a mock subprocess result for failed command execution.
    
    Returns:
        Mock: A mock subprocess result with failure indicators
    """
    result = Mock()
    result.returncode = 1
    result.stdout = ""
    result.stderr = "Command failed"
    return result


@pytest.fixture
def mock_subprocess_json():
    """
    Create a mock subprocess result with JSON output.
    
    Returns:
        Mock: A mock subprocess result with JSON output
    """
    result = Mock()
    result.returncode = 0
    result.stdout = '{"test": "data", "success": true}'
    result.stderr = ""
    return result


@pytest.fixture(autouse=True)
def reset_mocks():
    """
    Automatically reset all mocks after each test.
    This ensures test isolation.
    """
    yield
    # Any cleanup code would go here if needed


# Test markers for categorizing tests
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_slurm: mark test as requiring SLURM environment"
    ) 