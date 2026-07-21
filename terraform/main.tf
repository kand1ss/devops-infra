resource "hcloud_firewall" "firewall" {
  name = "my-firewall"

  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "22"
    source_ips = [
      "100.64.0.0/10"
    ]
  }

  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "80"
    source_ips = [
      "0.0.0.0/0",
      "::/0"
    ]
  }

  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "443"
    source_ips = [
      "0.0.0.0/0",
      "::/0"
    ]
  }
}

data "hcloud_ssh_key" "default_key" {
  name = "Default"
}

variable "tskey_auth" {
  type      = string
  sensitive = true
}

variable "ts_host" {
  type      = string
  sensitive = false
}

resource "hcloud_server" "app-server" {
  name        = "app-server"
  image       = "ubuntu-24.04"
  server_type = "cx23"
  location    = "nbg1"

  user_data = templatefile("${path.module}/cloud-init.tpl", {
    tailscale_authkey = var.tskey_auth
    tailscale_host    = var.ts_host
  })

  ssh_keys = [
    data.hcloud_ssh_key.default_key.id
  ]

  firewall_ids = [
    hcloud_firewall.firewall.id
  ]

  public_net {
    ipv4_enabled = true
    ipv6_enabled = true
  }
}

output "server_public_ip" {
  value       = hcloud_server.app-server.ipv4_address
  description = "Server IP"
}
