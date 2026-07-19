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

variable "github_token" {
  type      = string
  sensitive = true
}

resource "hcloud_server" "app-server" {
  name        = "app-server"
  image       = "ubuntu-24.04"
  server_type = "cx23"
  location    = "nbg1"

  ssh_keys = [
    data.hcloud_ssh_key.default_key.id
  ]

  user_data = templatefile("${path.module}/cloud-init.tpl", {
    github_token = var.github_token
  })

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
