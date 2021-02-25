


resource "proxmox_vm_qemu" "kube_p21" {

  vmid        = 0
  name        = local.kube["213"]["name"]
  target_node = "p21"
  clone       = "ubuntu-cloudinit-9004"
  agent       = 1
  # custom cloud init file located on proxmox host in snippets dir
  cicustom = "user=local:snippets/user-data-cicustom.yaml"

  cores   = 4
  sockets = 1
  memory  = 12000

  ipconfig0  = "ip=10.21.10.100/24,gw=10.21.10.1"
  nameserver = "9.9.9.9"
  ciuser     = "jon"


  sshkeys = <<EOF
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJjM78UyIQWNbMsca2qafeshPflijH8HbbsKuTTZqB1F jon@DESKTOP-SNM4E2E
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGlAs2ApLH1sTfDTfYvFDcDS5cyAdkCqcJ28D+4Lpuyo jon@troon
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJpASWQUj+UkSv2M4kgxMEeM3oUYtKI54N1CVnwKrk9A root@salt
EOF


  disk {
    size    = "8G"
    type    = "scsi"
    storage = "zfs1"
  }
  disk {
    size    = "100G"
    type    = "scsi"
    storage = "zfs1"
  }
  lifecycle {
    ignore_changes = [
      network,
    ]
  }

  # basic remote execution script 
  provisioner "remote-exec" {
    inline = [
      "sudo hostnamectl set-hostname ${local.kube[213]["name"]}",
      "sudo echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf",
      "sudo sysctl -p",
      "sudo wget -O bootstrap-salt.sh https://bootstrap.saltstack.com",
      "sudo chmod 700 bootstrap-salt.sh",
      "sudo ./bootstrap-salt.sh -A 86.29.22.70",
    ]
    connection {
      private_key = file(var.ssh_private_key)
      host        = "10.21.10.100"
      user        = "jon"
    }
  }

}

