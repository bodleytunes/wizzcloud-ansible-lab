locals {
  lb2_ip       = "10.101.0.254"
  lb2_hostname = "lb2.wizznet.co.uk"
}

resource "proxmox_vm_qemu" "lb2" {

  vmid        = 202
  name        = "lb2.wizznet.co.uk"
  desc        = "HAproxy Load Balancer 2"
  target_node = "p21"
  clone       = "9006-ubuntu-20-04-template"
  clone_wait  = 12
  agent       = 0
  # custom cloud init file located on proxmox host in snippets dir
  #os_type  = "cloud-init"
  #cicustom = "user=local:snippets/user-data-cicustom.yaml"




  cores   = 1
  sockets = 1
  memory  = 2048

  ipconfig0  = "ip=10.101.0.254/24,gw=10.101.0.1"
  ipconfig1  = "ip=10.0.0.254/24"
  nameserver = "10.21.66.5"
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
    replicate = 1
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
  #     "sudo hostnamectl set-hostname ${local.lb2_hostname}",
  #   ]
  #   connection {
  #     private_key = file(var.ssh_private_key)
  #     host        = local.lb2_ip
  #     user        = "jon"
  #   }
  # }

  lifecycle {
    ignore_changes = [
      network,
    ]
  }

}
