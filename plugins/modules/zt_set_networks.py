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
        zt_node_id=dict(type="str", required=True),
        zt_networks=dict(type="list", required=True),
        zt_subnet=dict(type="dict", required=True),
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
    result["data"] = set_networks(module)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def set_networks(module):

    token = module.params["token"]
    zt_network_id = module.params["zt_network_id"]
    zt_node_id = module.params["zt_node_id"]
    networks = module.params["zt_networks"]
    zt_subnet = module.params["zt_subnet"]

    bearer = f"bearer {token}"
    headers = {"Content-Type": "application/json", "Authorization": bearer}
    url = f"https://my.zerotier.com/api/network/{zt_network_id}"

    # networks = [{"target": "10.21.0.0/16", "via": "10.55.0.21"}, {"target": "10.31.0.0/16", "via": "10.55.0.21"}]

    if token or zt_network_id or zt_node_id or networks is not None:

        response_data = requests.get(url, headers=headers)
        response_dict = response_data.json()
        current_route_list = response_dict["config"]["routes"]
        updated_route_list = []
        # check if already routes in zt, if not then skip this loop
        if len(current_route_list) > 0:
            # append new routes to existing but check if they are already there and dont append / duplicate
            for net in networks:
                if net not in current_route_list:
                    current_route_list.append(net)
            # now updated route list should equal current_route_list
            updated_route_list = current_route_list
            # zt_subnet - check its there if its not then append it.
            if zt_subnet not in updated_route_list:
                updated_route_list.append(zt_subnet)

        else:
            updated_route_list = networks
            # Also add the missing ZT subnet
            updated_route_list.append(zt_subnet)

        json_payload = {"config": {"routes": updated_route_list}}

        response_update = requests.post(
            url, headers=headers, data=json.dumps(json_payload)
        )
        data = response_update.json()
        return data
    return {}


def main():
    run_module()


if __name__ == "__main__":
    main()