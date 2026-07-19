import os
from pyinfra.operations import files
from shared.block_render import render_managed_block

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
SCRIPT_PATH = os.path.join(CURRENT_DIR, "prometheus", "ssh_alert.py")

REMOTE_SCRIPT_PATH = "/usr/local/bin/ssh_alert.py"
TEXTFILE_COLLECTOR_DIR = "/var/lib/node_exporter/textfile_collector"


def setup_ssh_login_prometheus_alerts():
    if not os.path.isfile(SCRIPT_PATH):
        raise FileNotFoundError(f"Missing script: {SCRIPT_PATH}")

    files.put(
        name="Upload SSH login alert script",
        src=SCRIPT_PATH,
        dest=REMOTE_SCRIPT_PATH,
        user="root",
        group="root",
        mode="750",
    )

    # session-фаза, не auth: срабатывает только при УСПЕШНОМ логине.
    # Это intentional — см. semantics fix в ssh_alert.py ниже.
    render_managed_block(
        dest="/etc/pam.d/sshd",
        block_name="ssh_alert_hook",
        content=f"session optional pam_exec.so {REMOTE_SCRIPT_PATH}",
    )
