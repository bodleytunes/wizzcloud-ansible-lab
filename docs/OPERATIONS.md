# Day-N Operations Guide

This guide covers operational procedures for maintaining and managing the WizzCloud Ansible Lab infrastructure after initial deployment.

## Table of Contents

- [System Maintenance](#system-maintenance)
- [Network Operations](#network-operations)
- [Storage Operations](#storage-operations)
- [Virtual Machine Management](#virtual-machine-management)
- [Kubernetes Operations](#kubernetes-operations)
- [Identity Management Operations](#identity-management-operations)
- [Backup and Recovery](#backup-and-recovery)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Operations](#security-operations)
- [Troubleshooting](#troubleshooting)

---

## System Maintenance

### System Updates

#### Dist-Upgrade All Hosts

Update all packages on bare-metal hosts and VMs:

```bash
# Upgrade all systems
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/operational/general_operations.yml --tags dist_upgrade

# Upgrade specific host group
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/operational/general_operations.yml --tags dist_upgrade --limit baremetal_hosts

# Upgrade single host
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/operational/general_operations.yml --tags dist_upgrade --limit p21
```

**What it does**:
- Runs `apt update && apt dist-upgrade -y`
- Updates all packages to latest versions
- May require reboot for kernel updates

#### Kernel Updates

After kernel updates, reboot is required:

```bash
# Check if reboot is required
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "[ -f /var/run/reboot-required ] && echo 'Reboot required' || echo 'No reboot needed'"

# Reboot hosts (one at a time)
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/operational/general_operations.yml --tags reboot_hosts --limit p21

# Wait for host to come back up, then reboot next
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/operational/general_operations.yml --tags reboot_hosts --limit p22
```

**Best Practice**: Reboot bare-metal hosts one at a time to maintain cluster quorum.

### Package Management

#### Install New Packages

```bash
# Add package to group_vars/baremetal_hosts/packages.yml
# Then run:
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags install_required_packages

# Or install ad-hoc
ansible -i inventories/ovh_soyoustart/inventory.ini all -m apt -a "name=htop state=present"
```

#### Remove Packages

```bash
# Remove package
ansible -i inventories/ovh_soyoustart/inventory.ini all -m apt -a "name=package_name state=absent"

# Remove with dependencies
ansible -i inventories/ovh_soyoustart/inventory.ini all -m apt -a "name=package_name state=absent autoremove=yes"
```

### Service Management

#### Check Service Status

```bash
# Check specific service
ansible -i inventories/ovh_soyoustart/inventory.ini all -m systemd -a "name=sshd state=started enabled=yes"

# Check multiple services
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "systemctl status sshd proxmox zerotier-one"
```

#### Restart Services

```bash
# Restart service across all hosts
ansible -i inventories/ovh_soyoustart/inventory.ini all -m systemd -a "name=frr state=restarted"

# Restart FRR routing daemon
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m systemd -a "name=frr state=restarted"
```

---

## Network Operations

### Reconfigure FRR Routing

If you modify FRR BGP configuration templates or variables:

```bash
# Reconfigure FRR on all nodes
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags reconfigure_frr_routing

# Reconfigure on specific node
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags reconfigure_frr_routing --limit p21
```

**What it does**:
- Regenerates FRR configuration from templates
- Reloads FRR daemon
- Applies new BGP settings

### Check BGP Status

```bash
# BGP summary
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "vtysh -c 'show ip bgp summary'"

# BGP neighbors
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "vtysh -c 'show ip bgp neighbors'"

# Advertised routes
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "vtysh -c 'show ip bgp'"

# EVPN routes
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "vtysh -c 'show bgp l2vpn evpn'"
```

### Regenerate Nebula Certificates

If you modify Nebula groups or node assignments:

```bash
# Regenerate certificates for all nodes
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags regen_certs

# Regenerate for specific node
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags regen_certs --limit p21
```

**What it does**:
- Generates new Nebula certificates with updated groups
- Distributes certificates to nodes
- Restarts Nebula service

### ZeroTier Network Management

```bash
# Check ZeroTier status
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "zerotier-cli status"

# List networks
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "zerotier-cli listnetworks"

# Get node IDs (for authorization in ZeroTier Central)
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "zerotier-cli info"

# Rejoin network
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags zerotier_networking
```

### Firewall Rule Updates

```bash
# Update firewall rules
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/operational/firewall_operations.yml

# Or reconfigure from day0
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags firewall

# Check UFW status
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "ufw status verbose"

# Add rule ad-hoc
ansible -i inventories/ovh_soyoustart/inventory.ini all -m ufw -a "rule=allow port=8080 proto=tcp"
```

### Network Interface Changes

```bash
# Reconfigure interfaces
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags networking_interfaces

# Restart networking (be careful with remote connections!)
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "systemctl restart networking"

# Check interface status
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "ip -br a"
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "ip route"
```

---

## Storage Operations

### GlusterFS Operations

#### Check Volume Status

```bash
# Volume status
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "gluster volume status"

# Volume info
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "gluster volume info"

# Peer status
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "gluster peer status"
```

#### Expand GlusterFS Volume

```bash
# Add brick to volume
ssh root@p21
gluster volume add-brick <volume_name> replica 3 p23:/gluster/brick1/<volume_name>
gluster volume rebalance <volume_name> start

# Monitor rebalance
gluster volume rebalance <volume_name> status
```

#### Heal GlusterFS Volume

```bash
# Check for split-brain or heal status
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "gluster volume heal <volume_name> info"

# Trigger heal
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "gluster volume heal <volume_name>"

# Monitor heal
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "gluster volume heal <volume_name> info"
```

### ZFS Operations

#### Check ZFS Status

```bash
# Pool status
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "zpool status"

# Pool list
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "zpool list"

# Dataset list
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "zfs list"
```

#### Create ZFS Snapshot

```bash
# Create snapshot
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "zfs snapshot rpool/data@backup-$(date +%Y%m%d)"

# List snapshots
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "zfs list -t snapshot"

# Rollback to snapshot
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "zfs rollback rpool/data@backup-20231015"
```

#### Scrub ZFS Pool

```bash
# Start scrub
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "zpool scrub rpool"

# Check scrub status
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "zpool status rpool"
```

### S3FS Backup Storage

```bash
# Setup or refresh S3FS mounts
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/operational/storage_operations.yml --tags setup_s3fs

# Check S3FS mounts
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "df -h | grep s3fs"

# Remount S3FS
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "umount /mnt/backups && mount /mnt/backups"
```

---

## Virtual Machine Management

### Add New VM (Day-N Workflow)

**1. Define VM in Terraform configuration**:

Edit `terraform/vms.tf` or appropriate terraform config:

```hcl
resource "proxmox_vm_qemu" "new_vm" {
  name        = "newvm.wizznet.co.uk"
  target_node = "p21"
  clone       = "debian-10-template"
  cores       = 2
  memory      = 4096
  # ... additional configuration
}
```

**2. Add VM to inventory**:

Edit `inventories/ovh_soyoustart/inventory.ini`:

```ini
[virtual_machines]
# ... existing VMs
newvm.wizznet.co.uk ansible_host=10.0.0.50 ansible_user=root

[ipa_clients]
# ... existing clients
newvm.wizznet.co.uk
```

**3. Deploy VM via Terraform**:

```bash
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags terraform_deploy
```

**4. Wait for VM to boot** (2-3 minutes)

**5. Configure VM**:

```bash
# Dist-upgrade
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/operational/general_operations.yml --tags dist_upgrade --limit newvm.wizznet.co.uk

# Configure networking
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags vm_networking --limit newvm.wizznet.co.uk

# Enroll in FreeIPA
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags freeipa_client --limit newvm.wizznet.co.uk

# Configure Teleport client
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/run_once/configure_teleport_servers.yml --tags configure_teleport_clients --limit newvm.wizznet.co.uk

# Run post-operations
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini post_operations_vm.yml --limit newvm.wizznet.co.uk
```

### Remove VM

**1. Destroy VM via Terraform**:

Comment out or remove VM from terraform config, then:

```bash
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags terraform_destroy
```

**2. Remove from inventory**

**3. Clean up FreeIPA**:

```bash
# Remove host from IPA
ssh root@<ipa-master>
ipa host-del newvm.wizznet.co.uk
```

### VM Snapshots

```bash
# Create snapshot via Proxmox
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_master -m shell -a "qm snapshot <vmid> <snapshot_name>"

# List snapshots
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_master -m shell -a "qm listsnapshot <vmid>"

# Rollback to snapshot
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_master -m shell -a "qm rollback <vmid> <snapshot_name>"

# Delete snapshot
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_master -m shell -a "qm delsnapshot <vmid> <snapshot_name>"
```

### VM Resource Adjustments

```bash
# Increase CPU
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_master -m shell -a "qm set <vmid> --cores 4"

# Increase RAM
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_master -m shell -a "qm set <vmid> --memory 8192"

# Resize disk
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_master -m shell -a "qm resize <vmid> scsi0 +10G"
```

---

## Kubernetes Operations

### Upgrade K3s Cluster

```bash
# Upgrade K3s to specific version
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/operational/upgrade_k3s.yml

# Or via standard playbook with version variable override
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags k3s_deploy -e "k3s_version=v1.28.2+k3s1"
```

### Add K3s Node

**1. Create VM** (see VM Management section)

**2. Add to inventory under `[kubernetes_servers]`**

**3. Deploy K3s agent**:

```bash
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags k3s_deploy --limit new_k3s_node
```

**4. Verify node joined**:

```bash
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_master -m shell -a "kubectl get nodes"
```

### Remove K3s Node

**1. Drain node**:

```bash
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_master -m shell -a "kubectl drain <node_name> --ignore-daemonsets --delete-emptydir-data"
```

**2. Delete node**:

```bash
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_master -m shell -a "kubectl delete node <node_name>"
```

**3. Uninstall K3s on node**:

```bash
ansible -i inventories/ovh_soyoustart/inventory.ini <node> -m shell -a "/usr/local/bin/k3s-uninstall.sh"
```

### Deploy Applications to K3s

```bash
# Deploy K3s applications
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags k3s_apps

# Check deployments
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_master -m shell -a "kubectl get deployments --all-namespaces"

# Check pods
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_master -m shell -a "kubectl get pods --all-namespaces"
```

### Kubernetes Troubleshooting

```bash
# Check cluster status
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_master -m shell -a "kubectl cluster-info"

# Check node status
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_master -m shell -a "kubectl get nodes -o wide"

# Check pod logs
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_master -m shell -a "kubectl logs -n <namespace> <pod_name>"

# Describe pod
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_master -m shell -a "kubectl describe pod -n <namespace> <pod_name>"

# Check events
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_master -m shell -a "kubectl get events --all-namespaces --sort-by='.lastTimestamp'"
```

---

## Identity Management Operations

### FreeIPA User Management

#### Add User

```bash
# Via Ansible
# Add user to group_vars and run:
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags freeipa_users

# Via IPA CLI
ssh root@<ipa-master>
ipa user-add username --first=First --last=Last --email=user@example.com --password
```

#### Remove User

```bash
ssh root@<ipa-master>
ipa user-del username
```

#### Reset User Password

```bash
ssh root@<ipa-master>
ipa user-mod username --password
```

### FreeIPA Host Management

#### Enroll New Host

```bash
# Add host to ipa_clients group in inventory
# Then run:
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags freeipa_client --limit new_host
```

#### Remove Host

```bash
ssh root@<ipa-master>
ipa host-del hostname.domain.com
```

### FreeIPA Service Status

```bash
# Check IPA services
ansible -i inventories/ovh_soyoustart/inventory.ini ipa_master -m shell -a "ipactl status"

# Restart IPA services
ansible -i inventories/ovh_soyoustart/inventory.ini ipa_master -m shell -a "ipactl restart"

# Check replication
ssh root@<ipa-master>
ipa-replica-manage list
ipa-replica-manage list-ruv
```

### Teleport Operations

#### Configure Teleport Components

```bash
# Configure auth server
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/run_once/configure_teleport_servers.yml --tags configure_teleport_auth_server

# Configure proxy server
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/run_once/configure_teleport_servers.yml --tags configure_teleport_proxy_server

# Configure clients
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini playbooks/run_once/configure_teleport_servers.yml --tags configure_teleport_clients
```

#### Manage Teleport Users

```bash
# List users
ssh root@<teleport-auth-server>
tctl users ls

# Add user
tctl users add <username> --roles=access

# Remove user
tctl users rm <username>
```

#### Check Teleport Nodes

```bash
# List nodes
ssh root@<teleport-auth-server>
tctl nodes ls

# Check node status
ansible -i inventories/ovh_soyoustart/inventory.ini teleport_clients -m systemd -a "name=teleport state=started"
```

---

## Backup and Recovery

### Backup Strategies

#### VM Backups (Proxmox)

```bash
# Create VM backup
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_master -m shell -a "vzdump <vmid> --storage local --mode snapshot --compress gzip"

# List backups
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_master -m shell -a "ls -lh /var/lib/vz/dump/"

# Restore VM from backup
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_master -m shell -a "qmrestore /var/lib/vz/dump/vzdump-qemu-<vmid>-<date>.vma.gz <new_vmid>"
```

#### GlusterFS Backups

```bash
# GlusterFS snapshots
ssh root@p21
gluster snapshot create <snap_name> <volume_name>

# List snapshots
gluster snapshot list

# Restore from snapshot
gluster snapshot restore <snap_name>
```

#### Configuration Backups

```bash
# Backup Ansible configurations
cd /path/to/wizzcloud-ansible-lab
tar -czf ~/ansible-backup-$(date +%Y%m%d).tar.gz \
  inventories/ \
  group_vars/ \
  host_vars/ \
  roles/ \
  playbooks/

# Backup to S3FS
cp ~/ansible-backup-*.tar.gz /mnt/backups/ansible/
```

#### FreeIPA Backups

```bash
# Full IPA backup
ssh root@<ipa-master>
ipa-backup

# Backups stored in /var/lib/ipa/backup/
ls -lh /var/lib/ipa/backup/
```

### Recovery Procedures

#### Restore FreeIPA

```bash
ssh root@<ipa-master>
ipa-restore /var/lib/ipa/backup/<backup_dir>
```

#### Restore VM

```bash
# Via Proxmox
qmrestore /path/to/backup.vma.gz <vmid>

# Start VM
qm start <vmid>
```

---

## Monitoring and Logging

### Log Locations

- **Ansible Logs**: `/var/log/ansible.log`
- **System Logs**: `journalctl -u <service>`
- **Proxmox Logs**: `/var/log/pve/`
- **K3s Logs**: `journalctl -u k3s`
- **FreeIPA Logs**: `/var/log/ipa*`

### Check Logs

```bash
# Ansible log
tail -f /var/log/ansible.log

# Service logs
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "journalctl -u <service> -n 100"

# System log
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "tail -100 /var/log/syslog"
```

### System Health Checks

```bash
# CPU and Memory
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "top -bn1 | head -20"

# Disk usage
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "df -h"

# Network connections
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "ss -tuln"

# Process list
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "ps aux | head -20"
```

---

## Security Operations

### SSL Certificate Management

```bash
# Cert-Manager status (K8s)
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_master -m shell -a "kubectl get certificates --all-namespaces"

# Check certificate expiry
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "openssl x509 -in /path/to/cert.pem -noout -dates"
```

### SSH Key Rotation

**1. Update SSH keys in group_vars**:

Edit `inventories/ovh_soyoustart/group_vars/all/ssh_keys.yml`

**2. Distribute new keys**:

```bash
ansible-playbook -i inventories/ovh_soyoustart/inventory.ini day0.yml --tags ssh_keys
```

### Firewall Audits

```bash
# List all firewall rules
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "ufw status numbered"

# Check for specific port
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "ufw status | grep 22"
```

---

## Troubleshooting

### Connectivity Issues

```bash
# Test ping
ansible -i inventories/ovh_soyoustart/inventory.ini all -m ping

# Test SSH
ssh root@<hostname>

# Check routing
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "ip route"

# Check network interfaces
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "ip -br a"
```

### Service Issues

```bash
# Check service status
ansible -i inventories/ovh_soyoustart/inventory.ini all -m systemd -a "name=<service>"

# View service logs
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "journalctl -u <service> -n 50"

# Restart service
ansible -i inventories/ovh_soyoustart/inventory.ini all -m systemd -a "name=<service> state=restarted"
```

### Performance Issues

```bash
# Check load average
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "uptime"

# Check disk I/O
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "iostat -x 1 3"

# Check memory usage
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "free -h"

# Check running processes
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "ps aux --sort=-%mem | head -10"
```

---

## Maintenance Windows

### Planning Maintenance

1. **Schedule maintenance window**
2. **Notify users**
3. **Create backups**
4. **Document changes**
5. **Prepare rollback plan**

### During Maintenance

```bash
# 1. Put cluster in maintenance mode (if applicable)

# 2. Take backups
# (See Backup section)

# 3. Perform changes

# 4. Test changes

# 5. Monitor systems
```

### Post-Maintenance

```bash
# Verify all services
ansible -i inventories/ovh_soyoustart/inventory.ini all -m ping
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_nodes -m shell -a "pvecm status"
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_master -m shell -a "kubectl get nodes"

# Check logs for errors
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "journalctl --since '1 hour ago' --priority err"
```

---

## Emergency Procedures

### Service Down

```bash
# Identify failed service
ansible -i inventories/ovh_soyoustart/inventory.ini all -m shell -a "systemctl --failed"

# Restart service
ansible -i inventories/ovh_soyoustart/inventory.ini <host> -m systemd -a "name=<service> state=restarted"

# Check logs
ansible -i inventories/ovh_soyoustart/inventory.ini <host> -m shell -a "journalctl -u <service> -n 100"
```

### Node Down

```bash
# Check if node is accessible
ansible -i inventories/ovh_soyoustart/inventory.ini <node> -m ping

# If not accessible, check via OOB/IPMI or cloud provider console

# Verify cluster quorum (Proxmox)
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_nodes -m shell -a "pvecm status"

# Verify K8s cluster
ansible -i inventories/ovh_soyoustart/inventory.ini kubernetes_master -m shell -a "kubectl get nodes"
```

### Data Loss Prevention

```bash
# Immediate GlusterFS snapshot
ssh root@p21
gluster snapshot create emergency-$(date +%Y%m%d-%H%M%S) <volume_name>

# Immediate ZFS snapshot
ansible -i inventories/ovh_soyoustart/inventory.ini baremetal_hosts -m shell -a "zfs snapshot rpool/data@emergency-$(date +%Y%m%d-%H%M%S)"

# Immediate VM snapshot
ansible -i inventories/ovh_soyoustart/inventory.ini proxmox_master -m shell -a "qm snapshot <vmid> emergency-$(date +%Y%m%d-%H%M%S)"
```

---

This operations guide provides comprehensive procedures for Day-N maintenance and management of the WizzCloud Ansible Lab infrastructure. Regular maintenance following these procedures will ensure a stable and reliable environment.
