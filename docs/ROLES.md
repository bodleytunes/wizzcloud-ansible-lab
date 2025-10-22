# Ansible Roles Reference Guide

This document provides detailed information about all 43 roles in the WizzCloud Ansible Lab project.

## Table of Contents

- [Core Infrastructure Roles](#core-infrastructure-roles)
- [Networking Roles](#networking-roles)
- [Storage Roles](#storage-roles)
- [Compute & Container Roles](#compute--container-roles)
- [Identity & Access Management Roles](#identity--access-management-roles)
- [Application & Service Roles](#application--service-roles)
- [Infrastructure Management Roles](#infrastructure-management-roles)
- [Support & Configuration Roles](#support--configuration-roles)

---

## Core Infrastructure Roles

### proxmox

**Purpose**: Installs and configures Proxmox VE hypervisor on bare-metal Debian servers.

**Key Functions**:
- Installs Proxmox VE packages and dependencies
- Configures required kernel modules (`vfio`, `vfio_iommu_type1`, `vfio_pci`, `vfio_virqfd`)
- Sets up ZFS storage pools for VM storage
- Configures Proxmox storage resources
- Optimizes system for virtualization

**Tags**: `proxmox`

**Dependencies**: Debian 10 Buster base system

**Key Variables**:
- ZFS pool configurations
- Proxmox storage definitions
- Kernel module parameters

---

### proxmox_clustering

**Purpose**: Forms Proxmox VE clusters and joins nodes to existing clusters.

**Key Functions**:
- Creates new Proxmox clusters on master nodes
- Joins additional nodes to existing clusters
- Configures cluster networking
- Sets up high availability

**Tags**: `proxmox_clustering`

**Execution**: Serial execution (one host at a time) to prevent race conditions

**Dependencies**:
- `proxmox` role must be completed first
- Network connectivity between all cluster nodes

**Key Variables**:
- Cluster name
- Master node designation

---

### proxmox_vm

**Purpose**: Manages Proxmox VM templates and configurations.

**Key Functions**:
- Creates and manages VM templates
- Configures cloud-init for VM provisioning
- Sets up VM defaults and standards

**Tags**: `proxmox_vm`

**Dependencies**: Proxmox cluster operational

---

### storage_proxmox

**Purpose**: Configures Proxmox-specific storage resources.

**Key Functions**:
- Adds storage backends to Proxmox
- Configures GlusterFS storage in Proxmox
- Sets up S3FS backup storage
- Manages storage permissions

**Tags**: `storage_proxmox`

**Dependencies**: Storage systems must be configured first

---

### lxd

**Purpose**: Installs and configures LXD for system containers.

**Key Functions**:
- Installs LXD via snap
- Configures LXD networking bridges
- Sets up container defaults
- Initializes LXD daemon

**Tags**: `lxd`

**Use Case**: Lightweight system containers for specific workloads

---

## Networking Roles

### networking

**Purpose**: Base network configuration including interfaces, routing, and traffic control.

**Key Functions**:
- Installs and configures `ifupdown2` for advanced interface management
- Sets up FRR (Free Range Routing) for BGP/EVPN
- Configures Linux Traffic Control (TC) with CAKE QoS
- Implements DSCP marking with IPtables mangle rules
- Creates network bridges for VMs and containers

**Tags**: `networking`

**Key Technologies**:
- FRR BGP routing daemon
- Linux TC (Traffic Control)
- CAKE QoS algorithm
- DSCP traffic marking

**Key Variables**:
- Interface configurations
- BGP AS numbers and peering
- QoS policies

---

### networking_interfaces

**Purpose**: Manages network interface configuration files.

**Key Functions**:
- Generates `/etc/network/interfaces` configuration
- Configures VLANs and bonds
- Sets up bridge interfaces
- Applies interface configurations

**Tags**: `networking_interfaces`

**Dependencies**: `ifupdown2` package installed

---

### networking_frr

**Purpose**: Configures FRR (Free Range Routing) for dynamic routing.

**Key Functions**:
- Installs FRR routing daemon
- Configures BGP routing
- Sets up EVPN/VXLAN overlays
- Advertises routes and anycast addresses
- Manages routing policies

**Tags**: `networking_frr`, `reconfigure_frr_routing`

**Key Features**:
- BGP for dynamic routing
- EVPN/VXLAN for L2 overlay networks
- Anycast IP advertisement for load balancing
- Route filtering and policies

**Key Variables**:
- BGP AS number
- Router ID
- Network advertisements
- Neighbor configurations

---

### networking_nebula

**Purpose**: Deploys Slack Nebula encrypted P2P overlay mesh network.

**Key Functions**:
- Installs Nebula daemon
- Generates or distributes Nebula certificates
- Configures Nebula lighthouses (rendezvous points)
- Sets up Nebula firewall rules
- Creates encrypted mesh between all nodes

**Tags**: `networking_nebula`, `regen_certs`

**Key Features**:
- Certificate-based authentication
- Encrypted P2P tunneling
- Lighthouse-based discovery
- Firewall integrated with Nebula

**Key Variables**:
- CA configuration
- Lighthouse addresses
- IP assignments
- Firewall rules

---

### zerotier_networking

**Purpose**: Configures ZeroTier-One overlay networking.

**Key Functions**:
- Installs ZeroTier-One daemon
- Joins ZeroTier networks
- Configures static IP assignments via API
- Sets interface MTU
- Authorizes nodes via ZeroTier API

**Tags**: `zerotier_networking`

**Custom Modules Used**:
- `zt_get_auth_token`
- `zt_authorize`
- `zt_check_networks`
- `zt_get_interface_name`
- `zt_set_networks`
- `zt_set_ip`
- `zt_set_mtu`
- `zt_set_name`

**Key Variables**:
- ZeroTier network IDs
- API tokens
- Static IP assignments

---

### githubixx.ansible_role_wireguard

**Purpose**: Configures Wireguard VPN tunnels (external role).

**Key Functions**:
- Installs Wireguard kernel module and tools
- Generates Wireguard keys
- Configures point-to-point tunnels
- Sets up routing for tunneled traffic

**Tags**: `wireguard`

**Source**: https://github.com/githubixx/ansible-role-wireguard

**Use Case**: Site-to-site VPN, specific encrypted tunnels

---

### networking_docker_bridges

**Purpose**: Configures Docker bridge and overlay networks.

**Key Functions**:
- Creates custom Docker bridge networks
- Configures Docker overlay networks for Swarm
- Sets up network isolation
- Manages Docker network driver options

**Tags**: `docker_networks`

**Dependencies**: Docker installed

---

### vm_networking

**Purpose**: Configures networking for virtual machines.

**Key Functions**:
- Sets up VM network interfaces
- Configures VM routing
- Manages VM DNS settings
- Integrates VMs with overlay networks

**Tags**: `vm_networking`

**Target**: Virtual machine guests

---

### firewall

**Purpose**: Configures UFW (Uncomplicated Firewall) rules.

**Key Functions**:
- Enables and configures UFW
- Sets up firewall rules from group variables
- Configures NAT and forwarding rules
- Manages ingress rules for services

**Tags**: `firewall`

**Key Variables**:
- `ufw_rules` - List of firewall rules
- NAT configurations
- Forwarding policies

---

## Storage Roles

### storage_configuration

**Purpose**: Primary storage orchestration role.

**Key Functions**:
- Orchestrates GlusterFS deployment
- Configures Samba file sharing
- Sets up S3FS cloud storage mounts
- Manages storage dependencies

**Tags**: `storage`

**Dependencies**: Block devices and filesystems ready

---

### storage_zfs

**Purpose**: Manages ZFS zpools and datasets.

**Key Functions**:
- Creates ZFS storage pools
- Configures ZFS datasets
- Sets ZFS properties (compression, dedup, etc.)
- Manages ZFS snapshots and replication
- Optimizes ZFS for workload

**Tags**: `storage_zfs`

**Key Features**:
- Copy-on-write filesystem
- Built-in compression
- Snapshot support
- Data integrity checking

**Key Variables**:
- Zpool configurations
- Dataset definitions
- ZFS properties

---

### storage_glusterfs

**Purpose**: Deploys GlusterFS distributed storage cluster.

**Key Functions**:
- Installs GlusterFS server packages
- Creates trusted storage pools
- Configures GlusterFS volumes (replicated, distributed, etc.)
- Starts and manages GlusterFS services
- Optimizes volume settings

**Tags**: `storage_glusterfs`

**Key Features**:
- Distributed and replicated storage
- Scale-out NAS
- POSIX-compliant
- Self-healing

**Key Variables**:
- Volume configurations
- Replica counts
- Brick locations

---

### storage_glusterfs_client

**Purpose**: Mounts GlusterFS volumes on client systems.

**Key Functions**:
- Installs GlusterFS client packages
- Mounts GlusterFS volumes
- Configures fstab entries
- Optimizes mount options

**Tags**: `storage_glusterfs_client`

**Target**: VMs and nodes consuming GlusterFS storage

---

### storage_samba

**Purpose**: Configures Samba SMB/CIFS file sharing.

**Key Functions**:
- Installs Samba server
- Configures Samba shares
- Sets up user authentication
- Manages share permissions

**Tags**: `storage_samba`

**Use Case**: Windows-compatible file sharing

**Key Variables**:
- Share definitions
- User credentials
- Access permissions

---

### storage_linstor

**Purpose**: Deploys LINSTOR DRBD replicated block storage.

**Key Functions**:
- Installs LINSTOR controller and satellites
- Configures DRBD kernel module
- Creates storage pools
- Manages replicated volumes
- Integrates with Proxmox

**Tags**: `storage_linstor`

**Key Features**:
- Synchronous replication
- Block-level storage
- Proxmox integration
- High availability

**Key Variables**:
- Controller node
- Storage pool definitions
- Replication policies

---

## Compute & Container Roles

### k3s

**Purpose**: Deploys K3s lightweight Kubernetes distribution.

**Key Functions**:
- Installs K3s server (control plane)
- Joins K3s agents (worker nodes)
- Configures K3s with custom options
- Disables default components (Traefik, ServiceLB)
- Sets up kubectl and kubeconfig

**Tags**: `k3s_deploy`, `k3s`

**Key Features**:
- Lightweight Kubernetes (< 100MB)
- Single binary installation
- Optimized for edge/IoT
- Full Kubernetes compatibility

**Key Variables**:
- K3s version
- K3s token
- Server options
- Node taints and labels

---

### vm_configuration_kubernetes

**Purpose**: Configures Kubernetes cluster on VMs with additional components.

**Key Functions**:
- Deploys K3s on virtual machines
- Installs Rancher for cluster management
- Deploys MetalLB for load balancing
- Configures Helm package manager
- Sets up Cert-Manager for certificates

**Tags**: `vm_configuration_kubernetes`, `post_k3s`

**Components Installed**:
- Rancher (Kubernetes management UI)
- MetalLB (bare-metal load balancer)
- Helm (package manager)
- Cert-Manager (certificate automation)

**Key Variables**:
- Rancher hostname
- MetalLB IP range
- Helm repositories

---

### docker

**Purpose**: Installs Docker container runtime.

**Key Functions**:
- Installs Docker CE (Community Edition)
- Configures Docker daemon
- Sets up Docker networks
- Manages Docker storage drivers
- Enables Docker service

**Tags**: `docker`

**Key Variables**:
- Docker daemon options
- Storage driver configuration
- Network settings

---

### rancher

**Purpose**: Deploys Rancher Kubernetes management platform.

**Key Functions**:
- Installs Rancher on K3s cluster
- Configures Rancher ingress
- Sets up Rancher authentication
- Manages Rancher namespaces

**Tags**: `rancher`

**Dependencies**: K3s cluster operational

**Use Case**: Multi-cluster Kubernetes management UI

---

### portainer

**Purpose**: Deploys Portainer Docker management UI.

**Key Functions**:
- Installs Portainer container
- Configures Portainer volumes
- Sets up Portainer authentication
- Exposes Portainer web interface

**Tags**: `portainer`

**Use Case**: Docker container management and monitoring

---

## Identity & Access Management Roles

### freeipa

**Purpose**: Deploys FreeIPA identity management server.

**Key Functions**:
- Installs FreeIPA server (master)
- Configures FreeIPA replica nodes
- Sets up DNS and DHCP integration
- Configures Kerberos authentication
- Manages FreeIPA domains and realms

**Tags**: `freeipa`

**Key Features**:
- Centralized identity management
- LDAP directory service
- Kerberos authentication
- DNS management
- Certificate authority

**Node Types**:
- **IPA Master**: Primary identity server
- **IPA Replica**: Redundant identity servers

**Key Variables**:
- Domain name
- Realm
- Admin credentials
- DNS configuration

---

### freeipa_client

**Purpose**: Enrolls systems as FreeIPA clients.

**Key Functions**:
- Installs FreeIPA client packages
- Enrolls systems in FreeIPA domain
- Configures SSSD for authentication
- Sets up Kerberos on clients
- Manages host certificates

**Tags**: `freeipa_client`

**Custom Modules**: Uses custom enrollment modules

**Target**: All VMs and hosts requiring centralized authentication

---

### freeipa_users

**Purpose**: Manages FreeIPA user accounts.

**Key Functions**:
- Creates FreeIPA user accounts
- Manages user groups
- Sets user permissions
- Configures RBAC policies

**Tags**: `freeipa_users`

**Dependencies**: FreeIPA server operational

---

### ssh_keys

**Purpose**: Distributes SSH public keys to authorized hosts.

**Key Functions**:
- Manages SSH authorized_keys files
- Distributes user SSH public keys
- Configures SSH key-based authentication
- Removes unauthorized keys

**Tags**: `ssh_keys`

**Key Variables**:
- User SSH public keys
- Key distribution mappings

---

### users

**Purpose**: Creates and manages system user accounts.

**Key Functions**:
- Creates user accounts
- Configures user shells
- Sets up home directories
- Manages user permissions and groups
- Configures sudo access

**Tags**: `users`

**Key Variables**:
- User definitions
- Group memberships
- Sudo permissions

---

### gravitational_teleport

**Purpose**: Deploys Gravitational Teleport SSH replacement and access control.

**Key Functions**:
- Installs Teleport binaries
- Configures Teleport auth servers
- Sets up Teleport proxy servers
- Enrolls Teleport clients (nodes)
- Manages Teleport certificates
- Configures anycast for auth servers

**Tags**: `gravitational_teleport`, `configure_teleport_auth_server`, `configure_teleport_proxy_server`, `configure_teleport_clients`

**Node Types**:
- **Auth Server**: Certificate authority and authentication
- **Proxy Server**: SSH proxy and web UI
- **Client Nodes**: Systems managed by Teleport

**Key Features**:
- Certificate-based SSH authentication
- Session recording
- RBAC for SSH access
- Web-based terminal
- Audit logging

**Anycast Integration**: Auth servers advertise anycast IPs via BGP for high availability

**Key Variables**:
- Teleport cluster name
- Auth server addresses
- Proxy addresses
- Join tokens

---

## Application & Service Roles

### openvpn_pritunl

**Purpose**: Deploys Pritunl OpenVPN server for remote access.

**Key Functions**:
- Installs Pritunl server
- Configures OpenVPN tunnels
- Integrates with FRR BGP for route advertisement
- Manages Pritunl users and organizations
- Sets up Pritunl web UI

**Tags**: `pritunl_server`

**Key Features**:
- OpenVPN-based VPN
- Web management interface
- Multi-organization support
- BGP route injection

**Integration**: Routes advertised via BGP to enable seamless network access

**Key Variables**:
- Pritunl server configuration
- Organization settings
- BGP integration options

---

### powerdns

**Purpose**: Deploys PowerDNS authoritative DNS server.

**Key Functions**:
- Installs PowerDNS server
- Configures DNS zones
- Sets up PowerDNS API
- Manages DNS records
- Integrates with backends (MySQL, PostgreSQL)

**Tags**: `powerdns`

**Use Case**: Authoritative DNS with API management

**Key Variables**:
- DNS zones
- PowerDNS backend configuration
- API settings

---

### elasticsearch

**Purpose**: Deploys Elasticsearch for logging and search.

**Key Functions**:
- Installs Elasticsearch cluster
- Configures Elasticsearch nodes
- Sets up index templates
- Manages cluster settings
- Integrates with Kibana

**Tags**: `elasticsearch`

**Use Case**: Centralized logging, log search and analysis

**Key Variables**:
- Cluster name
- Node configurations
- Index settings

---

### syslog-ng

**Purpose**: Deploys Syslog-ng for centralized logging.

**Key Functions**:
- Installs Syslog-ng daemon
- Configures log sources and destinations
- Sets up log filtering
- Manages log rotation
- Integrates with Elasticsearch

**Tags**: `syslog_ng`

**Use Case**: Centralized syslog collection and forwarding

**Key Variables**:
- Log sources
- Destinations
- Filters and parsers

---

### webtop

**Purpose**: Deploys Webtop web-based desktop environment.

**Key Functions**:
- Runs Webtop Docker container
- Configures Webtop environment
- Sets up Webtop authentication
- Exposes Webtop via web interface

**Tags**: `webtop`

**Use Case**: Web-based Linux desktop accessible via browser

**Technology**: Docker-based containerized desktop

---

### bertvv.dhcp

**Purpose**: Deploys ISC DHCP server (external role).

**Key Functions**:
- Installs ISC DHCP server
- Configures DHCP scopes
- Manages reservations
- Sets DHCP options

**Tags**: `dhcp_servers`

**Source**: https://github.com/bertvv/ansible-role-dhcp

**Use Case**: DHCP service for network infrastructure

---

## Infrastructure Management Roles

### terraform

**Purpose**: Provisions Proxmox VMs using Terraform.

**Key Functions**:
- Deploys Terraform binary
- Generates Terraform configurations for VMs
- Applies Terraform plans
- Provisions VMs on Proxmox
- Configures cloud-init for VMs

**Tags**: `terraform_deploy`, `vm_deploy`

**Key Features**:
- Infrastructure as Code for VM provisioning
- Declarative VM definitions
- Proxmox provider integration

**Terraform Configurations**: Located in `terraform/` directory

**Key Variables**:
- VM specifications (CPU, RAM, disk)
- Network configurations
- Cloud-init templates

---

### terraform_destroy

**Purpose**: Destroys infrastructure provisioned by Terraform.

**Key Functions**:
- Runs `terraform destroy`
- Removes VMs from Proxmox
- Cleans up Terraform state

**Tags**: `terraform_destroy`

**Use Case**: Infrastructure teardown and cleanup

---

### ovh

**Purpose**: Manages OVH dedicated servers via OVH API.

**Key Functions**:
- Wipes OVH servers (reinstalls OS)
- Checks server status
- Reboots servers
- Configures server settings via API

**Tags**: `ovh_wipe`, `ovh_operations`

**Custom Modules**:
- `ovh_wipe.py` - Server reinstallation
- `ovh_status.py` - Server status queries

**Key Variables**:
- OVH API credentials
- Server names/IDs

**Use Case**: Automated bare-metal server provisioning on OVH/SoyouStart

---

## Support & Configuration Roles

### common

**Purpose**: Common tasks applied across all systems.

**Key Functions**:
- System dist-upgrade
- Package installation and updates
- System reboots
- DNS configuration
- Basic Docker installation
- Hostname configuration

**Tags**: `common`, `dist_upgrade`, `reboot`

**Use Case**: Standard system maintenance tasks

**Key Tasks**:
- `apt update && apt dist-upgrade`
- System reboot with wait
- Package cache management

---

### day0_pre

**Purpose**: Pre-deployment preparation tasks.

**Key Functions**:
- Prepares systems for deployment
- Validates prerequisites
- Sets up initial configurations
- Performs system checks

**Tags**: `day0_pre`, `host_pre`

**Execution**: First role in Day 0 deployment

**Key Tasks**:
- System validation
- Prerequisite checks
- Initial system hardening

---

### install_required_packages

**Purpose**: Installs required system packages.

**Key Functions**:
- Installs base packages for infrastructure
- Updates package cache
- Installs Python dependencies
- Installs network utilities

**Tags**: `install_required_packages`

**Package Categories**:
- System utilities
- Network tools
- Development libraries
- Python packages

**Key Packages**:
- `vim`, `htop`, `tmux` (utilities)
- `curl`, `wget`, `net-tools` (networking)
- `python3`, `python3-pip` (Python)
- `git`, `jq` (development)

---

## Role Dependencies and Execution Order

### Recommended Deployment Order

1. **Day 0 Pre-Configuration**:
   - `day0_pre`
   - `users`
   - `ssh_keys`
   - `install_required_packages`

2. **Hypervisor Setup**:
   - `proxmox`
   - `proxmox_clustering`

3. **Networking**:
   - `networking`
   - `networking_interfaces`
   - `networking_frr`
   - `zerotier_networking`
   - `networking_nebula`
   - `wireguard`

4. **Storage**:
   - `storage_zfs`
   - `storage_glusterfs`
   - `storage_linstor`
   - `storage_configuration`

5. **Virtualization**:
   - `terraform` (VM deployment)
   - `vm_networking`

6. **Identity & Access**:
   - `freeipa`
   - `freeipa_client`
   - `gravitational_teleport`

7. **Applications**:
   - `docker`
   - `k3s`
   - `vm_configuration_kubernetes`
   - `rancher`

8. **Services**:
   - `powerdns`
   - `openvpn_pritunl`
   - `elasticsearch`
   - `syslog-ng`

---

## Role Tagging Strategy

Roles are tagged for flexible execution:

- **Individual Role Tags**: Execute single role (e.g., `--tags proxmox`)
- **Phase Tags**: Execute groups of roles (e.g., `--tags phase1`, `--tags phase2`)
- **Functional Tags**: Execute related roles (e.g., `--tags networking`, `--tags storage`)
- **Operational Tags**: Day-N tasks (e.g., `--tags dist_upgrade`, `--tags reconfigure_frr_routing`)

### Common Tag Patterns

```bash
# Individual component
--tags proxmox

# Related components
--tags networking

# Deployment phase
--tags phase1

# Day-N operation
--tags reconfigure_frr_routing
```

---

## Custom Ansible Modules

Many roles leverage custom Python modules located in `plugins/modules/`:

### ZeroTier Modules
- `zt_get_auth_token.py`
- `zt_authorize.py`
- `zt_check_networks.py`
- `zt_get_interface_name.py`
- `zt_get_node_id.py`
- `zt_set_networks.py`
- `zt_set_ip.py`
- `zt_set_mtu.py`
- `zt_set_name.py`
- `zt_set_description.py`

### Proxmox Modules
- `pve_api.py` - Proxmox API interface
- `pve_operations.py` - VM operations, snapshots, etc.

### OVH Modules
- `ovh_wipe.py` - Server reinstallation
- `ovh_status.py` - Server status queries

### Storage Modules
- `gluster_func.py` - GlusterFS operations

---

## External Roles

The project includes two external roles from Ansible Galaxy:

1. **githubixx.ansible_role_wireguard**
   - Repository: https://github.com/githubixx/ansible-role-wireguard
   - Purpose: Wireguard VPN configuration
   - Integration: Git submodule

2. **bertvv.dhcp**
   - Repository: https://github.com/bertvv/ansible-role-dhcp
   - Purpose: ISC DHCP server
   - Integration: Ansible Galaxy

---

## Role Development Guidelines

When creating or modifying roles:

1. **Idempotency**: Ensure roles can be run multiple times safely
2. **Tagging**: Add appropriate tags for flexible execution
3. **Variables**: Use group_vars for configuration
4. **Documentation**: Document role purpose, variables, and dependencies
5. **Testing**: Test roles individually before full deployment
6. **Error Handling**: Include proper error handling and validation
7. **Logging**: Provide meaningful output for debugging

---

## Troubleshooting Roles

### Debugging Individual Roles

```bash
# Run role with verbose output
ansible-playbook -i inventory.ini day0.yml --tags role_name -vvv

# Check role tasks
ansible-playbook -i inventory.ini day0.yml --tags role_name --list-tasks

# Dry run (check mode)
ansible-playbook -i inventory.ini day0.yml --tags role_name --check

# Limit to specific host
ansible-playbook -i inventory.ini day0.yml --tags role_name --limit hostname
```

### Common Role Issues

**Role Not Found**:
- Verify role exists in `roles/` directory
- Check `roles_path` in ansible.cfg

**Variable Not Defined**:
- Check group_vars and host_vars
- Verify variable hierarchy
- Use `ansible-inventory --list` to debug variables

**Dependencies Not Met**:
- Review role dependencies
- Ensure prerequisite roles have run
- Check for required packages or services

---

This comprehensive role reference provides the foundation for understanding and working with the WizzCloud Ansible Lab infrastructure.
