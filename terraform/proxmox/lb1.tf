locals {
  lb1_ip       = "10.100.0.253"
  lb1_hostname = "lb1"
}

resource "proxmox_vm_qemu" "lb1" {

  vmid        = 201
  name        = "lb1"
  desc        = "HAproxy Load Balancer 1"
  target_node = "p20"
  clone       = "9005-ubuntu-20-04-template"
  agent       = 1
  # custom cloud init file located on proxmox host in snippets dir
  #cicustom = "user=local:snippets/user-data-cicustom.yaml"


  cores   = 1
  sockets = 1
  memory  = 2048

  ipconfig0  = "ip=10.100.0.253/24,gw=10.100.0.1"
  ipconfig1  = "ip=10.0.0.253/24"
  nameserver = "9.9.9.9"
  ciuser     = "jon"

  sshkeys = <<EOF
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJjM78UyIQWNbMsca2qafeshPflijH8HbbsKuTTZqB1F jon@DESKTOP-SNM4E2E
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGlAs2ApLH1sTfDTfYvFDcDS5cyAdkCqcJ28D+4Lpuyo jon@troon
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJpASWQUj+UkSv2M4kgxMEeM3oUYtKI54N1CVnwKrk9A root@salt
EOF

  disk {
    size      = "12G"
    type      = "scsi"
    storage   = "zpool1"
    replicate = true
  }

  network {
    model  = "virtio"
    bridge = "lxdbr0"
  }

  network {
    model  = "virtio"
    bridge = "evpn100"
  }


  # basic remote execution script 
  # provisioner "remote-exec" {
  #   inline = [
  #     "sudo hostnamectl set-hostname ${local.lb1_hostname}",
  #   ]
  #   connection {
  #     private_key = file(var.ssh_private_key)
  #     host        = local.lb1_ip
  #     user        = "jon"
  #   }
  # }

  lifecycle {
    ignore_changes = [
      network,
    ]
  }

}
