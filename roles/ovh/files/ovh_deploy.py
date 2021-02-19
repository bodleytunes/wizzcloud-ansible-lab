import json
import sys
import ovh
from ovh.client import ENDPOINTS
import yaml
import os
import pytest


# def get_ovh_secrets():
#
#    dir = os.path.dirname(os.path.realpath(__file__))
#    full_path = dir + "/" + ".ovh_module_vars.yml"
#    with open(full_path) as file:
#        secrets_file = yaml.load(file, Loader=yaml.FullLoader)
#    ovh_secrets = secrets_file["ovh"]
#
#    return ovh_secrets


def get_client_auth():

    client = get_client()

    result = client.post(
        "/auth/credential",
        accessRules=[
            {"method": "GET", "path": "/*"},
            {"method": "POST", "path": "/*"},
            {"method": "PUT", "path": "/*"},
            {"method": "DELETE", "path": "/*"},
        ],
        redirection=None,
    )

    return result


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


def print_result(client):
    print(json.dumps(client, indent=4))


def print_results(results):

    for key, value in results.items():
        print(json.dumps(key, indent=4))
        print(json.dumps(value, indent=4))


@pytest.mark.ovh
@pytest.mark.ovh_install
def reinstall_servers():

    client = get_client()
    server_inventory = get_server_inventory()

    # re-install servers
    for server in server_inventory:
        friendly_name = server["friendly_name"]
        retreived_hostname = server["hostname"]
        start_install(client, server=retreived_hostname, friendly_name=friendly_name)


def main(*args):
    o = OvhDeploy(*args)

    o.reinstall_servers()


# main()
# run initialize to get consumer key
# initialize()
# run reinstall servers to reinstall all servers

# run get install status to get progress of reinstallation
# get_install_status()


class OvhDeploy:
    """
    Deploy baremetal via ovh API
    """

    COMMON_SSH_ARGS = "-o StrictHostKeyChecking=no"

    def __init__(self, *args):
        self.endpoint = sys.argv[1]
        self.application_key = sys.argv[2]
        self.application_secret = sys.argv[3]
        self.consumer_key = sys.argv[4]
        self.server_inventory = sys.argv[5]

    def get_secrets(self) -> dict:

        ovh_secrets = {}
        ovh_secrets["endpoint"] = self.endpoint
        ovh_secrets["application_key"] = self.application_key
        ovh_secrets["application_secret"] = self.application_secret
        ovh_secrets["consumer_key"] = self.consumer_key

        return ovh_secrets

    def reinstall_servers(self):
        secrets = self.get_secrets()
        client = self.get_client(secrets)
        server_inventory = self.server_inventory

        # re-install servers
        for server in server_inventory:
            friendly_name = server["friendly_name"]
            retreived_hostname = server["hostname"]
            start_install(
                client, server=retreived_hostname, friendly_name=friendly_name
            )

    def get_client(self, secrets):

        ovh_secrets = secrets

        client = ovh.Client(
            endpoint=ovh_secrets["endpoint"],
            application_key=ovh_secrets["application_key"],
            application_secret=ovh_secrets["application_secret"],
            consumer_key=ovh_secrets["consumer_key"],
        )

        return client


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
