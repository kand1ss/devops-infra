import os
from pyinfra.operations import apt, server, systemd, files
from dotenv import load_dotenv

load_dotenv()

NEW_USER = os.getenv("USER", "default")
SSH_PUBLIC_KEY = os.getenv(
    "SSH_PUBLIC_KEY", os.path.expanduser("~/.ssh/id_rsa.pub")
)

SUDO_PASSWORD_HASH = os.getenv("SUDO_PASSWORD_HASH")
if not SUDO_PASSWORD_HASH:
    raise RuntimeError("SUDO_PASSWORD_HASH env var is required")

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

apt.packages(
    name="Update PM",
    update=True,
    upgrade=True,
    _sudo=True,
    _env={
        "DEBIAN_FRONTEND": "noninteractive",
        "APT_LISTCHANGES_FRONTEND": "none",
    },
)

apt.packages(
    name="Setup basic utilities",
    packages=[
        "git",
        "fail2ban",
        "ufw",
        "curl",
        "docker.io",
        "auditd",
    ],
    _sudo=True,
)

server.shell(
    name="Add Docker Repository",
    commands=[
        "mkdir -p /etc/apt/keyrings",
        "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg",
        'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu noble stable" | tee /etc/apt/sources.list.d/docker.list',
    ],
    _sudo=True,
)

apt.packages(
    name="Setup Docker Compose",
    packages=["docker-compose-plugin"],
    update=True,
    _sudo=True,
)

server.user(
    name="Creating user and adding to groups",
    user=NEW_USER,
    shell="/bin/bash",
    ensure_home=True,
    groups=["sudo", "docker"],
    _sudo=True,
)

server.user(
    name="Set password for sudo user",
    user=NEW_USER,
    password=SUDO_PASSWORD_HASH,
    _sudo=True,
)

files.line(
    name="Allow sudo with cached timestamp",
    path=f"/etc/sudoers.d/{NEW_USER}",
    line=f"{NEW_USER} ALL=(ALL) ALL",   
    _sudo=True,
)

files.line(
    name="Set sudo timestamp timeout",
    path=f"/etc/sudoers.d/{NEW_USER}",
    line=f"Defaults:{NEW_USER} timestamp_timeout=60",
    _sudo=True,
)

server.user_authorized_keys(
    name=f"Adding SSH-key to user '{NEW_USER}'",
    user=NEW_USER,
    public_keys=[open(SSH_PUBLIC_KEY).read().strip()],
    _sudo=True,
)

for service_name in ["fail2ban", "docker"]:
    systemd.service(
        name=f"Executing service '{service_name}'",
        service=service_name,
        enabled=True,
        running=True,
        _sudo=True,
    )

server.shell(
    name="Setup Firewall rules",
    commands=[
        "ufw allow OpenSSH",
        "ufw allow 80",
        "ufw allow 443",
        "echo 'y' | ufw enable",
    ],
    _sudo=True,
)

server.reboot(name="Server reboot", delay=5, _sudo=True)
