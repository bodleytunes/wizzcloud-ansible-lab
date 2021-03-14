Starting a new version of the ovh cloud deployment lab but based entirely on Ansible rather than using mostly saltstack.

###### Overview

* Deploys servers from bare metal debian 10 buster
* Install packages, proxmox etc
* Setup Linux networking and bridges using ifupdown2
* Setup encrypted overlay networking via Zerotier-One
* Setup encryption p2p overlay between nodes using Slack Nebula (similar to ZT)
* Custom python ansible execution module to setup the zerotier Networking, add networks / routes etc
* Custom python ansible execution module to deal with OVH API
* Custom Python ansible execution module to control proxmox cli
* Using exec module to interact with proxmox-ve api for networking etc ( using https://github.com/robinelfrink/ansible-proxmox-api )
* Setup inter-host bridge evpn/vxlan overlay via FRR / Free range routing (encapped through Zerotier-one)
* Setup Proxmox cluster
* Kernel Modules
* Disk Partitioning: ZFS zpools and datasets
* LXD system container install via snap / configure lxc related bridges
* UFW firewall and NAT ingress rules
* Haproxy Load balancers with Anycast Loopbacks advertised into BGP
* S3FS Backups to backblaze - S3FS Fuse mounts to directory
* GlusterFS shared storage for stateful apps/storage in rancher/k3s
* LizardFS shared storage for plex/media programs
* Users, SSH Keys, login policy
* Terraform and cloud init templates/images to deploy initial VM's in proxmox
* Deploy K3s (lightweight kubernetes)
* Install Rancher to control K3s

Examples:

###### Run the whole playbook

```
ansible-playbook -i inventory.ini day0.yml --tags ovh_wipe
ansible-playbook -i inventory.ini day0.yml 
```

##### Run plays (groups of roles)
```
ansible-playbook -i inventory.ini day0.yml --tags phase1
ansible-playbook -i inventory.ini day0.yml --tags phase2
etc..
```

##### Run specific Roles

```
 ansible-playbook -i inventory.ini day0.yml --tags proxmox
 ansible-playbook -i inventory.ini day0.yml --tags users
 ansible-playbook -i inventory.ini day0.yml --tags networking
 ansible-playbook -i inventory.ini day0.yml --tags firewall
```

##### Terraform

###### Deploy (Apply)

`ansible-playbook -i inventory.ini day0.yml --tags terraform_deploy`

###### Destroy
`ansible-playbook -i inventory.ini day0.yml --tags terraform_destroy`

##### Day N operations

###### Regenerate Nebula Certs
If you modify the groups the node belongs to you will have to regen and load new certs on the nodes - this is an adhoc run via a tag
`ansible-playbook -i inventory.ini day0.yml --tags regen_certs`

###### Reconfigure the routing Daemon (FRR)
If you make modificaations to the templates or to the vars they consume then run this to reconfigure the routing
`ansible-playbook -i inventory.ini day0.yml --tags reconfigure_frr_routing`