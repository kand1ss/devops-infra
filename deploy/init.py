import os
from pathlib import Path

from dotenv import load_dotenv
from pyinfra.operations import files, server

load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
NEW_USER = os.getenv("NEW_USER", "default")

REMOTE_PROJECT_DIR = "/opt/infrastructure"
REMOTE_REPO_NAME = os.getenv("REMOTE_REPO_NAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not REMOTE_REPO_NAME or not GITHUB_TOKEN:
    raise RuntimeError("REMOTE_REPO_NAME and GITHUB_TOKEN env vars are required")

LOCAL_SECRETS_DIR = Path(ROOT_DIR) / "secrets"
if not LOCAL_SECRETS_DIR.is_dir():
    raise RuntimeError("'secrets' directory was not found locally")

server.shell(
    name="Create project directory and set permissions",
    commands=[
        f"mkdir -p {REMOTE_PROJECT_DIR}",
        f"chown -R {NEW_USER}:{NEW_USER} {REMOTE_PROJECT_DIR}",
    ],
    _sudo=True,
)

files.sync(
    name="Deliver secrets directory to remote",
    src=str(LOCAL_SECRETS_DIR),
    dest=f"{REMOTE_PROJECT_DIR}/secrets/",
    mode="600",
    delete=True,
)
