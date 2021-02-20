#!/usr/bin/python3


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import *
from pathlib import Path

import requests
import json


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict()

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(changed=False, original_message="", message="", data={})

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    # reinstall_servers
    token_dict = get_auth_token()
    result["data"] = token_dict["token"]

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def get_auth_token():

    auth_file = Path("/var/lib/zerotier-one/authtoken.secret")

    if auth_file.is_file():
        # file exists
        file = open("/var/lib/zerotier-one/authtoken.secret", "r")
        token = file.readline()
        token_dict = dict(token=token)
        return token_dict

    else:
        return {}


def main():
    run_module()


if __name__ == "__main__":
    main()