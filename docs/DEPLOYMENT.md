# Deployment Guide

This comprehensive guide walks you through deploying the WizzCloud Ansible Lab infrastructure from bare-metal servers to a fully operational private cloud.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Initial Setup](#initial-setup)
- [Full Deployment (Automated)](#full-deployment-automated)
- [Phased Deployment (Recommended)](#phased-deployment-recommended)
- [Component-Specific Deployment](#component-specific-deployment)
- [Hetzner Cloud Deployment](#hetzner-cloud-deployment)
- [Post-Deployment Verification](#post-deployment-verification)
- [Troubleshooting Deployment](#troubleshooting-deployment)

---

## Prerequisites

### Hardware Requirements

**Minimum Configuration (OVH SoyouStart)**:
- **Bare-metal servers**: 2+ (for HA)
- **CPU**: 4+ cores per server
- **RAM**: 16GB+ per server
- **Storage**: 500GB+ per server
- **Network**: Public IP per server, 1Gbps+ connectivity

**Hetzner Cloud Configuration**:
- **Cloud instances**: 3+ (rancher1, rancher2, rancher3)
- **Instance type**: CX31+ or equivalent
- **Network**: Public IPs, private networking

### Software Requirements

**Control Machine** (where Ansible runs):
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Ansible**: 4.0.0 or higher
- **Python**: 3.7 or higher
- **Terraform**: 1.0+ (for VM provisioning)
- **Git**: For cloning repository
- **SSH Client**: OpenSSH

**Target Servers**:
- **OS**: Debian 10 Buster (fresh installation)
- **Root access**: SSH access as root user
- **Python 3**: Pre-installed (usually available on Debian 10)

### Cloud Provider Accounts

1. **OVH SoyouStart** (if deploying on OVH):
   - Active account with dedicated servers
   - API credentials (Application Key, Application Secret, Consumer Key)
   - Server access via OVH manager

2. **Hetzner Cloud** (if deploying on Hetzner):
   - Active Hetzner Cloud account
   - Cloud instances created
   - SSH access configured

3. **ZeroTier**:
   - Account at https://my.zerotier.com
   - Network created
   - API access token

4. **Backblaze** (optional, for backups):
   - B2 Cloud Storage account
   - Application key and key ID

### Network Requirements

- **Public IPs**: One per bare-metal server
- **DNS Domain**: For FreeIPA and services (e.g., wizznet.co.uk)
- **BGP Support**: If using BGP routing features (check with provider)
- **Firewall Access**: Ability to configure firewall rules

---

## Pre-Deployment Checklist

Before starting deployment, complete these steps:

### 1. Prepare Control Machine

```bash
# Install Ansible
pip3 install ansible

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify installations
ansible --version
terraform --version
```

### 2. Clone Repository

```bash
git clone https://github.com/bodleytunes/wizzcloud-ansible-lab.git
cd wizzcloud-ansible-lab
```

### 3. Install Ansible Dependencies

```bash
# Install required Ansible collections and roles
ansible-galaxy install -r requirements.yml

# Or use Makefile
make install
```

### 4. Configure Vault Password

```bash
# Create vault password file
echo "your-secure-vault-password" > /root/.vault_password
chmod 600 /root/.vault_password
```

### 5. Prepare Target Servers

**On each bare-metal server**:

```bash
# Ensure Debian 10 Buster is installed
cat /etc/debian_version  # Should show 10.x

# Ensure SSH is accessible
systemctl status sshd

# Ensure Python 3 is installed
python3 --version
```

### 6. Configure SSH Access

**On control machine**:

```bash
# Generate SSH key if needed
ssh-keygen -t ed25519 -C "ansible-automation"

# Copy SSH key to all target servers
ssh-copy-id root@server1-ip
ssh-copy-id root@server2-ip
# ... repeat for all servers

# Verify SSH access
ssh root@server1-ip "hostname"
```

**Configure ~/.ssh/config** (or /root/.ssh/config):

```
Host p21
    HostName <public-ip-of-p21>
    User root
    IdentityFile ~/.ssh/id_ed25519

Host p22
    HostName <public-ip-of-p22>
    User root
    IdentityFile ~/.ssh/id_ed25519

# Add entries for all servers
```

### 7. Configure Inventory

**Edit inventory file**:

```bash
# For OVH deployment
vi inventories/ovh_soyoustart/inventory.ini

# For Hetzner deployment
vi inventories/hetzner_cloud/inventory.ini
```

**Example inventory.ini**:

```ini
[baremetal_hosts]
p21 ansible_host=xxx.xxx.xxx.xxx
p22 ansible_host=xxx.xxx.xxx.xxx

[proxmox_nodes:children]
baremetal_hosts

[proxmox_master]
p21

[ipa_master]
p21

[ipa_replica]
p22
```

### 8. Configure Group Variables

**Edit global variables**:

```bash
vi inventories/ovh_soyoustart/group_vars/all/global.yml
```

**Key variables to set**:

```yaml
# Domain configuration
domain_name: "wizznet.co.uk"
ipa_realm: "WIZZNET.CO.UK"

# Network configuration
management_network: "10.0.0.0/24"
overlay_network: "10.100.0.0/24"

# ZeroTier
zerotier_network_id: "your-network-id"
```

**Configure encrypted secrets**:

```bash
# Edit OVH API credentials
ansible-vault edit inventories/ovh_soyoustart/group_vars/ovh/vault.yml

# Add:
ovh_application_key: "your-app-key"
ovh_application_secret: "your-app-secret"
ovh_consumer_key: "your-consumer-key"

# Edit ZeroTier secrets
ansible-vault edit inventories/ovh_soyoustart/group_vars/all/vault.yml

# Add:
zerotier_api_token: "your-zerotier-token"
```

### 9. Verify Inventory

```bash
# View inventory structure
ansible-inventory -i inventories/ovh_soyoustart/inventory.ini --graph

# Test connectivity
ansible -i inventories/ovh_soyoustart/inventory.ini all -m ping
```

---

## Initial Setup

### Test Ansible Connectivity

```bash
# Ping all hosts
ansible -i inventories/ovh_soyoustart/inventory.ini all -m ping

# Expected output:
# p21 | SUCCESS => {
#     "changed": false,
#     "ping": "pong"
# }
```

### Gather Initial Facts

```bash
# Gather facts from all hosts
ansible -i inventories/ovh_soyoustart/inventory.ini all -m setup | less

# Check Debian version
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "cat /etc/debian_version"
```

---

## Full Deployment (Automated)

For a complete automated deployment (not recommended for first-time):

```bash
# Full deployment - all phases
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml

# With verbose output
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml -v

# Dry run (check mode)
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --check
```

**Duration**: Approximately 2-4 hours depending on:
- Number of hosts
- Network speed
- Package download speeds
- VM count

---

## Phased Deployment (Recommended)

For better control and easier troubleshooting, deploy in phases:

### Phase 1: Base System and Hypervisor Setup

**Purpose**: Prepare bare-metal servers with Proxmox hypervisor

```bash
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags phase1
```

**Phase 1 includes**:
1. Pre-deployment checks (`day0_pre`)
2. User creation (`users`)
3. SSH key distribution (`ssh_keys`)
4. Package installation (`install_required_packages`)
5. Proxmox installation (`proxmox`)
6. Proxmox clustering (`proxmox_clustering`)

**Verification after Phase 1**:

```bash
# Check Proxmox status
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_nodes -m shell -a "pveversion"

# Check cluster status
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_nodes -m shell -a "pvecm status"

# Expected: All nodes in cluster, quorum active
```

### Phase 2: Networking, Storage, and Applications

**Purpose**: Configure networking, storage, and deploy applications

```bash
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags phase2
```

**Phase 2 includes**:
1. Network configuration (`networking`, `networking_interfaces`, `networking_frr`)
2. Overlay networks (`zerotier_networking`, `networking_nebula`, `wireguard`)
3. Storage setup (`storage_zfs`, `storage_glusterfs`, `storage_linstor`)
4. Firewall rules (`firewall`)
5. VM deployment (`terraform`)
6. Kubernetes deployment (`k3s`, `vm_configuration_kubernetes`, `rancher`)
7. Identity management (`freeipa`, `freeipa_client`)
8. Access management (`gravitational_teleport`)

**Verification after Phase 2**:

```bash
# Check ZeroTier status
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "zerotier-cli status"

# Check GlusterFS volumes
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "gluster volume status"

# Check K3s status
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_servers -m shell -a "kubectl get nodes"
```

---

## Component-Specific Deployment

For granular control, deploy individual components:

### 1. Base System Preparation

```bash
# Pre-deployment tasks
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags day0_pre

# Create users
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags users

# Distribute SSH keys
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags ssh_keys

# Install required packages
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags install_required_packages
```

### 2. Proxmox Hypervisor

```bash
# Install Proxmox
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags proxmox

# Configure Proxmox clustering
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags proxmox_clustering

# Verify
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_nodes -m shell -a "pvecm status"
```

### 3. Networking

```bash
# Base networking
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags networking

# Network interfaces
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags networking_interfaces

# FRR BGP routing
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags networking_frr

# ZeroTier overlay
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags zerotier_networking

# Nebula overlay
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags networking_nebula

# Wireguard VPN
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags wireguard

# Firewall rules
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags firewall

# Verify networking
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "ip a"
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "ip route"
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "vtysh -c 'show ip bgp summary'"
```

### 4. Storage

```bash
# ZFS configuration
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags storage_zfs

# GlusterFS distributed storage
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags storage_glusterfs

# LINSTOR replicated storage
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags storage_linstor

# Storage orchestration
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags storage

# Verify storage
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "zpool list"
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "gluster volume status"
```

### 5. Virtual Machines

```bash
# Deploy VMs via Terraform
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags terraform_deploy

# Configure VM networking
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags vm_networking

# Wait for VMs to boot (2-3 minutes)

# Verify VMs
ansible -i inventories/ovh_soyoustart/inventory.ini virtual_machines -m ping
```

### 6. Identity Management

```bash
# Deploy FreeIPA server
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags freeipa

# Enroll FreeIPA clients
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags freeipa_client

# Verify FreeIPA
ansible -i inventories/ovh_soyoustart/inventory.ini ipa_master -m shell -a "ipactl status"
ansible -i inventories/ovh_soyoustart/inventory.ini ipa_clients -m shell -a "ipa env"
```

### 7. Kubernetes

```bash
# Deploy K3s
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags k3s_deploy

# Configure Kubernetes VMs
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags vm_configuration_kubernetes

# Deploy Rancher
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags rancher

# Deploy K3s applications
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags k3s_apps

# Verify Kubernetes
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_servers -m shell -a "kubectl get nodes"
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_servers -m shell -a "kubectl get pods --all-namespaces"
```

### 8. Access Management

```bash
# Deploy Teleport
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags gravitational_teleport

# Configure Teleport auth server
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/run_once/configure_teleport_servers.yml --tags configure_teleport_auth_server

# Configure Teleport proxy server
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/run_once/configure_teleport_servers.yml --tags configure_teleport_proxy_server

# Configure Teleport clients
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/run_once/configure_teleport_servers.yml --tags configure_teleport_clients
```

---

## Hetzner Cloud Deployment

For Hetzner Cloud-specific deployments (rancher1, rancher2, rancher3):

### Full Hetzner Deployment

```bash
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml
```

### Step-by-Step Hetzner Deployment

```bash
# 1. Install required packages
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --tags install_required_packages

# 2. Configure FRR routing
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --tags networking_frr

# 3. Create users
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --tags users

# 4. Setup ZeroTier
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --tags zerotier_networking

# 5. Configure Kubernetes VMs
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --tags vm_configuration_kubernetes

# 6. Setup networking
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --tags networking
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --tags networking_interfaces

# 7. Deploy K3s
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --tags k3s_deploy

# 8. Post-K3s configuration
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --tags post_k3s

# 9. Deploy Rancher
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --tags rancher
```

### Single Host Deployment (Hetzner)

Deploy to a specific host:

```bash
# Deploy to rancher3 only
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --limit rancher3 --tags install_required_packages
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --limit rancher3 --tags networking_frr
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --limit rancher3 --tags users
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --limit rancher3 --tags zerotier_networking
ansible-playbook -i inventories/hetzner_cloud/inventory.ini day0_site_hetzcloud.yml --limit rancher3 --tags k3s_deploy
```

---

## Post-Deployment Verification

After deployment, verify all components are operational:

### 1. System Health

```bash
# Check all hosts are reachable
ansible -i inventories/ovh_soyoustart/inventory.ini all -m ping

# Check system uptime
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "uptime"

# Check disk space
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "df -h"
```

### 2. Proxmox Cluster

```bash
# Cluster status
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_nodes -m shell -a "pvecm status"

# Proxmox version
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_nodes -m shell -a "pveversion"

# List VMs
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_master -m shell -a "qm list"
```

### 3. Networking

```bash
# ZeroTier status
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "zerotier-cli status"
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "zerotier-cli listnetworks"

# Nebula status
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "systemctl status nebula"

# BGP status
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "vtysh -c 'show ip bgp summary'"

# Network interfaces
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "ip -br a"
```

### 4. Storage

```bash
# ZFS pools
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "zpool status"

# GlusterFS volumes
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "gluster volume status"

# GlusterFS peers
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "gluster peer status"
```

### 5. FreeIPA

```bash
# IPA server status
ansible -i inventories/ovh_soyoustart/inventory.ini ipa_master -m shell -a "ipactl status"

# IPA topology
ansible -i inventories/ovh_soyoustart/inventory.ini ipa_master -m shell -a "ipa topologysuffix-list"

# Client enrollment
ansible -i inventories/ovh_soyoustart/inventory.ini ipa_clients -m shell -a "ipa env | grep server"
```

### 6. Kubernetes

```bash
# Node status
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_servers -m shell -a "kubectl get nodes"

# Pod status
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_servers -m shell -a "kubectl get pods --all-namespaces"

# Rancher status
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_master -m shell -a "kubectl get pods -n cattle-system"

# Get Rancher URL
echo "Access Rancher at: https://<rancher-hostname>"
```

### 7. Teleport

```bash
# Teleport status
ansible -i inventories/ovh_soyoustart/inventory.ini teleport_auth_servers -m shell -a "systemctl status teleport"

# Teleport nodes
ansible -i inventories/ovh_soyoustart/inventory.ini teleport_auth_servers -m shell -a "tctl nodes ls"
```

---

## Troubleshooting Deployment

### Common Issues and Solutions

#### Issue: Ansible Cannot Connect to Hosts

**Symptoms**:
```
fatal: [p21]: UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh"}
```

**Solutions**:

```bash
# Verify SSH access manually
ssh root@<host-ip>

# Check SSH config
cat ~/.ssh/config

# Test with verbose SSH
ssh -vvv root@<host-ip>

# Verify inventory
ansible-inventory -i inventories/ovh_soyoustart/inventory.ini --list

# Test with Ansible ping
ansible -i inventories/ovh_soyoustart/inventory.ini all -m ping -vvv
```

#### Issue: Proxmox Clustering Fails

**Symptoms**:
```
TASK [proxmox_clustering : Join nodes to cluster] **************************
fatal: [p22]: FAILED! => {"msg": "Cluster join failed"}
```

**Solutions**:

```bash
# Check network connectivity between nodes
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_nodes -m shell -a "ping -c 3 <master-ip>"

# Check Proxmox cluster status on master
ssh root@p21 "pvecm status"

# Remove failed node and retry
ssh root@p22 "pvecm delnode p22"
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags proxmox_clustering --limit p22
```

#### Issue: ZeroTier Network Not Joining

**Symptoms**:
- ZeroTier service running but not connected to network
- No IP assigned on ZeroTier interface

**Solutions**:

```bash
# Check ZeroTier status
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "zerotier-cli status"

# Check network membership
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "zerotier-cli listnetworks"

# Manually authorize nodes in ZeroTier Central
# Visit https://my.zerotier.com and authorize nodes

# Retry ZeroTier configuration
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags zerotier_networking
```

#### Issue: GlusterFS Volume Creation Fails

**Symptoms**:
```
TASK [storage_glusterfs : Create Gluster volume] ***************************
fatal: [p21]: FAILED! => {"msg": "volume create failed"}
```

**Solutions**:

```bash
# Check GlusterFS peers
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "gluster peer status"

# Probe peers manually if needed
ssh root@p21 "gluster peer probe p22"

# Check brick directories exist
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "ls -la /gluster/brick1"

# Retry GlusterFS setup
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags storage_glusterfs
```

#### Issue: K3s Installation Fails

**Symptoms**:
- K3s installation script fails
- K3s service not starting

**Solutions**:

```bash
# Check K3s service status
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_servers -m shell -a "systemctl status k3s"

# Check K3s logs
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_servers -m shell -a "journalctl -u k3s -n 50"

# Manually install K3s on master
ssh root@kube1
curl -sfL https://get.k3s.io | sh -s - --disable traefik --disable servicelb

# Retry K3s deployment
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags k3s_deploy
```

#### Issue: FreeIPA Enrollment Fails

**Symptoms**:
```
TASK [freeipa_client : Enroll client] **************************************
fatal: [vm1]: FAILED! => {"msg": "IPA client enrollment failed"}
```

**Solutions**:

```bash
# Check IPA server is accessible
ansible -i inventories/ovh_soyoustart/inventory.ini ipa_clients -m shell -a "ping -c 3 <ipa-master-ip>"

# Check DNS resolution
ansible -i inventories/ovh_soyoustart/inventory.ini ipa_clients -m shell -a "nslookup <ipa-master-hostname>"

# Manually unenroll and re-enroll
ssh root@vm1
ipa-client-install --uninstall
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags freeipa_client --limit vm1
```

### Getting Detailed Logs

```bash
# Run with maximum verbosity
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags <tag> -vvvv

# Check Ansible log file
tail -f /var/log/ansible.log

# Debug specific task
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags <tag> --step
```

### Recovery from Failed Deployment

If deployment fails partway through:

```bash
# Identify where it failed (check output)

# Re-run from failed tag
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags <failed-tag>

# Or re-run entire phase
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags phase1  # or phase2

# For idempotent roles, safe to re-run entire playbook
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml
```

---

## Best Practices

1. **Always Use Dry Run First**:
   ```bash
   ansible-playbook -i inventory.ini day0.yml --check
   ```

2. **Deploy in Phases**: Start with Phase 1, verify, then Phase 2

3. **Limit Scope**: Test on single host before deploying to all:
   ```bash
   ansible-playbook -i inventory.ini day0.yml --limit p21 --tags networking
   ```

4. **Use Tags**: Deploy individual components for easier troubleshooting

5. **Backup Before Changes**: Take snapshots of VMs before major changes

6. **Monitor During Deployment**: Watch logs and system resources

7. **Document Customizations**: Keep notes on any manual changes or customizations

8. **Version Control**: Commit inventory and group_vars changes to git

---

This deployment guide provides comprehensive instructions for deploying the WizzCloud Ansible Lab infrastructure. Follow the phased approach for the most reliable deployment experience.
