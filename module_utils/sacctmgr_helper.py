#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import subprocess
import json
import shlex
from ansible.module_utils.basic import AnsibleModule


class SacctmgrHelper(object):
    """
    Helper class for sacctmgr command wrapper.
    Provides a safe interface to execute sacctmgr commands with validation.
    """

    # Valid sacctmgr commands
    VALID_COMMANDS = [
        'add', 'create', 'delete', 'remove', 'modify', 'update', 
        'show', 'list', 'dump', 'load', 'archive', 'clear'
    ]
    
    # Valid entities that sacctmgr can operate on
    VALID_ENTITIES = [
        'account', 'association', 'cluster', 'coordinator', 'event',
        'federation', 'job', 'problem', 'qos', 'reservation', 'resource',
        'runaway', 'stats', 'transaction', 'tres', 'user', 'wckey'
    ]
    
    # Commands that are read-only and should use --readonly flag
    READONLY_COMMANDS = ['show', 'list', 'dump']
    
    # Commands that support JSON output
    JSON_SUPPORTED_COMMANDS = ['show', 'list', 'dump']

    def __init__(self, module):
        """
        Initialize the helper with an Ansible module instance.
        
        Args:
            module: AnsibleModule instance
        """
        self.module = module
        self.sacctmgr_path = self._find_sacctmgr()
        
    def _find_sacctmgr(self):
        """
        Find the sacctmgr executable path.
        
        Returns:
            str: Path to sacctmgr executable
            
        Raises:
            Fails the module if sacctmgr is not found
        """
        try:
            result = subprocess.run(['which', 'sacctmgr'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            self.module.fail_json(msg="sacctmgr command not found in PATH")
    
    def validate_command(self, command):
        """
        Validate that the command is a valid sacctmgr command.
        
        Args:
            command (str): The sacctmgr command to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            Fails the module if command is invalid
        """
        if command.lower() not in self.VALID_COMMANDS:
            self.module.fail_json(
                msg=f"Invalid sacctmgr command: {command}. "
                    f"Valid commands are: {', '.join(self.VALID_COMMANDS)}"
            )
        return True
    
    def validate_entity(self, entity):
        """
        Validate that the entity is a valid sacctmgr entity.
        
        Args:
            entity (str): The entity to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            Fails the module if entity is invalid
        """
        if entity.lower() not in self.VALID_ENTITIES:
            self.module.fail_json(
                msg=f"Invalid sacctmgr entity: {entity}. "
                    f"Valid entities are: {', '.join(self.VALID_ENTITIES)}"
            )
        return True
    
    def _build_command(self, command, entity, options=None, use_json=True, use_readonly=None):
        """
        Build the complete sacctmgr command with appropriate flags.
        
        Args:
            command (str): The sacctmgr command
            entity (str): The entity to operate on
            options (list): Additional command options
            use_json (bool): Whether to add --json flag
            use_readonly (bool): Whether to add --readonly flag (auto-detected if None)
            
        Returns:
            list: Complete command as list of arguments
        """
        cmd = [self.sacctmgr_path]
        
        # Add --immediate flag for non-interactive operation
        cmd.append('--immediate')
        
        # Add --readonly for read-only commands
        if use_readonly is None:
            use_readonly = command.lower() in self.READONLY_COMMANDS
        if use_readonly:
            cmd.append('--readonly')
        
        # Add --json for supported commands
        if use_json and command.lower() in self.JSON_SUPPORTED_COMMANDS:
            cmd.append('--json')
        
        # Add the main command and entity
        cmd.extend([command, entity])
        
        # Add any additional options
        if options:
            if isinstance(options, str):
                # Parse string options safely
                cmd.extend(shlex.split(options))
            elif isinstance(options, list):
                cmd.extend(options)
            else:
                self.module.fail_json(msg="Options must be a string or list")
        
        return cmd
    
    def run_command(self, command, entity, options=None, use_json=True, use_readonly=None):
        """
        Execute a sacctmgr command and return the results.
        
        Args:
            command (str): The sacctmgr command to run
            entity (str): The entity to operate on
            options (list/str): Additional command options
            use_json (bool): Whether to request JSON output
            use_readonly (bool): Whether to use readonly mode (auto-detected if None)
            
        Returns:
            dict: Command execution results with keys:
                - success (bool): Whether command succeeded
                - stdout (str): Command output
                - stderr (str): Command error output
                - data (dict/list): Parsed JSON data if JSON was used
                - changed (bool): Whether the command made changes
        """
        # Validate inputs
        self.validate_command(command)
        self.validate_entity(entity)
        
        # Build the command
        cmd = self._build_command(command, entity, options, use_json, use_readonly)
        
        # Determine if this command makes changes
        is_readonly = use_readonly if use_readonly is not None else command.lower() in self.READONLY_COMMANDS
        
        result = {
            'success': False,
            'stdout': '',
            'stderr': '',
            'data': None,
            'changed': not is_readonly,
            'command': ' '.join(cmd)
        }
        
        try:
            # Execute the command
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            result['stdout'] = proc.stdout
            result['stderr'] = proc.stderr
            result['success'] = proc.returncode == 0
            
            # Parse JSON output if requested and command succeeded
            if (result['success'] and use_json and 
                command.lower() in self.JSON_SUPPORTED_COMMANDS and 
                result['stdout'].strip()):
                try:
                    result['data'] = json.loads(result['stdout'])
                except json.JSONDecodeError as e:
                    # JSON parsing failed, but command succeeded
                    result['json_parse_error'] = str(e)
            
            # If command failed, include error details
            if not result['success']:
                result['changed'] = False
                
        except subprocess.TimeoutExpired:
            self.module.fail_json(msg=f"Command timed out after 300 seconds: {' '.join(cmd)}")
        except Exception as e:
            self.module.fail_json(msg=f"Failed to execute command: {str(e)}")
        
        return result
    
    def show(self, entity, options=None):
        """
        Convenience method for show commands.
        
        Args:
            entity (str): The entity to show
            options (list/str): Additional options
            
        Returns:
            dict: Command results
        """
        return self.run_command('show', entity, options, use_json=True, use_readonly=True)
    
    def add(self, entity, options=None):
        """
        Convenience method for add commands.
        
        Args:
            entity (str): The entity to add
            options (list/str): Additional options
            
        Returns:
            dict: Command results
        """
        return self.run_command('add', entity, options, use_json=False, use_readonly=False)
    
    def delete(self, entity, options=None):
        """
        Convenience method for delete commands.
        
        Args:
            entity (str): The entity to delete
            options (list/str): Additional options
            
        Returns:
            dict: Command results
        """
        return self.run_command('delete', entity, options, use_json=False, use_readonly=False)
    
    def modify(self, entity, options=None):
        """
        Convenience method for modify commands.
        
        Args:
            entity (str): The entity to modify
            options (list/str): Additional options
            
        Returns:
            dict: Command results
        """
        return self.run_command('modify', entity, options, use_json=False, use_readonly=False) 