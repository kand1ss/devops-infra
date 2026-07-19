#cloud-config
runcmd:
  - curl -fsSL https://tailscale.com/install.sh | sh
  - tailscale up --authkey=${tailscale_authkey} --hostname=infra --accept-dns=true
