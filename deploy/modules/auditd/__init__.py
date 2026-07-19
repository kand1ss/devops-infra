import os
from pyinfra.operations import server
from shared.block_render import render_managed_block

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATES_DIR = os.path.join(CURRENT_DIR, "templates")


def setup_security_auditing():
    config_path = os.path.join(TEMPLATES_DIR, "security.rules.j2")
    with open(config_path, "r", encoding="utf-8") as file:
        content = file.read()
        render_managed_block(
            dest="/etc/audit/rules.d/security.rules",
            block_name="security_audit",
            content=content,
        )

    server.shell(
        name="Reload auditd configuration",
        commands=["augenrules --load"],
    )
