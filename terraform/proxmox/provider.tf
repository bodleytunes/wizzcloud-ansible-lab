terraform {
  required_providers {
    proxmox = {
      source  = "Telmate/proxmox"
      version = "2.6.8"
    }
  }
  required_version = ">= 0.14"
}

provider "proxmox" {
  pm_tls_insecure = true

  // Credentials here or environment
  pm_api_url    = "https://ns31050143.ip-51-77-116.eu:8006/api2/json"
  pm_user       = "terraform-prov@pve"
  pm_parallel   = 2      
  pm_log_enable = true
  pm_log_file   = "terraform-plugin-proxmox.log"
  pm_log_levels = {
    _default = "debug"
  }
}

