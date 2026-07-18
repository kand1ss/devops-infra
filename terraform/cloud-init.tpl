#cloud-config
write_files:
  - path: /etc/profile.d/github_env.sh
    permissions: '0600'
    owner: root:root
    content: |
      export GITHUB_TOKEN="${github_token}"
