terraform {
  required_providers {
    proxmox = {
      source  = "Telmate/proxmox"
      version = "2.6.4"
    }
  }
  required_version = ">= 0.13"
}

provider "proxmox" {
  pm_tls_insecure = true

  // Credentials here or environment
  pm_api_url    = "https://10.55.0.20:8006/api2/json"
  pm_user       = "terraform-prov@pve"
  pm_log_enable = true
  pm_log_file   = "terraform-plugin-proxmox.log"
  pm_log_levels = {
    _default = "debug"
  }
}

