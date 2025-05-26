#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import subprocess
import json
import shlex
from ansible.module_utils.basic import AnsibleModule


class ScontrolHelper(object):
    """
    Helper class for scontrol command wrapper.
    Provides a safe interface to execute scontrol commands with validation.
    """

    # Valid scontrol commands
    VALID_COMMANDS = [
        'cancel_reboot', 'create', 'completing', 'delete', 'errnumstr',
        'fsdampeningfactor', 'getaddrs', 'help', 'hold', 'notify', 'pidinfo',
        'listjobs', 'listpids', 'liststeps', 'ping', 'power', 'reboot',
        'reconfigure', 'release', 'requeue', 'requeuehold', 'resume',
        'schedloglevel', 'setdebug', 'setdebugflags', 'show', 'shutdown',
        'suspend', 'takeover', 'top', 'token', 'uhold', 'update', 'version',
        'wait_job', 'write'
    ]
    
    # Commands that support JSON output
    JSON_SUPPORTED_COMMANDS = ['show']
    
    # Show command entities that support JSON
    JSON_SUPPORTED_ENTITIES = [
        'job', 'node', 'partition', 'reservation', 'config', 'licenses',
        'step', 'topology', 'assoc_mgr', 'burstbuffer', 'federation',
        'frontend', 'slurmd'
    ]
    
    # Commands that are read-only (don't modify system state)
    READONLY_COMMANDS = [
        'show', 'ping', 'version', 'help', 'completing', 'listjobs',
        'listpids', 'liststeps', 'pidinfo', 'getaddrs', 'errnumstr'
    ]
    
    # Valid entities for show command
    SHOW_ENTITIES = [
        'aliases', 'assoc_mgr', 'bbstat', 'burstbuffer', 'config', 'daemons',
        'dwstat', 'federation', 'frontend', 'hostlist', 'hostlistsorted',
        'hostnames', 'job', 'licenses', 'node', 'partition', 'reservation',
        'slurmd', 'step', 'topology'
    ]
    
    # Valid entities for update command
    UPDATE_ENTITIES = [
        'job', 'step', 'node', 'partition', 'reservation', 'frontend'
    ]
    
    # Valid entities for create command
    CREATE_ENTITIES = [
        'node', 'partition', 'reservation'
    ]
    
    # Valid entities for delete command
    DELETE_ENTITIES = [
        'node', 'partition', 'reservation'
    ]

    def __init__(self, module):
        """
        Initialize the helper with an Ansible module instance.
        
        Args:
            module: AnsibleModule instance
        """
        self.module = module
        self.scontrol_path = self._find_scontrol()
        
    def _find_scontrol(self):
        """
        Find the scontrol executable path.
        
        Returns:
            str: Path to scontrol executable
            
        Raises:
            Fails the module if scontrol is not found
        """
        try:
            result = subprocess.run(['which', 'scontrol'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            self.module.fail_json(msg="scontrol command not found in PATH")
    
    def validate_command(self, command):
        """
        Validate that the command is a valid scontrol command.
        
        Args:
            command (str): The scontrol command to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            Fails the module if command is invalid
        """
        if command.lower() not in self.VALID_COMMANDS:
            self.module.fail_json(
                msg=f"Invalid scontrol command: {command}. "
                    f"Valid commands are: {', '.join(self.VALID_COMMANDS)}"
            )
        return True
    
    def validate_show_entity(self, entity):
        """
        Validate that the entity is valid for show commands.
        
        Args:
            entity (str): The entity to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            Fails the module if entity is invalid
        """
        if entity.lower() not in self.SHOW_ENTITIES:
            self.module.fail_json(
                msg=f"Invalid show entity: {entity}. "
                    f"Valid entities are: {', '.join(self.SHOW_ENTITIES)}"
            )
        return True
    
    def validate_update_entity(self, entity):
        """
        Validate that the entity is valid for update commands.
        
        Args:
            entity (str): The entity to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            Fails the module if entity is invalid
        """
        if entity.lower() not in self.UPDATE_ENTITIES:
            self.module.fail_json(
                msg=f"Invalid update entity: {entity}. "
                    f"Valid entities are: {', '.join(self.UPDATE_ENTITIES)}"
            )
        return True
    
    def validate_create_entity(self, entity):
        """
        Validate that the entity is valid for create commands.
        
        Args:
            entity (str): The entity to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            Fails the module if entity is invalid
        """
        if entity.lower() not in self.CREATE_ENTITIES:
            self.module.fail_json(
                msg=f"Invalid create entity: {entity}. "
                    f"Valid entities are: {', '.join(self.CREATE_ENTITIES)}"
            )
        return True
    
    def validate_delete_entity(self, entity):
        """
        Validate that the entity is valid for delete commands.
        
        Args:
            entity (str): The entity to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            Fails the module if entity is invalid
        """
        if entity.lower() not in self.DELETE_ENTITIES:
            self.module.fail_json(
                msg=f"Invalid delete entity: {entity}. "
                    f"Valid entities are: {', '.join(self.DELETE_ENTITIES)}"
            )
        return True
    
    def _build_command(self, command, options=None, use_json=True):
        """
        Build the complete scontrol command with appropriate flags.
        
        Args:
            command (str): The scontrol command
            options (list/str): Additional command options
            use_json (bool): Whether to add --json flag
            
        Returns:
            list: Complete command as list of arguments
        """
        cmd = [self.scontrol_path]
        
        # Add --json for supported commands
        if use_json and command.lower() in self.JSON_SUPPORTED_COMMANDS:
            # For show commands, check if the entity supports JSON
            if command.lower() == 'show' and options:
                # Extract entity from options
                entity = None
                if isinstance(options, list) and len(options) > 0:
                    entity = options[0].lower()
                elif isinstance(options, str):
                    entity = options.split()[0].lower()
                
                if entity and entity in self.JSON_SUPPORTED_ENTITIES:
                    cmd.append('--json')
        
        # Add the main command
        cmd.append(command)
        
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
    
    def run_command(self, command, options=None, use_json=True):
        """
        Execute a scontrol command and return the results.
        
        Args:
            command (str): The scontrol command to run
            options (list/str): Additional command options
            use_json (bool): Whether to request JSON output
            
        Returns:
            dict: Command execution results with keys:
                - success (bool): Whether command succeeded
                - stdout (str): Command output
                - stderr (str): Command error output
                - data (dict/list): Parsed JSON data if JSON was used
                - changed (bool): Whether the command made changes
        """
        # Validate command
        self.validate_command(command)
        
        # Additional validation based on command type
        if command.lower() == 'show' and options:
            entity = None
            if isinstance(options, list) and len(options) > 0:
                entity = options[0]
            elif isinstance(options, str):
                entity = options.split()[0]
            
            if entity:
                self.validate_show_entity(entity)
        
        elif command.lower() == 'update' and options:
            entity = None
            if isinstance(options, list) and len(options) > 0:
                entity = options[0]
            elif isinstance(options, str):
                entity = options.split()[0]
            
            if entity:
                self.validate_update_entity(entity)
        
        elif command.lower() == 'create' and options:
            entity = None
            if isinstance(options, list) and len(options) > 0:
                entity = options[0]
            elif isinstance(options, str):
                entity = options.split()[0]
            
            if entity:
                self.validate_create_entity(entity)
        
        elif command.lower() == 'delete' and options:
            entity = None
            if isinstance(options, list) and len(options) > 0:
                entity = options[0]
            elif isinstance(options, str):
                entity = options.split()[0]
            
            if entity:
                self.validate_delete_entity(entity)
        
        # Build the command
        cmd = self._build_command(command, options, use_json)
        
        # Determine if this command makes changes
        is_readonly = command.lower() in self.READONLY_COMMANDS
        
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
    
    def show(self, entity, identifier=None, use_json=True):
        """
        Convenience method for show commands.
        
        Args:
            entity (str): The entity to show (job, node, partition, etc.)
            identifier (str): Optional identifier (job ID, node name, etc.)
            use_json (bool): Whether to request JSON output
            
        Returns:
            dict: Command results
        """
        options = [entity]
        if identifier:
            options.append(identifier)
        
        return self.run_command('show', options, use_json)
    
    def update(self, entity, specification):
        """
        Convenience method for update commands.
        
        Args:
            entity (str): The entity to update (job, node, partition, etc.)
            specification (str): The update specification
            
        Returns:
            dict: Command results
        """
        options = [entity, specification]
        return self.run_command('update', options, use_json=False)
    
    def hold(self, job_list):
        """
        Convenience method for hold commands.
        
        Args:
            job_list (str): Comma-separated list of job IDs
            
        Returns:
            dict: Command results
        """
        return self.run_command('hold', [job_list], use_json=False)
    
    def release(self, job_list):
        """
        Convenience method for release commands.
        
        Args:
            job_list (str): Comma-separated list of job IDs
            
        Returns:
            dict: Command results
        """
        return self.run_command('release', [job_list], use_json=False)
    
    def suspend(self, job_list):
        """
        Convenience method for suspend commands.
        
        Args:
            job_list (str): Comma-separated list of job IDs
            
        Returns:
            dict: Command results
        """
        return self.run_command('suspend', [job_list], use_json=False)
    
    def resume(self, job_list):
        """
        Convenience method for resume commands.
        
        Args:
            job_list (str): Comma-separated list of job IDs
            
        Returns:
            dict: Command results
        """
        return self.run_command('resume', [job_list], use_json=False)
    
    def create(self, entity, specification):
        """
        Convenience method for create commands.
        
        Args:
            entity (str): The entity to create (node, partition, reservation)
            specification (str): The creation specification
            
        Returns:
            dict: Command results
        """
        options = [entity, specification]
        return self.run_command('create', options, use_json=False)
    
    def delete(self, entity, specification):
        """
        Convenience method for delete commands.
        
        Args:
            entity (str): The entity to delete (node, partition, reservation)
            specification (str): The deletion specification
            
        Returns:
            dict: Command results
        """
        options = [entity, specification]
        return self.run_command('delete', options, use_json=False) 