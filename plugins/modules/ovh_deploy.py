#!/usr/bin/python3

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import *
import ovh


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        endpoint=dict(type="str", required=True),
        application_key=dict(type="str", required=True),
        application_secret=dict(type="str", required=True),
        consumer_key=dict(type="str", required=True),
        server_inventory=dict(type="list", required=True),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(changed=False, original_message="", message="")

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
    reinstall_servers(module)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def reinstall_servers(module):
    secrets = get_secrets(module)
    client = get_client(secrets)
    server_inventory = module.params["server_inventory"]
    # re-install servers
    for server in server_inventory:
        friendly_name = server["friendly_name"]
        retreived_hostname = server["hostname"]
        start_install(client, server=retreived_hostname, friendly_name=friendly_name)


def get_secrets(module) -> dict:
    ovh_secrets = {}
    ovh_secrets["endpoint"] = module.params["endpoint"]
    ovh_secrets["application_key"] = module.params["application_key"]
    ovh_secrets["application_secret"] = module.params["application_secret"]
    ovh_secrets["consumer_key"] = module.params["consumer_key"]
    return ovh_secrets


def get_client(secrets):
    ovh_secrets = secrets
    client = ovh.Client(
        endpoint=ovh_secrets["endpoint"],
        application_key=ovh_secrets["application_key"],
        application_secret=ovh_secrets["application_secret"],
        consumer_key=ovh_secrets["consumer_key"],
    )
    return client


def start_install(client, server, friendly_name):

    # create details  type
    details = {
        "customHostname": friendly_name,
        "noRaid": True,
        "resetHwRaid": True,
        "sshKeyName": "troon",
    }

    result = client.post(
        f"/dedicated/server/{server}/install/start",
        partitionSchemeName="jons-partition-latest",  # Partition scheme name (type: string)
        templateName="wiz-debian-10",  # Template name (type: string)
        details=details,  # parameters for default install (complex type: dedicated.server.InstallCustom)
    )

    return result


def main():
    run_module()


if __name__ == "__main__":
    main()