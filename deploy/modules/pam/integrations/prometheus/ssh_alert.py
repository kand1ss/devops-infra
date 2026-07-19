#!/usr/bin/env python3
import fcntl
import json
import logging
import logging.handlers
import os
import sys
import time
from pathlib import Path

METRIC_DIR = Path("/var/lib/node_exporter/textfile_collector")
METRIC_FILE = METRIC_DIR / "ssh_logins.prom"
STATE_FILE = METRIC_DIR / ".ssh_logins.state.json"
LOCK_FILE = METRIC_DIR / ".ssh_logins.lock"
LOCK_TIMEOUT_SEC = 3

logger = logging.getLogger("ssh_login_alert")
logger.addHandler(logging.handlers.SysLogHandler(address="/dev/log"))
logger.setLevel(logging.INFO)


def daemonize() -> None:
    if os.fork() > 0:
        os._exit(0)

    os.setsid()

    if os.fork() > 0:
        os._exit(0)

    devnull = os.open(os.devnull, os.O_RDWR)
    os.dup2(devnull, sys.stdin.fileno())
    os.dup2(devnull, sys.stdout.fileno())
    os.dup2(devnull, sys.stderr.fileno())


def update_metrics(user: str, rhost: str) -> None:
    if not METRIC_DIR.is_dir():
        logger.error("textfile_collector dir missing: %s", METRIC_DIR)
        return

    lock_fd = os.open(LOCK_FILE, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        deadline = time.monotonic() + LOCK_TIMEOUT_SEC
        while True:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    logger.warning(
                        "Could not acquire lock within %ss, skipping", LOCK_TIMEOUT_SEC
                    )
                    return
                time.sleep(0.05)

        state: dict[str, int] = {}
        if STATE_FILE.exists():
            try:
                state = json.loads(STATE_FILE.read_text())
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Corrupt state file, resetting: %s", e)
                state = {}

        key = f"{user}\t{rhost}"
        state[key] = state.get(key, 0) + 1

        tmp_state = STATE_FILE.with_suffix(".tmp")
        tmp_state.write_text(json.dumps(state))
        os.rename(tmp_state, STATE_FILE)

        lines = [
            "# HELP ssh_login_total Total successful SSH logins (session-phase pam_exec hook)",
            "# TYPE ssh_login_total counter",
        ]
        for k, count in state.items():
            u, r = k.split("\t", 1)
            lines.append(
                f"ssh_login_total{{user={json.dumps(u)},rhost={json.dumps(r)}}} {count}"
            )
        lines += [
            "# HELP ssh_login_last_timestamp_seconds Last successful SSH login timestamp",
            "# TYPE ssh_login_last_timestamp_seconds gauge",
            f"ssh_login_last_timestamp_seconds{{user={json.dumps(user)},rhost={json.dumps(rhost)}}} {int(time.time())}",
        ]

        tmp_metric = METRIC_FILE.with_suffix(".tmp")
        tmp_metric.write_text("\n".join(lines) + "\n")
        os.chmod(tmp_metric, 0o644)
        os.rename(tmp_metric, METRIC_FILE)

    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


def main() -> None:
    user = os.environ.get("PAM_USER", "unknown")
    rhost = os.environ.get("PAM_RHOST", "unknown")

    daemonize()

    try:
        update_metrics(user, rhost)
    except Exception:
        logger.exception("Unhandled error updating ssh_login metrics")


if __name__ == "__main__":
    main()
