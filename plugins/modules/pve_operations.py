#!/usr/bin/python3

from __future__ import absolute_import, division, print_function

import requests
import subprocess

__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import *


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        func=dict(type="str", required=True),
        group_storage_dict=dict(type="dict", required=False),
        host_storage_dict=dict(type="dict", required=False),
        template_ids=dict(type="list", required=False),
        zpool_name=dict(type=str, required=False),
        image_name=dict(type=str, required=False),
        s3fs=dict(type=dict, required=False),
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


def pve_operations(module) -> dict:

    func = module.params["func"]

    if func == "set_zfs_storage":
        set_zfs_storage(module)
    if func == "set_s3fs_storage":
        set_s3fs_storage(module)
    elif func == "create_template":
        result = create_template(module)
        return result
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
    return {"stdout:": stdout, "stderr": stderr}


def set_s3fs_storage(module):
    s3fs = module.params["s3fs"]
    # host_storage_dict = module.params["host_storage_dict"]

    import subprocess

    # pvesm add zfspool "{{ item[0].name }}" -pool "{{item[0].datasets.proxmox}}" --nodes p20,p21 --content rootdir,images
    # for zpool in group_storage_dict["zfs"]["zpools"]:

    process = subprocess.Popen(
        [
            "pvesm",
            "add",
            s3fs["type"],
            s3fs["name"],
            f"--path={s3fs['backup_folder']}",
            "--content=backup",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # get nodes as in p20,p21 auto build string separated by commas
    node_strings = s3fs["nodes"]
    joined_string = ",".join(node_strings)
    process = subprocess.Popen(
        ["pvesm", "set", s3fs["name"], "--nodes", joined_string],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    return {"stdout:": stdout, "stderr": stderr}


def create_template(module):

    template_ids = module.params["template_ids"]
    zpool_name = module.params["zpool_name"]
    image_name = module.params["image_name"]

    # qm create {{ template_id }} -name ubuntu-cloudinit-{{ template_id }} -memory 1024 -net0 virtio,bridge=lxdbr0 -cores 1 -sockets 1 -cpu cputype=host -description "Ubuntu 20.04 Cloud" -kvm 1 -numa 1

    result = {}

    for t in template_ids:
        template = t["vm_template_id"]
        # check existence
        existence = check_exists(template)
        if not existence:
            # create instance
            result["instance_result"] = qm_create_instance(template)
            # import image from iso to a template
            result["image_result"] = qm_import_image(template, image_name, zpool_name)
            # image associations
            result["properties_result"] = set_image_properties(template, zpool_name)
            # convert to template
            result["templates_result"] = convert_to_template(template)

    return result


def qm_create_instance(template):
    process = subprocess.Popen(
        [
            "qm",
            "create",
            template,
            "-name",
            f"ubuntu-cloudinit-{template}",
            "-memory",
            "1024",
            "-net0",
            "virtio,bridge=lxdbr0",
            "-cores",
            "1",
            "-sockets",
            "1",
            "-cpu",
            "cputype=host",
            "-description",
            "Ubuntu 20.04 Cloud",
            "-kvm",
            "1",
            "-numa",
            "1",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, stderr = process.communicate()

    return stdout, stderr


def qm_import_image(template, image_name, zpool_name):

    process = subprocess.Popen(
        [
            "qm",
            "importdisk",
            template,
            f"/var/lib/vz/template/iso/{image_name}",
            zpool_name,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()

    return stdout, stderr


def set_image_properties(template, zpool_name):

    process = subprocess.Popen(
        [
            "qm",
            "set",
            template,
            "--startup",
            "c",
            "up=45",
            "-agent",
            "1",
            "-hotplug",
            "disk,network,usb,memory,cpu",
            "-vcpus",
            "1",
            "-vga",
            "qx1",
            "-ide2",
            f"{zpool_name}:cloudinit",
        ]
    )
    stdout, stderr = process.communicate()

    process = subprocess.Popen(
        [
            "qm",
            "set",
            template,
            "-serial0",
            "socket",
        ]
    )
    stdout, stderr = process.communicate()

    process = subprocess.Popen(
        [
            "qm",
            "set",
            template,
            "-boot",
            "c",
            "-bootdisk",
            "virtio0",
        ]
    )
    stdout, stderr = process.communicate()

    process = subprocess.Popen(
        [
            "qm",
            "set",
            template,
            "-scsihw",
            "virtio-scsi-pci",
        ]
    )
    stdout, stderr = process.communicate()

    process = subprocess.Popen(
        [
            "qm",
            "set",
            template,
            "-virtio0",
            f"{zpool_name}:vm-{template}-disk-0",
        ]
    )
    stdout, stderr = process.communicate()

    process = subprocess.Popen(["qm", "set", template, "--startup", "up=45"])
    stdout, stderr = process.communicate()

    process = subprocess.Popen(["qm", "set", template, "-agent", "1"])
    stdout, stderr = process.communicate()

    process = subprocess.Popen(
        ["qm", "set", template, "-hotplug", "disk,network,usb,memory,cpu"]
    )
    stdout, stderr = process.communicate()

    process = subprocess.Popen(["qm", "set", template, "-vcpus", "1"])
    stdout, stderr = process.communicate()

    process = subprocess.Popen(["qm", "set", template, "-vga", "qx1"])
    stdout, stderr = process.communicate()

    process = subprocess.Popen(
        ["qm", "set", template, "-name", "ubuntu-20-04-template"]
    )
    stdout, stderr = process.communicate()

    process = subprocess.Popen(
        ["qm", "set", template, "-ide2", f"{zpool_name}:cloudinit"]
    )
    stdout, stderr = process.communicate()

    process = subprocess.Popen(
        ["qm", "set", template, "-name", f"{template}-ubuntu-20-04-template"]
    )
    stdout, stderr = process.communicate()

    # modify vnics based on template id
    if template == ("9005" or "9006"):
        process = subprocess.Popen(
            ["qm", "set", template, "-net1", "virtio,bridge=evpn100"]
        )
        stdout, stderr = process.communicate()
    # modify vnics based on template id
    elif template == ("9007" or "9008"):
        process = subprocess.Popen(
            ["qm", "set", template, "-net0", "virtio,bridge=evpn100"]
        )
        stdout, stderr = process.communicate()

    # resize disk
    process = subprocess.Popen(
        [
            "qm",
            "resize",
            template,
            "virtio0",
            "+8G",
        ]
    )
    stdout, stderr = process.communicate()

    stdout = (subprocess.PIPE,)
    stderr = (subprocess.PIPE,)

    stdout, stderr = process.communicate()

    return stdout, stderr


def convert_to_template(template):

    # convert to template
    process = subprocess.Popen(
        ["qm", "template", template],
    )

    stdout, stderr = process.communicate()

    return stdout, stderr


def check_exists(template) -> bool:
    process = subprocess.Popen(
        [
            "zfs",
            "list",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # get returned output of command
    stdout, stderr = process.communicate()
    # check output for existence
    if template in (str(stdout) or str(stderr)):
        print("true")
        return True
    else:
        print("false")
        return False


def main():
    run_module()


if __name__ == "__main__":
    main()