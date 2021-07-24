#!/usr/bin/python3

from __future__ import absolute_import, division, print_function

import subprocess

__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import *

from jinja2 import Template


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        baremetal_hosts=dict(type="list", required=True),
        gluster_volumes=dict(type="dict", required=True),
        gluster_zfs_dataset=dict(type="str", required=True),
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
    result["data"] = create_command(module)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def create_command(module):
    hosts = module.params["baremetal_hosts"]
    volumes = module.params["gluster_volumes"]
    gluster_zfs_dataset = module.params["gluster_zfs_dataset"]

    try:
        for volume in volumes["volumes"]:
            cmd = run_template(
                hosts,
                volume,
                gluster_zfs_dataset,
            )
            result = run_cmd(cmd)

    except BaseException as e:
        raise f"exception {e}"
    return result


def run_cmd(cmd):
    import subprocess

    process = subprocess.Popen(
        [
            cmd,
        ],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    return {"stdout:": stdout, "stderr": stderr}


def run_template(hosts, volume, gluster_zfs_dataset):
    num_of_replicas = len(hosts)
    cmd_location = "/usr/sbin/"
    prefix_cmd = f"{cmd_location}gluster volume create"
    volname = f"{volume['name']}"
    replicas = f"replica {num_of_replicas}"

    cmd_1 = str(f"{prefix_cmd} {volname} {replicas}")
    cmd_dataset = f":/{gluster_zfs_dataset}"

    cmd_3 = ""
    for host in hosts:
        cmd = f"{host}{cmd_dataset}"

        if len(cmd_3) > 0:
            cmd_3 = f"{cmd_3} {cmd}"
        else:
            cmd_3 = f"{cmd}"

    final_cmd = str(f"{cmd_1} {cmd_3} force")

    return final_cmd


def main():
    run_module()


if __name__ == "__main__":
    main()
