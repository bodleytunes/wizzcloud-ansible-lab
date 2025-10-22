# WizzCloud Ansible Lab

Enterprise-scale Ansible automation for deploying and managing hybrid cloud infrastructure across multiple cloud providers (OVH SoyouStart and Hetzner Cloud).

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Deployment Guide](#deployment-guide)
- [Day-N Operations](#day-n-operations)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Overview

**WizzCloud Ansible Lab** is a comprehensive Infrastructure-as-Code (IaC) solution that automates the deployment and management of a sophisticated hybrid cloud environment. The project transforms bare-metal Debian servers into a fully-functional private cloud infrastructure with hypervisors, virtual machines, Kubernetes clusters, distributed storage, and advanced networking.

### What This Project Does

- **Day 0 Deployment**: Automated bare-metal server provisioning from fresh Debian installation to production-ready infrastructure
- **Day N Operations**: Ongoing operational tasks including updates, configuration changes, and infrastructure modifications
- **Multi-Cloud Support**: Deploys across OVH SoyouStart and Hetzner Cloud providers
- **Complete Stack**: Manages everything from bare metal to containerized applications

### Key Technologies

- **Hypervisor**: Proxmox VE clustering
- **Networking**: FRR BGP/EVPN, Nebula, ZeroTier, Wireguard overlays
- **Storage**: ZFS, GlusterFS, LINSTOR, S3FS
- **Orchestration**: Kubernetes (K3s) with Rancher
- **Identity**: FreeIPA for DNS and identity management
- **Access**: Gravitational Teleport for SSH replacement
- **VPN**: Pritunl/OpenVPN for remote access

## Features

### Infrastructure Management

- **Bare-Metal Provisioning**: Deploy from fresh Debian 10 Buster installations
- **Hypervisor Clustering**: Proxmox VE cluster setup with high availability
- **VM Orchestration**: Terraform-based VM deployment with cloud-init
- **Container Platform**: K3s Kubernetes with Rancher management

### Advanced Networking

- **Multiple Overlay Networks**:
  - Slack Nebula for P2P encrypted mesh networking
  - ZeroTier-One for encrypted overlay tunneling
  - Wireguard for site-to-site VPN
- **BGP Routing**: FRR (Free Range Routing) with EVPN/VXLAN overlays
- **Traffic Management**: Linux TC with CAKE QoS for video traffic optimization
- **Anycast Load Balancing**: HAProxy with BGP anycast advertisements
- **DSCP Marking**: IPtables mangle rules for traffic prioritization

### Storage Solutions

- **ZFS**: High-performance zpools and datasets
- **GlusterFS**: Distributed storage for stateful Kubernetes applications
- **LINSTOR**: DRBD-based replicated block storage
- **S3FS**: Cloud backup integration with Backblaze
- **LizardFS**: Media storage for Plex and streaming applications
- **Samba**: SMB/CIFS file sharing

### Identity & Access

- **FreeIPA**: Centralized identity management with master and replica nodes
- **Gravitational Teleport**: Modern SSH replacement with certificate-based authentication
- **SSH Key Management**: Centralized key distribution and management
- **Pritunl/OpenVPN**: Secure remote access VPN

### Security & Compliance

- **UFW Firewall**: Comprehensive firewall rules and NAT configurations
- **Encrypted Overlays**: All inter-node communication encrypted
- **Certificate Management**: Automated cert management with Cert-Manager
- **SSSD Integration**: System Security Services Daemon for authentication

### Custom Modules

The project includes 16 custom Python Ansible modules for specialized operations:

- **ZeroTier API**: Complete ZeroTier network management
- **Proxmox API**: VM and hypervisor control
- **OVH API**: Dedicated server management and provisioning
- **GlusterFS**: Distributed storage operations

## Architecture

### Infrastructure Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Applications Layer                       │
│  (Rancher, K3s, Plex, Elasticsearch, Docker Services)       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Orchestration Layer                         │
│        (Kubernetes K3s, Docker, Terraform, FreeIPA)         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Virtualization Layer                        │
│              (Proxmox VE Cluster, LXD, VMs)                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                             │
│         (ZFS, GlusterFS, LINSTOR, S3FS, Samba)             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Network Layer                             │
│    (FRR BGP, Nebula, ZeroTier, Wireguard, EVPN/VXLAN)      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Bare-Metal Layer                           │
│         (Debian 10 Buster on OVH/Hetzner Servers)          │
└─────────────────────────────────────────────────────────────┘
```

### Network Architecture

The project implements a sophisticated multi-overlay network architecture:

1. **Physical Layer**: Bare-metal servers with public IPs
2. **Overlay Layer 1**: ZeroTier/Nebula encrypted mesh for inter-site connectivity
3. **Overlay Layer 2**: BGP/EVPN VXLAN for VM networking (encapsulated through ZeroTier)
4. **Overlay Layer 3**: Wireguard point-to-point tunnels for specific use cases
5. **Anycast Layer**: BGP-advertised anycast IPs for load balancing and high availability

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## Prerequisites

### Required Software

- **Control Machine**:
  - Ansible >= 4.0.0
  - Python >= 3.7
  - Terraform (for VM provisioning)
  - Git

- **Target Servers**:
  - Debian 10 Buster (fresh installation)
  - SSH access as root
  - Internet connectivity

### Cloud Provider Accounts

- **OVH SoyouStart**: API credentials required for server management
- **Hetzner Cloud**: Account and API access for cloud deployments
- **ZeroTier**: Account and API token for overlay networking
- **Backblaze** (optional): S3-compatible storage for backups

### Network Requirements

- Public IP addresses for bare-metal servers
- Ability to configure BGP routing (provider-dependent)
- DNS domain for FreeIPA and services

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/bodleytunes/wizzcloud-ansible-lab.git
cd wizzcloud-ansible-lab
```

### 2. Install Dependencies

```bash
# Install Ansible and Python dependencies
pip install -r requirements.txt

# Install Ansible Galaxy roles
ansible-galaxy install -r requirements.yml

# Or use the Makefile
make install
```

### 3. Configure Vault Password

```bash
# Create vault password file
echo "your-vault-password" > /root/.vault_password
chmod 600 /root/.vault_password
```

### 4. Configure Inventory

Edit the inventory for your environment:

```bash
# For OVH SoyouStart
vi inventories/ovh_soyoustart/inventory.ini

# For Hetzner Cloud
vi inventories/hetzner_cloud/inventory.ini
```

### 5. Configure Variables

Update group variables with your environment-specific settings:

```bash
# Edit global variables
vi inventories/ovh_soyoustart/group_vars/all/global.yml

# Edit OVH API credentials (encrypted)
ansible-vault edit inventories/ovh_soyoustart/group_vars/ovh/vault.yml
```

### 6. Deploy Infrastructure

**Full Deployment (All Phases)**:

```bash
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml
```

**Phased Deployment (Recommended for first-time deployment)**:

```bash
# Phase 1: Base system and hypervisor setup
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags phase1

# Phase 2: Networking, storage, and applications
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags phase2
```

## Project Structure

```
wizzcloud-ansible-lab/
├── playbooks/              # Organized playbook modules
│   ├── day0/               # Initial deployment playbooks
│   ├── operational/        # Day-N operational tasks
│   └── run_once/           # One-time configuration playbooks
├── roles/                  # 43 Ansible roles
│   ├── proxmox/            # Proxmox hypervisor installation
│   ├── networking/         # Network configuration
│   ├── storage_*/          # Storage system roles
│   ├── k3s/                # Kubernetes deployment
│   ├── freeipa/            # Identity management
│   └── ...                 # See ROLES.md for complete list
├── inventories/            # Multi-environment inventories
│   ├── ovh_soyoustart/     # OVH SoyouStart environment
│   │   ├── inventory.ini   # Host definitions
│   │   ├── group_vars/     # Group-specific variables
│   │   └── host_vars/      # Host-specific variables
│   └── hetzner_cloud/      # Hetzner Cloud environment
├── plugins/modules/        # Custom Python Ansible modules
│   ├── zt_*.py             # ZeroTier management modules
│   ├── pve_*.py            # Proxmox API modules
│   ├── ovh_*.py            # OVH API modules
│   └── gluster_func.py     # GlusterFS operations
├── terraform/              # VM provisioning configurations
├── docker/                 # Docker utilities and configs
├── validation/             # Testing and validation files
├── docs/                   # Detailed documentation
│   ├── ARCHITECTURE.md     # Architecture documentation
│   ├── ROLES.md            # Role reference guide
│   ├── DEPLOYMENT.md       # Detailed deployment guide
│   └── OPERATIONS.md       # Day-N operations guide
├── ansible.cfg             # Ansible configuration
├── day0.yml                # Primary deployment playbook
├── day0_site_hetzcloud.yml # Hetzner-specific playbook
├── Makefile                # Build automation
└── pyproject.toml          # Python dependencies
```

See [ROLES.md](docs/ROLES.md) for complete role documentation.

## Deployment Guide

### Tag-Based Deployment

The project uses Ansible tags for granular control over deployment:

#### Core Infrastructure Tags

```bash
# Install required packages
ansible-playbook -i inventory.ini day0.yml --tags install_required_packages

# Setup Proxmox hypervisor
ansible-playbook -i inventory.ini day0.yml --tags proxmox

# Configure Proxmox clustering
ansible-playbook -i inventory.ini day0.yml --tags proxmox_clustering

# Setup users and SSH keys
ansible-playbook -i inventory.ini day0.yml --tags users,ssh_keys
```

#### Networking Tags

```bash
# Configure base networking
ansible-playbook -i inventory.ini day0.yml --tags networking

# Setup network interfaces
ansible-playbook -i inventory.ini day0.yml --tags networking_interfaces

# Configure FRR BGP routing
ansible-playbook -i inventory.ini day0.yml --tags networking_frr

# Setup ZeroTier overlay
ansible-playbook -i inventory.ini day0.yml --tags zerotier_networking

# Setup Nebula overlay
ansible-playbook -i inventory.ini day0.yml --tags networking_nebula

# Configure Wireguard
ansible-playbook -i inventory.ini day0.yml --tags wireguard
```

#### Storage Tags

```bash
# Configure ZFS
ansible-playbook -i inventory.ini day0.yml --tags storage_zfs

# Setup GlusterFS
ansible-playbook -i inventory.ini day0.yml --tags storage_glusterfs

# Configure LINSTOR
ansible-playbook -i inventory.ini day0.yml --tags storage_linstor
```

#### Kubernetes Tags

```bash
# Deploy K3s cluster
ansible-playbook -i inventory.ini day0.yml --tags k3s_deploy

# Configure Kubernetes VMs
ansible-playbook -i inventory.ini day0.yml --tags vm_configuration_kubernetes

# Deploy Rancher
ansible-playbook -i inventory.ini day0.yml --tags rancher

# Deploy K3s applications
ansible-playbook -i inventory.ini day0.yml --tags k3s_apps
```

#### Identity & Access Tags

```bash
# Setup FreeIPA server
ansible-playbook -i inventory.ini day0.yml --tags freeipa

# Enroll FreeIPA clients
ansible-playbook -i inventory.ini day0.yml --tags freeipa_client

# Configure Teleport
ansible-playbook -i inventory.ini day0.yml --tags gravitational_teleport
```

### Hetzner Cloud Deployment

For Hetzner Cloud-specific deployments:

```bash
# Full Hetzner deployment
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml

# Tagged deployment for specific components
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --tags zerotier_networking
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --tags k3s_deploy
```

### Host-Specific Deployment

Deploy to specific hosts using the `--limit` flag:

```bash
# Deploy to a single host
ansible-playbook -i inventory.ini day0.yml --limit rancher3

# Deploy to a group of hosts
ansible-playbook -i inventory.ini day0.yml --limit baremetal_hosts

# Combine with tags for specific operations
ansible-playbook -i inventory.ini day0.yml --tags networking --limit rancher1,rancher2
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment scenarios and best practices.

## Day-N Operations

### System Maintenance

```bash
# Dist-upgrade all hosts
ansible-playbook -i inventory.ini playbooks/operational/general_operations.yml --tags dist_upgrade

# Reboot hosts
ansible-playbook -i inventory.ini playbooks/operational/general_operations.yml --tags reboot_hosts
```

### Network Operations

```bash
# Reconfigure FRR routing
ansible-playbook -i inventory.ini day0.yml --tags reconfigure_frr_routing

# Regenerate Nebula certificates
ansible-playbook -i inventory.ini day0.yml --tags regen_certs

# Update firewall rules
ansible-playbook -i inventory.ini playbooks/operational/firewall_operations.yml
```

### Storage Operations

```bash
# Setup S3FS backup storage
ansible-playbook -i inventory.ini playbooks/operational/storage_operations.yml --tags setup_s3fs

# Expand GlusterFS volumes
ansible-playbook -i inventory.ini playbooks/operational/storage_operations.yml --tags expand_gluster
```

### Kubernetes Operations

```bash
# Upgrade K3s cluster
ansible-playbook -i inventory.ini playbooks/operational/upgrade_k3s.yml

# Add new K3s node
ansible-playbook -i inventory.ini day0.yml --tags vm_configuration_kubernetes --limit new_node
```

### VM Management

```bash
# Add new VM (Day-N workflow)
# 1. Add to inventory
# 2. Run dist-upgrade
ansible-playbook -i inventory.ini playbooks/operational/general_operations.yml --tags dist_upgrade --limit new_vm

# 3. Configure VM networking
ansible-playbook -i inventory.ini day0.yml --tags vm_networking --limit new_vm

# 4. Enroll in FreeIPA
ansible-playbook -i inventory.ini day0.yml --tags freeipa_client --limit new_vm

# 5. Configure Teleport client
ansible-playbook -i inventory.ini playbooks/operational/general_operations.yml --tags configure_teleport_clients --limit new_vm
```

### Teleport Configuration

```bash
# Configure Teleport auth server
ansible-playbook -i inventory.ini playbooks/run_once/configure_teleport_servers.yml --tags configure_teleport_auth_server

# Configure Teleport proxy server
ansible-playbook -i inventory.ini playbooks/run_once/configure_teleport_servers.yml --tags configure_teleport_proxy_server

# Configure Teleport clients
ansible-playbook -i inventory.ini playbooks/run_once/configure_teleport_servers.yml --tags configure_teleport_clients
```

### Terraform Operations

```bash
# Deploy VMs via Terraform
ansible-playbook -i inventory.ini day0.yml --tags terraform_deploy

# Destroy VMs via Terraform
ansible-playbook -i inventory.ini day0.yml --tags terraform_destroy
```

See [OPERATIONS.md](docs/OPERATIONS.md) for complete operational procedures.

## Configuration

### Ansible Configuration

The project uses optimized Ansible settings in `ansible.cfg`:

- **Fact Caching**: JSON file caching with 7200-second TTL for performance
- **Parallel Execution**: 50 forks for faster deployments
- **Custom Modules**: Plugin directory for custom Python modules
- **SSH Optimization**: Pipelining and ControlMaster for faster connections
- **Vault Integration**: Automatic vault password file usage

### Inventory Configuration

Inventories are organized by environment with clear separation:

```
inventories/
├── ovh_soyoustart/
│   ├── inventory.ini       # Host definitions
│   └── group_vars/         # Environment-specific variables
└── hetzner_cloud/
    ├── inventory.ini
    └── group_vars/
```

### Variable Hierarchy

Variables are organized in a clear hierarchy:

1. **Global Variables**: `group_vars/all/` - Apply to all hosts
2. **Group Variables**: `group_vars/<group_name>/` - Apply to specific groups
3. **Host Variables**: `host_vars/<hostname>/` - Host-specific overrides
4. **Vault Variables**: `vault.yml` files - Encrypted sensitive data

### Makefile Usage

The included Makefile provides convenient shortcuts:

```bash
# View inventory
make inventory-graph env=inventories/ovh_soyoustart/inventory.ini

# Run playbook with tags
make run playbook=day0 env=inventories/ovh_soyoustart/inventory.ini tag=networking

# Debug host variables
make debug host=rancher1 env=inventories/hetzner_cloud/inventory.ini

# Dry run
make dry-run playbook=day0 env=inventories/ovh_soyoustart/inventory.ini
```

## Documentation

Detailed documentation is available in the `docs/` directory:

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Complete architecture overview with diagrams
- **[ROLES.md](docs/ROLES.md)**: Detailed role reference and descriptions
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)**: Step-by-step deployment procedures
- **[OPERATIONS.md](docs/OPERATIONS.md)**: Day-N operational procedures
- **[NETWORKING.md](docs/NETWORKING.md)**: Network architecture and configuration
- **[STORAGE.md](docs/STORAGE.md)**: Storage systems configuration and management

## Troubleshooting

### Common Issues

**SSH Connection Failures**

```bash
# Verify SSH connectivity
ansible -i inventory.ini all -m ping

# Check SSH config
cat /root/.ssh/config

# Increase verbosity
ansible-playbook -i inventory.ini day0.yml -vvv
```

**Proxmox Clustering Issues**

```bash
# Verify cluster status on Proxmox nodes
pvecm status

# Check network connectivity between nodes
ansible -i inventory.ini proxmox_nodes -m shell -a "pvecm nodes"
```

**ZeroTier Network Issues**

```bash
# Verify ZeroTier status
ansible -i inventory.ini all -m shell -a "zerotier-cli status"

# Check network membership
ansible -i inventory.ini all -m shell -a "zerotier-cli listnetworks"
```

**FreeIPA Client Enrollment Failures**

```bash
# Manual enrollment
ansible -i inventory.ini ipa_clients -m shell -a "ipa-client-install --uninstall"
ansible-playbook -i inventory.ini day0.yml --tags freeipa_client
```

**K3s Deployment Issues**

```bash
# Check K3s status
ansible -i inventory.ini kubernetes_servers -m shell -a "systemctl status k3s"

# View K3s logs
ansible -i inventory.ini kubernetes_servers -m shell -a "journalctl -u k3s -n 100"
```

### Debug Mode

Run playbooks in debug mode for detailed output:

```bash
# Verbose mode
ansible-playbook -i inventory.ini day0.yml -v

# Very verbose (connection debugging)
ansible-playbook -i inventory.ini day0.yml -vv

# Maximum verbosity
ansible-playbook -i inventory.ini day0.yml -vvv
```

### Ansible Facts

Debug host facts and variables:

```bash
# Gather and save facts
ansible -i inventory.ini all -m setup --tree out/

# View specific host facts
ansible -i inventory.ini rancher1 -m setup

# Debug hostvars
ansible -i inventory.ini rancher1 -m debug -a "var=hostvars[inventory_hostname]"
```

## Performance Optimization

The project includes several performance optimizations:

- **Fact Caching**: Reduces repeated fact gathering (7200s TTL)
- **SSH Pipelining**: Reduces SSH overhead
- **ControlMaster**: Reuses SSH connections
- **Parallel Execution**: 50 forks for concurrent host operations
- **Strategy Free**: Optional parallel execution strategy
- **Conditional Tasks**: Skip unnecessary tasks based on host state

## Security Considerations

- **Vault Encryption**: All sensitive data stored in Ansible Vault
- **SSH Key Authentication**: Password authentication disabled
- **Encrypted Overlays**: All inter-node traffic encrypted (Nebula/ZeroTier/Wireguard)
- **Firewall Rules**: UFW configured on all hosts
- **Certificate-Based Auth**: Teleport replaces traditional SSH
- **SSSD Integration**: Centralized authentication via FreeIPA

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Update documentation as needed
5. Submit a pull request

## License

This project is licensed under the terms specified in the repository.

## Support

For issues and questions:

- Open an issue on GitHub
- Review existing documentation in `docs/`
- Check Ansible logs: `/var/log/ansible.log`

## Acknowledgments

- **External Roles**:
  - [ansible-role-wireguard](https://github.com/githubixx/ansible-role-wireguard) by githubixx
  - [ansible-role-dhcp](https://github.com/bertvv/ansible-role-dhcp) by bertvv
- **Ansible Proxmox API**: Based on [ansible-proxmox-api](https://github.com/robinelfrink/ansible-proxmox-api)
- **Ansible Makefile**: Based on ANSIBLE-MAKEFILE v0.16.0 by Paul(r)B.r

## Project Statistics

- **Total Roles**: 43 specialized roles
- **Custom Modules**: 16 Python modules (1,750+ lines)
- **Playbooks**: 10+ playbooks for various operations
- **Supported Clouds**: 2 cloud providers (OVH, Hetzner)
- **Technologies Integrated**: 20+ infrastructure technologies

---

**Built with Ansible** | **Automating Cloud Infrastructure**
