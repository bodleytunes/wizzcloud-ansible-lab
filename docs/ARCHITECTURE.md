# WizzCloud Ansible Lab Architecture

This document provides a comprehensive overview of the WizzCloud Ansible Lab architecture, including infrastructure design, network topology, storage architecture, and component interactions.

## Table of Contents

- [High-Level Overview](#high-level-overview)
- [Infrastructure Layers](#infrastructure-layers)
- [Network Architecture](#network-architecture)
- [Storage Architecture](#storage-architecture)
- [Compute Architecture](#compute-architecture)
- [Identity and Access Architecture](#identity-and-access-architecture)
- [High Availability Design](#high-availability-design)
- [Security Architecture](#security-architecture)
- [Data Flow](#data-flow)
- [Scaling Considerations](#scaling-considerations)

---

## High-Level Overview

The WizzCloud Ansible Lab implements a multi-layered, highly available private cloud infrastructure that spans multiple cloud providers (OVH SoyouStart and Hetzner Cloud). The architecture follows a layered approach with clear separation of concerns.

### Design Principles

1. **Infrastructure as Code**: All components defined and managed via Ansible
2. **Idempotency**: Playbooks can be run multiple times safely
3. **High Availability**: Redundant components across multiple sites
4. **Security First**: Encrypted overlays, certificate-based auth, firewall rules
5. **Modularity**: Component-based design with clear interfaces
6. **Multi-Cloud**: Provider-agnostic where possible
7. **Automation**: Minimal manual intervention required

### Key Metrics

- **Deployment Time**: ~2-4 hours for full stack (depending on scale)
- **Supported Cloud Providers**: 2 (OVH SoyouStart, Hetzner Cloud)
- **Infrastructure Layers**: 6 distinct layers
- **Network Overlays**: 3 concurrent overlay networks
- **Storage Systems**: 4 different storage technologies
- **Management Domains**: 2 (OVH site, Hetzner site)

---

## Infrastructure Layers

The infrastructure is organized into six distinct layers, each building on the previous:

```
┌─────────────────────────────────────────────────────────────────────┐
│                      LAYER 6: APPLICATIONS                           │
│  ┌────────────┬────────────┬────────────┬────────────┬───────────┐ │
│  │  Rancher   │    Plex    │   Elastic  │   SABnzbd  │  Portainer│ │
│  │   (K8s UI) │   (Media)  │  (Logging) │  (Downloads)│  (Docker) │ │
│  └────────────┴────────────┴────────────┴────────────┴───────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    LAYER 5: ORCHESTRATION                            │
│  ┌────────────┬────────────┬────────────┬────────────┬───────────┐ │
│  │    K3s     │  Terraform │  FreeIPA   │  Teleport  │   Docker  │ │
│  │ (K8s Lite) │(IaC for VM)│   (IDM)    │  (SSH Alt) │ (Runtime) │ │
│  └────────────┴────────────┴────────────┴────────────┴───────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                   LAYER 4: VIRTUALIZATION                            │
│  ┌────────────────────┬──────────────────┬────────────────────────┐│
│  │   Proxmox Cluster  │    LXD/LXC      │   Virtual Machines     ││
│  │  (KVM Hypervisor)  │  (Containers)   │   (Cloud-Init)         ││
│  └────────────────────┴──────────────────┴────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      LAYER 3: STORAGE                                │
│  ┌─────────┬──────────┬──────────┬──────────┬──────────┬─────────┐ │
│  │   ZFS   │ GlusterFS│ LINSTOR  │  S3FS    │  Samba   │LizardFS │ │
│  │ (Local) │(Distrib.)│  (DRBD)  │(Backblaze)│(SMB/CIFS)│ (Media) │ │
│  └─────────┴──────────┴──────────┴──────────┴──────────┴─────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      LAYER 2: NETWORKING                             │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┬────────┐ │
│  │ FRR BGP  │  Nebula  │ ZeroTier │Wireguard │ EVPN/    │   UFW  │ │
│  │(Routing) │ (Mesh)   │ (Overlay)│  (VPN)   │  VXLAN   │(Firewall)│
│  └──────────┴──────────┴──────────┴──────────┴──────────┴────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     LAYER 1: BARE METAL                              │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │     Debian 10 Buster on OVH SoyouStart / Hetzner Cloud         │ │
│  │        (Physical Servers with Public IP Addresses)             │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Layer Descriptions

#### Layer 1: Bare Metal
- **Purpose**: Physical server infrastructure
- **Components**: Debian 10 Buster on dedicated servers
- **Providers**: OVH SoyouStart, Hetzner Cloud
- **Characteristics**: Public IP addresses, direct hardware access

#### Layer 2: Networking
- **Purpose**: Connectivity and routing between all components
- **Components**: BGP, overlay networks, VPN, firewall
- **Key Feature**: Multi-overlay architecture with encryption

#### Layer 3: Storage
- **Purpose**: Data persistence and sharing
- **Components**: Local, distributed, and cloud storage
- **Key Feature**: Multiple storage tiers for different use cases

#### Layer 4: Virtualization
- **Purpose**: Resource abstraction and isolation
- **Components**: Proxmox VE, LXD, VMs
- **Key Feature**: Full virtualization with clustering

#### Layer 5: Orchestration
- **Purpose**: Workload management and automation
- **Components**: Kubernetes, Terraform, Identity management
- **Key Feature**: Declarative infrastructure and workload definitions

#### Layer 6: Applications
- **Purpose**: End-user services and applications
- **Components**: Web apps, media services, logging
- **Key Feature**: Containerized applications on Kubernetes

---

## Network Architecture

The network architecture implements a sophisticated multi-overlay design with redundant paths and encrypted tunneling.

### Network Topology

```
                          [Internet]
                              │
                 ┌────────────┼────────────┐
                 │                         │
        [OVH SoyouStart Site]    [Hetzner Cloud Site]
                 │                         │
        ┌────────┴────────┐       ┌───────┴────────┐
        │  Baremetal p21  │       │  Baremetal     │
        │  (Public IP)    │       │  rancher1-3    │
        └────────┬────────┘       └────────┬───────┘
                 │                         │
         ┌───────┴───────┐         ┌──────┴───────┐
         │               │         │              │
    [ZeroTier   [Nebula Mesh]  [Wireguard] [ZeroTier
     Overlay]              Overlay]           Overlay]
         │                      │              │
         └──────────────┬───────┴──────────────┘
                        │
            [Unified Overlay Network]
                        │
         ┌──────────────┼──────────────┐
         │              │              │
    [BGP/EVPN      [Proxmox       [Virtual
     VXLAN]         Cluster]       Machines]
     Tunnel]
```

### Overlay Network Stack

The architecture uses three concurrent overlay networks, each serving different purposes:

#### Overlay 1: ZeroTier-One
- **Purpose**: Primary encrypted inter-site connectivity
- **Technology**: Peer-to-peer encrypted mesh with central controller
- **IP Range**: Typically 10.x.x.x/24 (configured per deployment)
- **Features**:
  - Centrally managed via ZeroTier API
  - NAT traversal built-in
  - Encrypted with Salsa20/Poly1305
  - Automatic peer discovery
- **Use Cases**:
  - Inter-site communication
  - Management traffic
  - Encapsulation tunnel for VXLAN

#### Overlay 2: Slack Nebula
- **Purpose**: P2P encrypted mesh with lighthouse-based discovery
- **Technology**: Certificate-based P2P overlay
- **IP Range**: Separate from ZeroTier (e.g., 192.168.100.0/24)
- **Features**:
  - No central controller (fully distributed)
  - Certificate-based authentication
  - Lighthouse nodes for discovery
  - Noise protocol encryption
  - Firewall rules embedded in certificates
- **Use Cases**:
  - Alternative/backup connectivity
  - Specific isolated networks
  - Certificate-based access control

#### Overlay 3: Wireguard
- **Purpose**: Point-to-point VPN tunnels
- **Technology**: Kernel-integrated VPN
- **Features**:
  - Extremely fast (kernel-space)
  - Minimal attack surface
  - Simple configuration
  - Perfect forward secrecy
- **Use Cases**:
  - Site-to-site tunnels
  - Specific encrypted links
  - Performance-critical connections

### BGP Routing Architecture

FRR (Free Range Routing) provides dynamic routing with BGP:

```
┌─────────────────────────────────────────────────────────────┐
│                    FRR BGP Architecture                      │
│                                                              │
│  Node p21 (AS 65001)          Node p22 (AS 65002)          │
│  ┌─────────────┐              ┌─────────────┐              │
│  │ FRR BGP     │◄────────────►│ FRR BGP     │              │
│  │ Router ID:  │  iBGP/eBGP   │ Router ID:  │              │
│  │ 10.100.0.1  │              │ 10.100.0.2  │              │
│  └──────┬──────┘              └──────┬──────┘              │
│         │                            │                      │
│         │                            │                      │
│  ┌──────▼──────┐              ┌─────▼───────┐             │
│  │  Advertises │              │  Advertises │             │
│  │  - Anycast  │              │  - Anycast  │             │
│  │  - Loopback │              │  - Loopback │             │
│  │  - VM nets  │              │  - VM nets  │             │
│  └─────────────┘              └─────────────┘             │
│                                                              │
│  Anycast IPs (advertised by multiple nodes):               │
│  - 10.0.0.6 (Teleport Auth Server)                         │
│  - 10.0.0.253/254 (Load Balancers)                         │
└─────────────────────────────────────────────────────────────┘
```

**BGP Features**:
- **EVPN/VXLAN**: Layer 2 overlay for VM networking
- **Anycast**: Multiple nodes advertise same IP for HA
- **Dynamic Routing**: Automatic failover and load balancing
- **Route Filtering**: Control which routes are advertised
- **Integration**: Pritunl VPN routes injected via BGP

### EVPN/VXLAN Architecture

EVPN (Ethernet VPN) with VXLAN provides Layer 2 extension across sites:

```
┌──────────────────────────────────────────────────────────────┐
│               EVPN/VXLAN Layer 2 Extension                    │
│                                                               │
│  Site 1 (OVH)                        Site 2 (Hetzner)        │
│  ┌──────────────┐                    ┌──────────────┐       │
│  │ Bridge vmbr1 │                    │ Bridge vmbr1 │       │
│  │ (VMs attach) │                    │ (VMs attach) │       │
│  └──────┬───────┘                    └──────┬───────┘       │
│         │                                   │               │
│    ┌────▼────┐                         ┌───▼─────┐         │
│    │  VXLAN  │                         │  VXLAN  │         │
│    │ Tunnel  │◄───────────────────────►│ Tunnel  │         │
│    │ VNI:100 │  (Encapped via ZT)     │ VNI:100 │         │
│    └─────────┘                         └─────────┘         │
│                                                               │
│  VMs on both sites share same L2 domain (10.100.0.0/24)    │
└──────────────────────────────────────────────────────────────┘
```

**Key Points**:
- VXLAN tunnels encapsulated through ZeroTier overlay
- Allows VMs on different sites to be on same subnet
- BGP EVPN for control plane (MAC address distribution)
- VNI (VXLAN Network Identifier) for network segmentation

### Traffic Control and QoS

Linux Traffic Control with CAKE (Common Applications Kept Enhanced) QoS:

```
┌────────────────────────────────────────────────────┐
│            Traffic Control Architecture             │
│                                                     │
│  1. Packet arrives on interface                    │
│  2. IPtables mangle marks packet with DSCP        │
│  3. TC CAKE classifier processes based on DSCP     │
│  4. CAKE tins assign priority:                     │
│     - Tin 0: Network Control (highest)             │
│     - Tin 1: Video Streaming                       │
│     - Tin 2: Best Effort                           │
│     - Tin 3: Bulk (lowest)                         │
│  5. CAKE shaper enforces bandwidth limits          │
│  6. Packet forwarded                               │
└────────────────────────────────────────────────────┘
```

**DSCP Marking Example**:
```
Video Traffic → DSCP 34 → CAKE Tin 1 (Priority)
Normal Traffic → DSCP 0 → CAKE Tin 2 (Best Effort)
Bulk Downloads → DSCP 8 → CAKE Tin 3 (Low Priority)
```

### Firewall Architecture

UFW (Uncomplicated Firewall) with custom rules:

- **Default Policy**: Deny all incoming, allow outgoing
- **Allowed Services**: SSH, HTTPS, custom ports per service
- **NAT Rules**: Port forwarding for ingress traffic
- **Overlay Integration**: Allow traffic on overlay interfaces
- **Rate Limiting**: SSH brute force protection

---

## Storage Architecture

The storage architecture implements multiple storage tiers for different use cases.

### Storage Tier Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                      Storage Architecture                         │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Tier 1: Local High-Performance Storage (ZFS)              │ │
│  │  - Use Case: VM boot disks, databases, hot data            │ │
│  │  - Technology: ZFS with compression and dedup              │ │
│  │  - Performance: Highest (local NVMe/SSD)                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Tier 2: Distributed Storage (GlusterFS)                   │ │
│  │  - Use Case: K8s persistent volumes, shared data           │ │
│  │  - Technology: GlusterFS replicated volumes                │ │
│  │  - Performance: Medium (network-dependent)                 │ │
│  │  - Redundancy: 2-3x replication                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Tier 3: Block Replication (LINSTOR/DRBD)                 │ │
│  │  - Use Case: Proxmox VM storage with live migration       │ │
│  │  - Technology: DRBD synchronous replication                │ │
│  │  - Performance: High (dedicated replication network)       │ │
│  │  - Redundancy: Synchronous mirroring                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Tier 4: Cloud Backup (S3FS/Backblaze)                    │ │
│  │  - Use Case: Offsite backups, archival                    │ │
│  │  - Technology: S3FS FUSE mount to Backblaze B2            │ │
│  │  - Performance: Low (internet-dependent)                   │ │
│  │  - Redundancy: Cloud provider redundancy                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Tier 5: Media Storage (LizardFS)                         │ │
│  │  - Use Case: Plex media files, large files                │ │
│  │  - Technology: LizardFS distributed filesystem            │ │
│  │  - Performance: Optimized for large files                  │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### Storage Use Case Matrix

| Storage Type | Use Case | Performance | Redundancy | Cost |
|--------------|----------|-------------|------------|------|
| ZFS Local | VM boot, DBs | Highest | RAID/mirrors | Medium |
| GlusterFS | K8s PVs, shared files | Medium | 2-3x replication | Medium |
| LINSTOR | Proxmox storage, HA VMs | High | Sync replication | Medium |
| S3FS | Backups, archives | Low | Cloud redundancy | Low |
| LizardFS | Media files, Plex | Medium | Configurable | Low |
| Samba | SMB shares, Windows | Medium | Depends on backend | Low |

### ZFS Configuration

**Zpools**:
- Pool for VM storage
- Pool for container storage
- Optimizations: compression (lz4), atime=off

**Datasets**:
- Separate datasets per use case
- Snapshot policies for backups
- ZFS send/receive for replication

### GlusterFS Architecture

```
┌────────────────────────────────────────────────────────┐
│             GlusterFS Distributed Storage               │
│                                                         │
│  Node p21           Node p22           Node rancher1   │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐    │
│  │ Brick 1  │      │ Brick 2  │      │ Brick 3  │    │
│  │ /gluster │      │ /gluster │      │ /gluster │    │
│  └────┬─────┘      └────┬─────┘      └────┬─────┘    │
│       │                 │                 │           │
│       └─────────────────┼─────────────────┘           │
│                         │                             │
│                ┌────────▼────────┐                    │
│                │ GlusterFS Volume│                    │
│                │   (Replicated)  │                    │
│                │  Replica Count:3│                    │
│                └────────┬────────┘                    │
│                         │                             │
│                ┌────────▼────────┐                    │
│                │  FUSE Mount on  │                    │
│                │  Client Nodes   │                    │
│                │ /mnt/glusterfs  │                    │
│                └─────────────────┘                    │
│                         │                             │
│                         ▼                             │
│              Kubernetes PersistentVolumes             │
└────────────────────────────────────────────────────────┘
```

---

## Compute Architecture

### Proxmox Cluster Architecture

```
┌───────────────────────────────────────────────────────────┐
│                  Proxmox VE Cluster                        │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Node p21    │  │  Node p22    │  │  Node p42    │   │
│  │  (Master)    │  │  (Member)    │  │  (Member)    │   │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤   │
│  │ CPU: X cores │  │ CPU: X cores │  │ CPU: X cores │   │
│  │ RAM: X GB    │  │ RAM: X GB    │  │ RAM: X GB    │   │
│  │ Storage: ZFS │  │ Storage: ZFS │  │ Storage: ZFS │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │            │
│         └─────────────────┼─────────────────┘            │
│                           │                              │
│                  ┌────────▼────────┐                     │
│                  │  Cluster Quorum │                     │
│                  │  (Corosync)     │                     │
│                  └────────┬────────┘                     │
│                           │                              │
│                  ┌────────▼────────┐                     │
│                  │   Shared Config │                     │
│                  │   (pmxcfs)      │                     │
│                  └─────────────────┘                     │
└───────────────────────────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │        Virtual Machines              │
        │  ┌──────┐ ┌──────┐ ┌──────┐ ┌─────┐│
        │  │ kube1│ │ kube2│ │ lb1  │ │plex ││
        │  └──────┘ └──────┘ └──────┘ └─────┘│
        └──────────────────────────────────────┘
```

### Kubernetes (K3s) Architecture

```
┌────────────────────────────────────────────────────────────┐
│                K3s Lightweight Kubernetes                   │
│                                                             │
│  Master Nodes (Control Plane)                              │
│  ┌────────────────┐  ┌────────────────┐                   │
│  │  kube1         │  │  kube2         │                   │
│  │  10.100.0.100  │  │  10.101.0.100  │                   │
│  ├────────────────┤  ├────────────────┤                   │
│  │ - API Server   │  │ - API Server   │                   │
│  │ - Scheduler    │  │ - Scheduler    │                   │
│  │ - Controller   │  │ - Controller   │                   │
│  │ - etcd         │  │ - etcd         │                   │
│  └────────┬───────┘  └────────┬───────┘                   │
│           │                   │                            │
│           └───────────┬───────┘                            │
│                       │                                    │
│              ┌────────▼────────┐                           │
│              │  K3s Cluster    │                           │
│              │  (HA Mode)      │                           │
│              └────────┬────────┘                           │
│                       │                                    │
│       ┌───────────────┼───────────────┐                   │
│       │               │               │                    │
│  ┌────▼────┐    ┌────▼────┐    ┌────▼────┐              │
│  │ Rancher │    │ MetalLB │    │Cert-Mgr │              │
│  │  (Mgmt) │    │   (LB)  │    │ (Certs) │              │
│  └─────────┘    └─────────┘    └─────────┘              │
│                                                             │
│  Application Workloads:                                    │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐                │
│  │  Plex   │  │ SABnzbd  │  │  Elastic │                │
│  │ (Media) │  │(Download)│  │ (Logging)│                │
│  └─────────┘  └──────────┘  └──────────┘                │
└────────────────────────────────────────────────────────────┘
```

**K3s Features Used**:
- Embedded etcd for HA
- Disabled Traefik (using custom ingress)
- Disabled ServiceLB (using MetalLB)
- GlusterFS for persistent volumes
- Helm for package management

---

## Identity and Access Architecture

### FreeIPA Deployment

```
┌──────────────────────────────────────────────────────────┐
│              FreeIPA Identity Management                  │
│                                                           │
│  OVH Site                        Hetzner Site            │
│  ┌─────────────────┐            ┌─────────────────┐     │
│  │ IPA Master      │            │ IPA Replica     │     │
│  │ (Primary)       │◄──────────►│ (Secondary)     │     │
│  ├─────────────────┤            ├─────────────────┤     │
│  │ - LDAP          │ Replication│ - LDAP          │     │
│  │ - Kerberos KDC  │            │ - Kerberos KDC  │     │
│  │ - DNS           │            │ - DNS           │     │
│  │ - CA            │            │ - CA            │     │
│  └────────┬────────┘            └────────┬────────┘     │
│           │                              │              │
│           └──────────┬───────────────────┘              │
│                      │                                   │
│          ┌───────────▼───────────┐                      │
│          │   IPA Clients         │                      │
│          │  (All VMs + Hosts)    │                      │
│          ├───────────────────────┤                      │
│          │ - SSSD Authentication │                      │
│          │ - Kerberos Tickets    │                      │
│          │ - Host Certificates   │                      │
│          └───────────────────────┘                      │
└──────────────────────────────────────────────────────────┘
```

**FreeIPA Services**:
- **LDAP**: User and group directory
- **Kerberos**: Single sign-on authentication
- **DNS**: Integrated DNS management
- **Certificate Authority**: TLS certificate issuance
- **SSSD**: System Security Services Daemon on clients

### Teleport Access Architecture

```
┌──────────────────────────────────────────────────────────┐
│           Gravitational Teleport Architecture             │
│                                                           │
│  ┌─────────────────────────────────────────────┐        │
│  │         Teleport Auth Server                │        │
│  │         (10.0.0.6 - Anycast)               │        │
│  │  ┌───────────────────────────────────────┐ │        │
│  │  │ - Certificate Authority               │ │        │
│  │  │ - User Database                       │ │        │
│  │  │ - Session Recordings                  │ │        │
│  │  │ - RBAC Policies                       │ │        │
│  │  └───────────────────────────────────────┘ │        │
│  │                                             │        │
│  │  Advertised via BGP Anycast                │        │
│  │  (HA - multiple nodes share same IP)       │        │
│  └─────────────────┬───────────────────────────┘        │
│                    │                                     │
│          ┌─────────┴──────────┐                         │
│          │                    │                         │
│  ┌───────▼─────────┐  ┌──────▼─────────┐              │
│  │ Teleport Proxy  │  │ Teleport Proxy │              │
│  │  (Web UI/SSH)   │  │  (Web UI/SSH)  │              │
│  └───────┬─────────┘  └──────┬─────────┘              │
│          │                   │                         │
│          └────────┬──────────┘                         │
│                   │                                     │
│          ┌────────▼────────┐                           │
│          │ Teleport Clients│                           │
│          │ (All Nodes/VMs) │                           │
│          ├─────────────────┤                           │
│          │ - Node Service  │                           │
│          │ - Cert-based    │                           │
│          │   SSH           │                           │
│          └─────────────────┘                           │
└──────────────────────────────────────────────────────────┘
```

**Teleport Features**:
- **Certificate-Based SSH**: No password/key management
- **Session Recording**: All SSH sessions recorded
- **RBAC**: Role-based access control
- **Web UI**: Browser-based terminal access
- **Audit Logging**: Complete access audit trail
- **Anycast HA**: Auth servers on anycast IP for redundancy

---

## High Availability Design

### HA Components

| Component | HA Strategy | Redundancy Level |
|-----------|-------------|------------------|
| **Proxmox Cluster** | Multi-node cluster with quorum | 3+ nodes |
| **K3s Control Plane** | Embedded etcd HA | 2+ masters |
| **FreeIPA** | Master + Replica(s) | 2+ servers |
| **Teleport Auth** | Anycast BGP + multiple instances | 2+ servers |
| **Load Balancers** | Anycast BGP + HAProxy | 2+ instances |
| **GlusterFS** | Replicated volumes | 2-3x replication |
| **LINSTOR** | Synchronous DRBD replication | 2x replication |
| **Network Overlays** | Multiple concurrent overlays | 3 overlays |

### Failover Mechanisms

**Anycast Failover** (Teleport, Load Balancers):
1. Multiple servers advertise same IP via BGP
2. BGP routing directs traffic to nearest/available server
3. Server failure triggers BGP withdraw
4. Traffic automatically reroutes to remaining servers

**Kubernetes HA** (K3s):
1. Multiple control plane nodes with embedded etcd
2. Client load balancing across API servers
3. Automatic leader election
4. Pod rescheduling on node failure

**Storage HA** (GlusterFS):
1. Data replicated across multiple bricks
2. Self-healing on brick failure
3. Client-side failover to replica bricks
4. Automatic rebalance on new brick addition

---

## Security Architecture

### Defense in Depth

```
┌──────────────────────────────────────────────────────────┐
│                  Security Layers                          │
│                                                           │
│  Layer 7: Application Security                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ - RBAC in Kubernetes/Rancher                        │ │
│  │ - Application-level auth                            │ │
│  └─────────────────────────────────────────────────────┘ │
│                         ↓                                 │
│  Layer 6: Identity & Access                              │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ - FreeIPA centralized auth                          │ │
│  │ - Teleport certificate-based SSH                    │ │
│  │ - SSH key management                                │ │
│  └─────────────────────────────────────────────────────┘ │
│                         ↓                                 │
│  Layer 5: Encryption                                     │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ - TLS for all web services                          │ │
│  │ - Cert-Manager for certificate automation           │ │
│  └─────────────────────────────────────────────────────┘ │
│                         ↓                                 │
│  Layer 4: Network Encryption                             │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ - ZeroTier encrypted overlay                        │ │
│  │ - Nebula encrypted mesh                             │ │
│  │ - Wireguard VPN                                      │ │
│  └─────────────────────────────────────────────────────┘ │
│                         ↓                                 │
│  Layer 3: Firewall                                       │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ - UFW on all hosts                                  │ │
│  │ - Default deny inbound                              │ │
│  │ - Service-specific allow rules                      │ │
│  └─────────────────────────────────────────────────────┘ │
│                         ↓                                 │
│  Layer 2: Network Segmentation                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ - VLANs and network isolation                       │ │
│  │ - Overlay network segmentation                      │ │
│  └─────────────────────────────────────────────────────┘ │
│                         ↓                                 │
│  Layer 1: Physical Security                              │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ - Provider datacenter security                      │ │
│  │ - IPMI/OOB access control                           │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### Secret Management

- **Ansible Vault**: Encrypted variables in group_vars
- **FreeIPA**: Certificate storage and distribution
- **Kubernetes Secrets**: Application secrets in K8s
- **Teleport**: Certificate-based authentication tokens

---

## Data Flow

### VM Provisioning Flow

```
Ansible → Terraform → Proxmox API → KVM → Cloud-Init → VM Running
   │                                                        │
   └────────────────────────────────────────────────────────┘
              (Ansible configures running VM)
```

### User Access Flow (via Teleport)

```
User → Teleport Proxy → Teleport Auth (Anycast) → Certificate Issued
   │                                                        │
   └────────────────────────────────────────────────────────┘
              (User connects to node with certificate)
```

### Application Deployment Flow (K8s)

```
Helm Chart → K3s API Server → Scheduler → Node Selection
                                              │
                                              ▼
                                    Pod Scheduling → Container Start
                                              │
                                              ▼
                                    GlusterFS PV Mount → App Running
```

---

## Scaling Considerations

### Horizontal Scaling

- **Proxmox Nodes**: Add nodes to cluster, automatic VM distribution
- **K3s Nodes**: Add agents, automatic pod rescheduling
- **GlusterFS Bricks**: Add bricks, rebalance volumes
- **Overlay Networks**: Automatic peer discovery and mesh expansion

### Vertical Scaling

- **VM Resources**: Increase CPU/RAM via Proxmox
- **Storage**: Expand zpools, add disks to GlusterFS
- **Network**: Increase bandwidth, optimize QoS tins

### Geographic Expansion

- **New Sites**: Deploy infrastructure in new cloud provider
- **Overlay Extension**: ZeroTier/Nebula automatic mesh to new site
- **FreeIPA Replica**: Deploy replica at new site for local auth
- **BGP Peering**: Establish BGP peering for routing

---

This architecture provides a robust, scalable, and highly available private cloud infrastructure suitable for production workloads across multiple sites.
