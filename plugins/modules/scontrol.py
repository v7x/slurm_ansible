#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: my_module
short_description: This is my custom Ansible module
version_added: "1.0.0"
description:
    - "This is my longer description explaining the module's purpose"
options:
    name:
        description:
            - This is the name parameter for the module
        required: true
        type: str
    state:
        description:
            - Whether the resource should exist or not
        choices: ['present', 'absent']
        default: present
        type: str
author:
    - Your Name (@yourgithub)
'''

EXAMPLES = r'''
# A simple example
- name: Create a resource
  my_module:
    name: example
    state: present

# Remove a resource
- name: Remove a resource
  my_module:
    name: example
    state: absent
'''

RETURN = r'''
original_message:
    description: The original name param that was passed in
    type: str
    returned: always
    sample: 'example'
message:
    description: The output message that the module generates
    type: str
    returned: always
    sample: 'Resource created successfully'
'''

from ansible.module_utils.basic import AnsibleModule

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )

    # seed the result dict in the object
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # manipulate or modify the state as needed
    result['original_message'] = module.params['name']
    
    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current state
    if module.check_mode:
        module.exit_json(**result)

    # during normal operation, perform the actual work
    if module.params['state'] == 'present':
        # Implement logic for 'present' state
        result['changed'] = True
        result['message'] = 'Resource created successfully'
    else:
        # Implement logic for 'absent' state
        result['changed'] = True
        result['message'] = 'Resource removed successfully'

    # return collected results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main() 