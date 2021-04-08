Starting a new version of the ovh cloud deployment lab but based entirely on Ansible rather than using mostly saltstack.

###### Overview

* Deploys servers from bare metal debian 10 buster
* Install packages, proxmox etc
* Setup Linux networking and bridges using ifupdown2
* Setup encrypted overlay networking via Zerotier-One
* Setup encryption p2p overlay between nodes using Slack Nebula (similar to ZT)
* Setup encrypted P2P overlay between nodes using Wireguard (useing wireguard role from https://github.com/githubixx/ansible-role-wireguard)
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
* Install Linstor DRBD replicated storage
* Users, SSH Keys, login policy
* Terraform and cloud init templates/images to deploy initial VM's in proxmox
* Deploy K3s (lightweight kubernetes)
* Install Rancher to control K3s
* Install FreeIPA server and replica on main nodes for DNS and IDM
* Install FreeIPA client and enroll virtual machines
* Install Gravitational Teleport auth, proxy and clients for an alternative to SSH and key based auth
* Gravitational Auth server advertises and listens on anycast loopback.  This done via BGP as its 10.0.0.6 address is unreachable from non local baremetal host due to anycast MAC addresses on shared evpn stretched segment causing reply issues (basically if the remote gw sends a frame with its anycast mac as the src, the reply will return to the local gw and thus is blackholed).


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

##### Day N operational tasks

###### Regenerate Nebula Certs
If you modify the groups the node belongs to you will have to regen and load new certs on the nodes - this is an adhoc run via a tag
`ansible-playbook -i inventory.ini day0.yml --tags regen_certs`

###### Reconfigure the routing Daemon (FRR)
If you make modificaations to the templates or to the vars they consume then run this to reconfigure the routing
`ansible-playbook -i inventory.ini day0.yml --tags reconfigure_frr_routing`

###### Dist upgrade baremetal hosts + vm's
`ansible-playbook -i inventory.ini operations.yml --tags dist_upgrade`

###### Setup s3fs backup storage device in proxmox
`ansible-playbook -i inventory.ini operations.yml --tags setup_s3fs`

###### Configure Teleport

`ansible-playbook -i inventory.ini adhoc.yml  --tags configure_teleport_auth_server`

`ansible-playbook -i inventory.ini adhoc.yml  --tags configure_teleport_proxy_server`

`ansible-playbook -i inventory.ini adhoc.yml  --tags configure_teleport_clients`




###### Extra Notes for kubernetes quorum node on Raspberry Pi4

###### on pi4 list
cat /boot/cmdline.txt
---
```
 console=tty1 root=PARTUUID=ad09722e-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait net.ifnames=0 cgroup_memory=1 cgroup_enable=memory cgroup_enable=cpuset
```

###### k3s install on pi4

`curl -fL https://get.k3s.io |  INSTALL_K3S_CHANNEL=stable   K3S_TOKEN=token_goes_here sh -s - --server https://10.100.0.100:6443  --node-ip 10.55.0.11 --node-taint k3s-controlplane=true:NoExecute --disable traefik --disable servicelb`

###### Add a new VM after deployment (Day N Operations)

add to inventory.ini
add to correct groups in inventory e.g. ipa_clients requires a group that the vm belongs to.


`pritunl.wizznet.co.uk ansible_host=10.0.0.7 ansible_user=jon`

run dist-upgrade

`ansible-playbook -i inventory.ini operations.yml  --tags dist_upgrade`


run vm_networking

`ansible-playbook -i inventory.ini day0.yml  --tags vm_networking`

join IPA / IDM

`ansible-playbook -i inventory.ini day0.yml  --tags freeipa_client`

join Teleport SSH

`ansible-playbook -i inventory.ini operations.yml  --tags configure_teleport_clients`


###### VM Post Ops

`ansible-playbook -i inventory.ini post_operations_vm.yml`

###### VM Add k3s host

`ansible-playbook -i inventory.ini day0.yml --tags vm_configuration_kubernetes`

###### example deployment using day0 playbook but running groups of roles

```
ansible-playbook -i inventory.ini day0.yml --tags host_pre
ansible-playbook -i inventory.ini day0.yml --tags freeipa
ansible-playbook -i inventory.ini day0.yml --tags wireguard
ansible-playbook -i inventory.ini day0.yml --tags proxmox_clustering
ansible-playbook -i inventory.ini day0.yml --tags networking
ansible-playbook -i inventory.ini day0.yml --tags lxd
ansible-playbook -i inventory.ini day0.yml --tags dhcp_servers
ansible-playbook -i inventory.ini day0.yml --tags storage
ansible-playbook -i inventory.ini day0.yml --tags vm_pre
ansible-playbook -i inventory.ini day0.yml --tags vm_deploy
ansible-playbook -i inventory.ini day0.yml --tags vm_post 
ansible-playbook -i inventory.ini day0.yml --tags gravitational_teleport
ansible-playbook -i inventory.ini day0.yml --tags freeipa_client
ansible-playbook -i inventory.ini day0.yml --tags docker
ansible-playbook -i inventory.ini day0.yml --tags pritunl_server
ansible-playbook -i inventory.ini day0.yml --tags k3s_deploy
ansible-playbook -i inventory.ini day0.yml --tags k3s_apps
```