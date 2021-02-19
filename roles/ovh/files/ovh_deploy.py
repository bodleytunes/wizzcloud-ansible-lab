import json
import ovh
import yaml
import os
import pytest


def initialize():
    try:
        my_input = input
    except NameError:
        pass

    client = get_client()

    # Request RO, /me API access
    ck = client.new_consumer_key_request()
    # ck.add_rules(ovh.API_READ_ONLY, "/me")
    ck.add_recursive_rules(ovh.API_READ_WRITE, "/")

    # Request token
    validation = ck.request()

    print("Please visit %s to authenticate" % validation["validationUrl"])
    input("and press Enter to continue...")

    # Print nice welcome message
    print("Welcome", client.get("/me")["firstname"])
    print("Btw, your 'consumerKey' is '%s'" % validation["consumerKey"])


def get_ovh_secrets():

    dir = os.path.dirname(os.path.realpath(__file__))
    full_path = dir + "/" + ".ovh_module_vars.yml"
    with open(full_path) as file:
        secrets_file = yaml.load(file, Loader=yaml.FullLoader)
    ovh_secrets = secrets_file["ovh"]

    return ovh_secrets


def get_server_inventory() -> list:

    dir = os.path.dirname(os.path.realpath(__file__))
    full_path = dir + "/" + ".ovh_module_vars.yml"
    with open(full_path) as file:
        secrets_file = yaml.load(file, Loader=yaml.FullLoader)

    server_inventory = secrets_file["ovh"]["servers"]

    return server_inventory


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


def get_client():

    ovh_secrets = get_ovh_secrets()

    client = ovh.Client(
        endpoint=ovh_secrets["endpoint"],
        application_key=ovh_secrets["application_key"],
        application_secret=ovh_secrets["application_secret"],
        consumer_key=ovh_secrets["consumer_key"],
    )

    return client


def get_services(client):
    services = client.get("/dedicated/server")
    return services


def get_service_details(client, service):
    service_details = client.get(f"/dedicated/server/{service}")
    return service_details


def get_templates(client):
    templates = client.get("/dedicated/installationTemplate")
    return templates


def get_my_templates(client):
    templates = client.get("/me/installationTemplate")
    return templates


@pytest.mark.ovh
@pytest.mark.ovh_get_partition_schemes
def get_partition_schemes(client=get_client(), template_name="wiz-debian-10"):
    pscheme = client.get(f"/me/installationTemplate/{template_name}/partitionScheme")
    print_result(pscheme)
    return pscheme


@pytest.mark.ovh
@pytest.mark.ovh_get_partition_scheme
def get_partition_scheme(
    client=get_client(),
    template_name="wiz-debian-10",
    scheme_name="jons-partition-latest",
):
    pscheme = client.get(
        f"/me/installationTemplate/{template_name}/partitionScheme/{scheme_name}"
    )
    print_result(pscheme)
    return pscheme


@pytest.mark.ovh_get_partitions
def get_partitions(
    client=get_client(),
    template_name="wiz-debian-10",
    scheme_name="jons-partition-latest",
):
    pscheme = client.get(
        f"/me/installationTemplate/{template_name}/partitionScheme/{scheme_name}/partition"
    )
    print_result(pscheme)
    return pscheme


@pytest.mark.ovh_add_partition
def add_partition_scheme(client=get_client(), template_name="wiz-debian-10"):
    p = client.post(
        f"/me/installationTemplate/{template_name}/partitionScheme",
        name="jons-partition-latest",
        priority=10,
    )
    print_result(p)
    return


@pytest.mark.ovh_add_partition_hardware_raid
def add_partition_scheme_hwraid(
    client=get_client(),
    template_name="wiz-debian-10",
    scheme_name="jons-partition-latest",
):
    p = client.post(
        f"/me/installationTemplate/{template_name}/partitionScheme/{scheme_name}/partition",
        filesystem="ext4",
        mountpoint="/",
        size=120000,
        step=1,
        type="primary",
    )
    print_result(p)
    return


@pytest.mark.ovh_add_partition_hardware_raid_swap
def add_partition_scheme_hwraid_swap(
    client=get_client(),
    template_name="wiz-debian-10",
    scheme_name="jons-partition-latest",
):
    p = client.post(
        f"/me/installationTemplate/{template_name}/partitionScheme/{scheme_name}/partition",
        filesystem="swap",
        mountpoint="/swap",
        size=4000,
        step=2,
        type="primary",
    )
    print_result(p)
    return


def get_disk_groups(client, service):
    disk_groups = client.get(f"/dedicated/server/{service}/specifications/hardware")
    return disk_groups


@pytest.mark.ovh
@pytest.mark.ovh_get_status
def get_install_status():

    client = get_client()
    server_inventory = get_server_inventory()

    for item in server_inventory:
        service_name = item["hostname"]
        try:
            status = client.get(f"/dedicated/server/{service_name}/install/status")
            print_result(status)
        except:
            print("Not installing ")


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


def main():

    client = get_client()

    results = {
        "services": get_services(client),
        "service_details": get_service_details(client),
        "templates": get_templates(client),
        "my_templates": get_my_templates(client),
        "partition_schemes": get_partition_schemes(client),
        "partitions": get_partitions(client),
        "disk_groups": get_disk_groups(client),
    }

    # install_results = {
    #    "installation": start_install(client, servers=get_services(client))
    # }

    print_results(results)


# main()
# run initialize to get consumer key
# initialize()
# run reinstall servers to reinstall all servers
reinstall_servers()

# run get install status to get progress of reinstallation
# get_install_status()