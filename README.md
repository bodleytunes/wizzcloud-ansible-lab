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
* Gravitational Auth server advertises and listens on anycast loopback.  This done via BGP as its 10.0.0.6 address is unreachable from non local baremetal host due to anycast MAC addresses on shared evpn stretched segment causing reply issues (basically if the remote gw sends a frame with its anycast mac, the reply goes to the local gw and thus is blackholed).


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


###### Notes for kubernetes quorum node on Raspberry Pi4

###### on pi4 list
cat /boot/cmdline.txt
---
```
 console=tty1 root=PARTUUID=ad09722e-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait net.ifnames=0 cgroup_memory=1 cgroup_enable=memory cgroup_enable=cpuset
```

###### k3s install on pi4

`curl -fL https://get.k3s.io |  INSTALL_K3S_CHANNEL=stable   K3S_TOKEN=token_goes_here sh -s - --server https://10.100.0.100:6443  --node-ip 10.55.0.11 --node-taint k3s-controlplane=true:NoExecute --disable traefik --disable servicelb`