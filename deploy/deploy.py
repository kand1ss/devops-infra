import os
import base64
from pyinfra.operations import server, files
from dotenv import load_dotenv
from shared.render_env import render_yaml
from pathlib import Path

load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

REMOTE_REPO_NAME = os.getenv("REMOTE_REPO_NAME")
if not REMOTE_REPO_NAME:
    raise RuntimeError("REMOTE_REPO_NAME env var is required")

REMOTE_PROJECT_DIR = "/opt/infrastructure"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN env var is required")

LOCAL_VALUES_FILE = Path(ROOT_DIR) / "values.yaml"
LOCAL_ENV_FILE = Path(ROOT_DIR) / ".env"

if not LOCAL_VALUES_FILE.exists():
    raise RuntimeError("'values.yaml' was not found in root")

render_yaml(read_from=LOCAL_VALUES_FILE, save_to=LOCAL_ENV_FILE)

AUTH_STRING = base64.b64encode(f"x-access-token:{GITHUB_TOKEN}".encode()).decode()
AUTH_HEADER = f"AUTHORIZATION: basic {AUTH_STRING}"
server.shell(
    name="Clone or update GitHub Repository",
    commands=[
        f"""
        set -e
        if [ -d {REMOTE_PROJECT_DIR}/.git ]; then
            echo "Updating repository..."
            cd {REMOTE_PROJECT_DIR}
            git -c http.extraheader="{AUTH_HEADER}" pull
        else
            echo "Cloning repository..."
            git -c http.extraheader="{AUTH_HEADER}" clone \
                https://github.com/kand1ss/{REMOTE_REPO_NAME}.git {REMOTE_PROJECT_DIR}
        fi
        """
    ],
    _sudo=True,
)

files.put(
    name="Deliver rendered .env",
    src=str(LOCAL_ENV_FILE),
    dest=f"{REMOTE_PROJECT_DIR}/.env",
    mode="600",
    _sudo=True,
)

LOCAL_SECRETS_DIR = os.path.join(ROOT_DIR, "secrets")
if not os.path.isdir(LOCAL_SECRETS_DIR):
    raise RuntimeError("'secrets' directory was not found in root")

files.sync(
    name="Deliver secrets",
    src=LOCAL_SECRETS_DIR,
    dest=f"{REMOTE_PROJECT_DIR}/secrets/",
    mode="600",
    _sudo=True,
)

server.shell(
    name="Run project",
    commands=[f"cd {REMOTE_PROJECT_DIR} && docker compose up -d --build"],
    _sudo=True,
)


server.shell(
    name="Reset and apply Tailscale serve rule",
    commands=[
        "tailscale serve reset",
        "tailscale serve --bg --https=443 --set-path=/grafana http://127.0.0.1:3000",
    ],
    _sudo=True,
)
