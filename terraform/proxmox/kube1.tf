
resource "proxmox_vm_qemu" "kube1" {

  vmid        = 113
  name        = "kube1.wizznet.co.uk"
  target_node = "p20"
  clone       = "9003-ubuntu-20-04-template"
  full_clone  = false
  clone_wait  = 12
  bootdisk    = "scsi0"
  os_type     = "cloud-init"
  agent       = 0
  # custom cloud init file located on proxmox host in snippets dir
  #cicustom = "user=local:snippets/user-data-cicustom.yaml"


  cores   = 4
  sockets = 1
  memory  = 12000

  ipconfig0  = "ip=10.100.0.100/24,gw=10.100.0.1"
  nameserver = "10.20.66.5"
  network {
    model  = "virtio"
    bridge = "lxdbr0"
  }
  ciuser = "jon"

  sshkeys = <<EOF
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJjM78UyIQWNbMsca2qafeshPflijH8HbbsKuTTZqB1F jon@DESKTOP-SNM4E2E
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGlAs2ApLH1sTfDTfYvFDcDS5cyAdkCqcJ28D+4Lpuyo jon@troon
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJpASWQUj+UkSv2M4kgxMEeM3oUYtKI54N1CVnwKrk9A root@salt
EOF

  disk {
    size    = "12G"
    type    = "scsi"
    storage = "zpool1"
    replicate = 1
  }
  disk {
    size    = "100G"
    type    = "scsi"
    storage = "zpool1"
    replicate = 1
  }

  # basic remote execution script 
  # provisioner "remote-exec" {
  #   inline = [
  #     "sudo hostnamectl set-hostname ${local.kube[113]["name"]}",
  #   ]
  #   connection {
  #     private_key = file(var.ssh_private_key)
  #     host        = "10.100.0.100"
  #     user        = "jon"
  #   }
  # }

  lifecycle {
    ignore_changes = [
      network,
    ]
  }

}
