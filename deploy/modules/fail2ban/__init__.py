import os
from pyinfra.operations import apt, files, server

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATES_DIR = os.path.join(CURRENT_DIR, "templates")


def setup_bruteforce_protection():
    changed = False
    jails = [
        {
            "local_name": "sshd-strict.conf.j2",
            "remote_path": "/etc/fail2ban/jail.d/sshd-strict.conf",
        },
    ]
    install_fail2ban = apt.packages(
        name="Install Fail2ban package",
        packages=["fail2ban"],
        update=True,
        cache_time=3600,
    )
    changed |= install_fail2ban.changed

    for jail in jails:
        local_file = os.path.join(TEMPLATES_DIR, jail["local_name"])
        if not os.path.isfile(local_file):
            raise FileNotFoundError(f"Missing template: {local_file}")

        upload_jail = files.template(
            name=f"Upload jail config: {jail['local_name']}",
            src=local_file,
            dest=jail["remote_path"],
            user="root",
            group="root",
            mode="644",
        )
        changed |= upload_jail.changed

    if changed:
        server.shell(name="Restart fail2ban", commands=["systemctl restart fail2ban"])
