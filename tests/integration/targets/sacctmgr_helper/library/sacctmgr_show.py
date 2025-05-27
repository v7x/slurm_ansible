#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sacctmgr_show
short_description: Test module for SacctmgrHelper show convenience method
description:
  - This module tests the show convenience method of SacctmgrHelper
  - Used specifically for integration testing of read-only operations
version_added: "1.0.0"
author:
  - Your Name (@yourusername)
options:
  entity:
    description:
      - The entity to show
    required: true
    type: str
    choices: ['account', 'association', 'cluster', 'coordinator', 'event', 'federation', 'job', 'problem', 'qos', 'reservation', 'resource', 'runaway', 'stats', 'transaction', 'tres', 'user', 'wckey']
  options:
    description:
      - Additional options for the show command
    required: false
    type: str
'''

EXAMPLES = r'''
- name: Show cluster information
  sacctmgr_show:
    entity: cluster

- name: Show specific account
  sacctmgr_show:
    entity: account
    options: "name=test format=account,description"
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
  sample: "Cluster information..."
stderr:
  description: Command error output
  returned: always
  type: str
  sample: ""
data:
  description: Parsed JSON data
  returned: when JSON parsing succeeds
  type: dict
  sample: {"clusters": [{"name": "test", "host": "localhost"}]}
changed:
  description: Whether the command made changes (always false for show)
  returned: always
  type: bool
  sample: false
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
        entity=dict(type='str', required=True,
                   choices=['account', 'association', 'cluster', 'coordinator', 'event',
                           'federation', 'job', 'problem', 'qos', 'reservation', 'resource',
                           'runaway', 'stats', 'transaction', 'tres', 'user', 'wckey']),
        options=dict(type='str', required=False)
    )

    # Create the module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Get parameters
    entity = module.params['entity']
    options = module.params['options']

    try:
        # Initialize the helper
        helper = SacctmgrHelper(module)
        
        # Parse options if provided
        parsed_options = None
        if options:
            parsed_options = options
        
        # Execute the show command using convenience method
        result = helper.show(entity, parsed_options)
        
        # Return the result
        module.exit_json(**result)
        
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {str(e)}")


def main():
    """Module entry point."""
    run_module()


if __name__ == '__main__':
    main() 