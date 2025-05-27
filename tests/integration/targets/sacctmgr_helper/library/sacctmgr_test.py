#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sacctmgr_test
short_description: Test module for SacctmgrHelper integration tests
description:
  - This module is used for testing the SacctmgrHelper class in integration tests
  - It provides a direct interface to test sacctmgr command functionality
version_added: "1.0.0"
author:
  - Your Name (@yourusername)
options:
  command:
    description:
      - The sacctmgr command to execute
    required: true
    type: str
    choices: ['add', 'create', 'delete', 'remove', 'modify', 'update', 'show', 'list', 'dump', 'load', 'archive', 'clear']
  entity:
    description:
      - The entity to operate on
    required: true
    type: str
    choices: ['account', 'association', 'cluster', 'coordinator', 'event', 'federation', 'job', 'problem', 'qos', 'reservation', 'resource', 'runaway', 'stats', 'transaction', 'tres', 'user', 'wckey']
  options:
    description:
      - Additional options for the command
    required: false
    type: str
  use_json:
    description:
      - Whether to request JSON output
    required: false
    type: bool
    default: true
  use_readonly:
    description:
      - Whether to use readonly mode
    required: false
    type: bool
'''

EXAMPLES = r'''
- name: Show cluster information
  sacctmgr_test:
    command: show
    entity: cluster
    options: "format=cluster,controlhost"

- name: Add test account
  sacctmgr_test:
    command: add
    entity: account
    options: "name=test description='Test Account'"
    use_json: false

- name: Show account with JSON
  sacctmgr_test:
    command: show
    entity: account
    options: "name=test"
    use_json: true
'''

RETURN = r'''
success:
  description: Whether the command succeeded
  returned: always
  type: bool
  sample: true
stdout:
  description: Command output
  returned: always
  type: str
  sample: "Account test created successfully"
stderr:
  description: Command error output
  returned: always
  type: str
  sample: ""
data:
  description: Parsed JSON data if JSON was requested and parsing succeeded
  returned: when JSON output is available
  type: dict
  sample: {"accounts": [{"name": "test", "description": "Test Account"}]}
changed:
  description: Whether the command made changes
  returned: always
  type: bool
  sample: true
command:
  description: The actual command that was executed
  returned: always
  type: str
  sample: "/usr/bin/sacctmgr --immediate --json add account name=test"
'''

import sys
import os

# Add the module_utils path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'module_utils'))

from ansible.module_utils.basic import AnsibleModule
from sacctmgr_helper import SacctmgrHelper


def run_module():
    """Main module execution function."""
    
    # Define module arguments
    module_args = dict(
        command=dict(type='str', required=True,
                    choices=['add', 'create', 'delete', 'remove', 'modify', 'update', 
                            'show', 'list', 'dump', 'load', 'archive', 'clear']),
        entity=dict(type='str', required=True,
                   choices=['account', 'association', 'cluster', 'coordinator', 'event',
                           'federation', 'job', 'problem', 'qos', 'reservation', 'resource',
                           'runaway', 'stats', 'transaction', 'tres', 'user', 'wckey']),
        options=dict(type='str', required=False),
        use_json=dict(type='bool', required=False, default=True),
        use_readonly=dict(type='bool', required=False)
    )

    # Create the module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Get parameters
    command = module.params['command']
    entity = module.params['entity']
    options = module.params['options']
    use_json = module.params['use_json']
    use_readonly = module.params['use_readonly']

    try:
        # Initialize the helper
        helper = SacctmgrHelper(module)
        
        # Parse options if provided
        parsed_options = None
        if options:
            parsed_options = options
        
        # Execute the command
        result = helper.run_command(
            command=command,
            entity=entity,
            options=parsed_options,
            use_json=use_json,
            use_readonly=use_readonly
        )
        
        # Return the result
        module.exit_json(**result)
        
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {str(e)}")


def main():
    """Module entry point."""
    run_module()


if __name__ == '__main__':
    main() 