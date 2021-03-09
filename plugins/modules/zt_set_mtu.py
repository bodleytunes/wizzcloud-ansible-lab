#!/usr/bin/python3

from __future__ import absolute_import, division, print_function

import requests

__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import *


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        token=dict(type="str", required=True),
        zt_network_id=dict(type="str", required=True),
        mtu=dict(type="int", required=True),
    )

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
    result["data"] = set_mtu(module)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def set_mtu(module):

    token = module.params["token"]
    zt_network_id = module.params["zt_network_id"]
    mtu = module.params["mtu"]

    bearer = f"bearer {token}"
    headers = {"Content-Type": "application/json", "Authorization": bearer}
    url = f"https://my.zerotier.com/api/network/{zt_network_id}"

    # {% set script_final_line = "'{\"config\": {\"ipAssignments\": [\"" + hostvars.zt_ip +"\"]} }'" %}
    json_payload = {"config": {"mtu": mtu}}

    if token or zt_network_id or mtu is not None:
        response = requests.post(url, headers=headers, data=json.dumps(json_payload))
        data = response.json()
        return data
    return {}


def main():
    run_module()


if __name__ == "__main__":
    main()