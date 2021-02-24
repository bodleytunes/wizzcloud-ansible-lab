#!/usr/bin/python3

from __future__ import absolute_import, division, print_function

import requests

__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import *


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        func=dict(type="str", required=True),
        group_storage_dict=dict(type="dict", required=True),
        host_storage_dict=dict(type="dict", required=False),
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
    result["data"] = pve_operations(module)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def pve_operations(module):

    func = module.params["func"]

    if func == "set_zfs_storage":
        set_zfs_storage(module)
    else:
        return {}


def set_zfs_storage(module):
    group_storage_dict = module.params["group_storage_dict"]
    host_storage_dict = module.params["host_storage_dict"]

    import subprocess

    # pvesm add zfspool "{{ item[0].name }}" -pool "{{item[0].datasets.proxmox}}" --nodes p20,p21 --content rootdir,images
    for zpool in group_storage_dict["zfs"]["zpools"]:

        process = subprocess.Popen(
            [
                "pvesm",
                "add",
                "zfspool",
                zpool["name"],
                "-pool",
                zpool["datasets"]["proxmox"],
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # get nodes as in p20,p21 build string separated by commas
        node_strings = zpool["nodes"]
        joined_string = ",".join(node_strings)
        process = subprocess.Popen(
            ["pvesm", "set", zpool["name"], "--nodes", joined_string],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    stdout, stderr = process.communicate()
    return stdout, stderr


def main():
    run_module()


if __name__ == "__main__":
    main()