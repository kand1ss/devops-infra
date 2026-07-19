#cloud-config
runcmd:
  - curl -fsSL https://tailscale.com/install.sh | sh
  - tailscale up --authkey=${tailscale_authkey} --hostname=test-infrastructure-server --accept-dns=true
