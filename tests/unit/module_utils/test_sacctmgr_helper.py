#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import pytest
import subprocess
from unittest.mock import Mock, patch, MagicMock
from ansible.module_utils.basic import AnsibleModule

# Import the class under test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'module_utils'))
from sacctmgr_helper import SacctmgrHelper


class TestSacctmgrHelper:
    """Test cases for SacctmgrHelper class."""
    
    @pytest.fixture
    def mock_module(self):
        """Create a mock AnsibleModule for testing."""
        module = Mock(spec=AnsibleModule)
        module.fail_json = Mock(side_effect=Exception("Module failed"))
        return module
    
    @pytest.fixture
    def helper(self, mock_module):
        """Create a SacctmgrHelper instance with mocked dependencies."""
        with patch.object(SacctmgrHelper, '_find_sacctmgr', return_value='/usr/bin/sacctmgr'):
            return SacctmgrHelper(mock_module)
    
    def test_init_success(self, mock_module):
        """Test successful initialization of SacctmgrHelper."""
        with patch.object(SacctmgrHelper, '_find_sacctmgr', return_value='/usr/bin/sacctmgr'):
            helper = SacctmgrHelper(mock_module)
            assert helper.module == mock_module
            assert helper.sacctmgr_path == '/usr/bin/sacctmgr'
    
    def test_init_sacctmgr_not_found(self, mock_module):
        """Test initialization when sacctmgr is not found."""
        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'which')):
            with pytest.raises(Exception, match="Module failed"):
                SacctmgrHelper(mock_module)
            mock_module.fail_json.assert_called_once_with(msg="sacctmgr command not found in PATH")
    
    def test_find_sacctmgr_success(self, mock_module):
        """Test successful finding of sacctmgr executable."""
        mock_result = Mock()
        mock_result.stdout = '/usr/bin/sacctmgr\n'
        
        with patch('subprocess.run', return_value=mock_result) as mock_run:
            helper = SacctmgrHelper(mock_module)
            assert helper.sacctmgr_path == '/usr/bin/sacctmgr'
            mock_run.assert_called_once_with(['which', 'sacctmgr'], 
                                           capture_output=True, text=True, check=True)
    
    def test_validate_command_valid(self, helper):
        """Test validation of valid commands."""
        valid_commands = ['add', 'show', 'delete', 'modify', 'list']
        for command in valid_commands:
            assert helper.validate_command(command) is True
            assert helper.validate_command(command.upper()) is True
    
    def test_validate_command_invalid(self, helper):
        """Test validation of invalid commands."""
        with pytest.raises(Exception, match="Module failed"):
            helper.validate_command('invalid_command')
        helper.module.fail_json.assert_called_with(
            msg="Invalid sacctmgr command: invalid_command. "
                "Valid commands are: add, create, delete, remove, modify, update, show, list, dump, load, archive, clear"
        )
    
    def test_validate_entity_valid(self, helper):
        """Test validation of valid entities."""
        valid_entities = ['account', 'user', 'cluster', 'qos', 'association']
        for entity in valid_entities:
            assert helper.validate_entity(entity) is True
            assert helper.validate_entity(entity.upper()) is True
    
    def test_validate_entity_invalid(self, helper):
        """Test validation of invalid entities."""
        with pytest.raises(Exception, match="Module failed"):
            helper.validate_entity('invalid_entity')
        helper.module.fail_json.assert_called_with(
            msg="Invalid sacctmgr entity: invalid_entity. "
                "Valid entities are: account, association, cluster, coordinator, event, federation, job, problem, qos, reservation, resource, runaway, stats, transaction, tres, user, wckey"
        )
    
    def test_build_command_basic(self, helper):
        """Test building basic command without options."""
        cmd = helper._build_command('show', 'account')
        expected = ['/usr/bin/sacctmgr', '--immediate', '--readonly', '--json', 'show', 'account']
        assert cmd == expected
    
    def test_build_command_with_string_options(self, helper):
        """Test building command with string options."""
        cmd = helper._build_command('show', 'account', 'name=test format=name,description')
        expected = ['/usr/bin/sacctmgr', '--immediate', '--readonly', '--json', 'show', 'account', 'name=test', 'format=name,description']
        assert cmd == expected
    
    def test_build_command_with_list_options(self, helper):
        """Test building command with list options."""
        cmd = helper._build_command('show', 'account', ['name=test', 'format=name,description'])
        expected = ['/usr/bin/sacctmgr', '--immediate', '--readonly', '--json', 'show', 'account', 'name=test', 'format=name,description']
        assert cmd == expected
    
    def test_build_command_no_json(self, helper):
        """Test building command without JSON flag."""
        cmd = helper._build_command('add', 'account', use_json=False)
        expected = ['/usr/bin/sacctmgr', '--immediate', 'add', 'account']
        assert cmd == expected
    
    def test_build_command_no_readonly(self, helper):
        """Test building command without readonly flag."""
        cmd = helper._build_command('add', 'account', use_readonly=False)
        expected = ['/usr/bin/sacctmgr', '--immediate', '--json', 'add', 'account']
        assert cmd == expected
    
    def test_build_command_invalid_options_type(self, helper):
        """Test building command with invalid options type."""
        with pytest.raises(Exception, match="Module failed"):
            helper._build_command('show', 'account', options=123)
        helper.module.fail_json.assert_called_with(msg="Options must be a string or list")
    
    @patch('subprocess.run')
    def test_run_command_success_with_json(self, mock_run, helper):
        """Test successful command execution with JSON output."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"accounts": [{"name": "test", "description": "Test account"}]}'
        mock_result.stderr = ''
        mock_run.return_value = mock_result
        
        result = helper.run_command('show', 'account')
        
        assert result['success'] is True
        assert result['changed'] is False  # show is readonly
        assert result['data'] == {"accounts": [{"name": "test", "description": "Test account"}]}
        assert result['stdout'] == mock_result.stdout
        assert result['stderr'] == ''
    
    @patch('subprocess.run')
    def test_run_command_success_without_json(self, mock_run, helper):
        """Test successful command execution without JSON output."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = 'Account test created successfully'
        mock_result.stderr = ''
        mock_run.return_value = mock_result
        
        result = helper.run_command('add', 'account', use_json=False)
        
        assert result['success'] is True
        assert result['changed'] is True  # add is not readonly
        assert result['data'] is None
        assert result['stdout'] == mock_result.stdout
    
    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run, helper):
        """Test command execution failure."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ''
        mock_result.stderr = 'Error: Account not found'
        mock_run.return_value = mock_result
        
        result = helper.run_command('show', 'account')
        
        assert result['success'] is False
        assert result['changed'] is False
        assert result['stderr'] == 'Error: Account not found'
    
    @patch('subprocess.run')
    def test_run_command_json_parse_error(self, mock_run, helper):
        """Test command execution with JSON parse error."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = 'Invalid JSON output'
        mock_result.stderr = ''
        mock_run.return_value = mock_result
        
        result = helper.run_command('show', 'account')
        
        assert result['success'] is True
        assert 'json_parse_error' in result
        assert result['data'] is None
    
    @patch('subprocess.run')
    def test_run_command_timeout(self, mock_run, helper):
        """Test command execution timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired('sacctmgr', 300)
        
        with pytest.raises(Exception, match="Module failed"):
            helper.run_command('show', 'account')
        
        helper.module.fail_json.assert_called_with(
            msg="Command timed out after 300 seconds: /usr/bin/sacctmgr --immediate --readonly --json show account"
        )
    
    @patch('subprocess.run')
    def test_run_command_exception(self, mock_run, helper):
        """Test command execution with general exception."""
        mock_run.side_effect = Exception("Unexpected error")
        
        with pytest.raises(Exception, match="Module failed"):
            helper.run_command('show', 'account')
        
        helper.module.fail_json.assert_called_with(msg="Failed to execute command: Unexpected error")
    
    def test_run_command_validates_inputs(self, helper):
        """Test that run_command validates command and entity."""
        with pytest.raises(Exception, match="Module failed"):
            helper.run_command('invalid', 'account')
        
        with pytest.raises(Exception, match="Module failed"):
            helper.run_command('show', 'invalid')
    
    @patch('subprocess.run')
    def test_show_convenience_method(self, mock_run, helper):
        """Test the show convenience method."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"accounts": []}'
        mock_result.stderr = ''
        mock_run.return_value = mock_result
        
        result = helper.show('account', ['name=test'])
        
        assert result['success'] is True
        assert result['changed'] is False
        mock_run.assert_called_once()
        
        # Verify the command was built correctly
        call_args = mock_run.call_args[0][0]
        assert 'show' in call_args
        assert 'account' in call_args
        assert 'name=test' in call_args
        assert '--readonly' in call_args
        assert '--json' in call_args
    
    @patch('subprocess.run')
    def test_add_convenience_method(self, mock_run, helper):
        """Test the add convenience method."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = 'Account added successfully'
        mock_result.stderr = ''
        mock_run.return_value = mock_result
        
        result = helper.add('account', ['name=test', 'description=Test'])
        
        assert result['success'] is True
        assert result['changed'] is True
        
        # Verify the command was built correctly
        call_args = mock_run.call_args[0][0]
        assert 'add' in call_args
        assert 'account' in call_args
        assert 'name=test' in call_args
        assert '--readonly' not in call_args
        assert '--json' not in call_args
    
    @patch('subprocess.run')
    def test_delete_convenience_method(self, mock_run, helper):
        """Test the delete convenience method."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = 'Account deleted successfully'
        mock_result.stderr = ''
        mock_run.return_value = mock_result
        
        result = helper.delete('account', ['name=test'])
        
        assert result['success'] is True
        assert result['changed'] is True
        
        # Verify the command was built correctly
        call_args = mock_run.call_args[0][0]
        assert 'delete' in call_args
        assert 'account' in call_args
        assert 'name=test' in call_args
        assert '--readonly' not in call_args
    
    @patch('subprocess.run')
    def test_modify_convenience_method(self, mock_run, helper):
        """Test the modify convenience method."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = 'Account modified successfully'
        mock_result.stderr = ''
        mock_run.return_value = mock_result
        
        result = helper.modify('account', ['name=test', 'set', 'description=Updated'])
        
        assert result['success'] is True
        assert result['changed'] is True
        
        # Verify the command was built correctly
        call_args = mock_run.call_args[0][0]
        assert 'modify' in call_args
        assert 'account' in call_args
        assert 'name=test' in call_args
        assert 'set' in call_args
        assert 'description=Updated' in call_args
    
    def test_readonly_commands_classification(self, helper):
        """Test that readonly commands are correctly classified."""
        readonly_commands = ['show', 'list', 'dump']
        modifying_commands = ['add', 'delete', 'modify', 'create']
        
        for cmd in readonly_commands:
            assert cmd in helper.READONLY_COMMANDS
        
        for cmd in modifying_commands:
            assert cmd not in helper.READONLY_COMMANDS
    
    def test_json_supported_commands(self, helper):
        """Test that JSON supported commands are correctly classified."""
        json_commands = ['show', 'list', 'dump']
        
        for cmd in json_commands:
            assert cmd in helper.JSON_SUPPORTED_COMMANDS
    
    def test_valid_commands_list(self, helper):
        """Test that all expected commands are in the valid commands list."""
        expected_commands = [
            'add', 'create', 'delete', 'remove', 'modify', 'update',
            'show', 'list', 'dump', 'load', 'archive', 'clear'
        ]
        
        for cmd in expected_commands:
            assert cmd in helper.VALID_COMMANDS
    
    def test_valid_entities_list(self, helper):
        """Test that all expected entities are in the valid entities list."""
        expected_entities = [
            'account', 'association', 'cluster', 'coordinator', 'event',
            'federation', 'job', 'problem', 'qos', 'reservation', 'resource',
            'runaway', 'stats', 'transaction', 'tres', 'user', 'wckey'
        ]
        
        for entity in expected_entities:
            assert entity in helper.VALID_ENTITIES


if __name__ == '__main__':
    pytest.main([__file__]) 