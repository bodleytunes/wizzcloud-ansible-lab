#!/usr/bin/python3

from __future__ import absolute_import, division, print_function

import requests

__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import *


def main():

    new_networks = [
        {"target": "10.21.0.0/16", "via": "10.55.0.21"},
        {"target": "10.20.0.0/16", "via": "10.55.0.20"},
        {"target": "10.30.0.0/16", "via": "10.55.0.30"},
    ]
    current_networks = [
        {"target": "10.12.0.0/16", "via": "10.55.0.11"},
        {"target": "10.30.0.0/16", "via": "10.55.0.30"},
    ]

    # remove existing networks from new networks
    for c in current_networks:
        for n in new_networks:
            if n["target"] in c["target"]:
                new_networks.remove(n)

    # merge the two lists
    new_networks = [*current_networks, *new_networks]
    # merge the two dicts
    # new_networks = {**current_networks, **new_networks}

    print(new_networks)


if __name__ == "__main__":
    main()