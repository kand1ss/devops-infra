terraform {
  required_version = "~> 1.15.7"
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = ">=1.45"
    }
  }
}

variable "hcloud_token" {
  sensitive = true
  type      = string
}


provider "hcloud" {
  token = var.hcloud_token
}
