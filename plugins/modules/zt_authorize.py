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
        authorize=dict(type="bool", required=True),
        hostname=dict(type="str", required=True),
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
    result["data"] = set_authorize_node(module)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def check_exists(token: str, zt_network_id: str, node: str):

    bearer = f"bearer {token}"
    headers = {"Content-Type": "application/json", "Authorization": bearer}
    url = f"https://my.zerotier.com/api/network/{zt_network_id}/member"

    # json_payload = {"config": {"authorized": authorize}}

    # full curl api example to central zerotier controller
    # curl -v -X POST https://my.zerotier.com/api/network/1_____d/member/64b124492d --header "Content-Type: application/json" --header "Authorization: bearer [secret-api-token-goes-here-fnowfjwnonf]" -d '{"config": {"authorized": true}}'

    if token or zt_network_id is not None:

        response_data = requests.get(url, headers=headers)
        # deserialize
        response_dict = response_data.json()

        if len(response_dict) > 0:
            for r in response_dict:
                new_url = ""

                if node in (r["description"] or r["name"]):
                    # delete entry
                    # curl -v -X DELETE -H 'X-ZT1-Auth: 62___5264a' http://localhost:9993/controller/network/2d___9ee/member/0123456789
                    new_url = url + "/" + r["nodeId"]
                    response = requests.delete(new_url, headers=headers)

    return


def set_authorize_node(module):

    token = module.params["token"]
    zt_network_id = module.params["zt_network_id"]
    zt_node_id = module.params["zt_node_id"]
    authorize = module.params["authorize"]
    node = module.params["hostname"]

    # first delete any existing
    check_exists(token, zt_network_id, node)

    bearer = f"bearer {token}"
    headers = {"Content-Type": "application/json", "Authorization": bearer}
    url = f"https://my.zerotier.com/api/network/{zt_network_id}/member/{zt_node_id}"
    # note that the authorize variable has to be a boolean not a string
    json_payload = {"config": {"authorized": authorize}}

    # full curl api example to central zerotier controller
    # curl -v -X POST https://my.zerotier.com/api/network/1_____d/member/64b124492d --header "Content-Type: application/json" --header "Authorization: bearer [secret-api-token-goes-here-fnowfjwnonf]" -d '{"config": {"authorized": true}}'

    if token or zt_network_id or zt_node_id is not None:
        # serialize the json
        response = requests.post(url, headers=headers, data=json.dumps(json_payload))
        data = response.json()
        return data
    return {}


def main():
    run_module()


if __name__ == "__main__":
    main()