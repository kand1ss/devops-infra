import os

from pyinfra.operations import files
from shared.block_render import render_managed_block

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATES_DIR = os.path.join(CURRENT_DIR, "pam")


def setup_pam_audit_protection():
    templates_dir = os.path.join(CURRENT_DIR, "pam")
    files.template(
        name="Upload Fail2ban filter for auditd-pam",
        src=os.path.join(templates_dir, "pam_filter.conf.j2"),
        dest="/etc/fail2ban/filter.d/auditd-pam.conf",
        user="root",
        group="root",
        mode="644",
    )

    files.template(
        name="Upload Fail2ban jail for auditd-pam",
        src=os.path.join(templates_dir, "pam_jail.conf.j2"),
        dest="/etc/fail2ban/jail.d/auditd-pam.conf",
        user="root",
        group="root",
        mode="644",
    )


def setup_ufw_rule():
    templates_dir = os.path.join(CURRENT_DIR, "ufw")
    with open(
        os.path.join(templates_dir, "jail.local.j2"), "r", encoding="utf-8"
    ) as file:
        content = file.read()
        render_managed_block(
            dest="/etc/fail2ban/jail.local",
            block_name="ufw_integration",
            content=content,
        )
    with open(
        os.path.join(templates_dir, "ufw.conf.j2"), "r", encoding="utf-8"
    ) as file:
        content = file.read()
        render_managed_block(
            dest="/etc/fail2ban/action.d/ufw.conf",
            block_name="ufw_integration",
            content=content,
        )
