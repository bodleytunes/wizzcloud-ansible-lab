locals {
  teleport_host = { 190 = { "name" = "pritunl.wizznet.co.uk" } }
}

resource "proxmox_vm_qemu" "pritunl" {

  vmid        = 0
  name        = local.teleport_host["190"]["name"]
  target_node = "p21"
  clone       = "9003-ubuntu-20-04-template"
  os_type     = "cloud-init"
  agent       = 1
  # custom cloud init file located on proxmox host in snippets dir
  #cicustom = "user=local:snippets/user-data-cicustom.yaml"


  cores   = 1
  sockets = 1
  memory  = 2048

  ipconfig0  = "ip=10.0.0.7/24,gw=10.0.0.1"
  nameserver = "10.22.66.5"
  network {
    model  = "virtio"
    bridge = "evpn100"
  }
  ciuser = "jon"

  sshkeys = <<EOF
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJjM78UyIQWNbMsca2qafeshPflijH8HbbsKuTTZqB1F jon@DESKTOP-SNM4E2E
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGlAs2ApLH1sTfDTfYvFDcDS5cyAdkCqcJ28D+4Lpuyo jon@troon
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJpASWQUj+UkSv2M4kgxMEeM3oUYtKI54N1CVnwKrk9A root@salt
EOF

  disk {
    size    = "24G"
    type    = "scsi"
    storage = "zpool1"
  }


  lifecycle {
    ignore_changes = [
      network,
    ]
  }

}
