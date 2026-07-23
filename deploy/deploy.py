import os
import base64
from pyinfra.operations import server 
from dotenv import load_dotenv
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

TSKEY_AUTH = os.getenv("TSKEY_AUTH")
if not TSKEY_AUTH:
    raise RuntimeError("TSKEY_AUTH env var is required")

LOCAL_VALUES_FILE = Path(ROOT_DIR) / "values.yaml"
LOCAL_ENV_FILE = Path(ROOT_DIR) / ".env"

if not LOCAL_VALUES_FILE.exists():
    raise RuntimeError("'values.yaml' was not found in root")


auth_string = base64.b64encode(f"x-access-token:{GITHUB_TOKEN}".encode()).decode()
auth_header = f"AUTHORIZATION: basic {auth_string}"
server.shell(
    name="Clone or update GitHub Repository",
    commands=[
        f"""
        set -e
        if [ -d {REMOTE_PROJECT_DIR}/.git ]; then
            echo "Updating repository..."
            cd {REMOTE_PROJECT_DIR}
            git -c http.extraheader="{auth_header}" pull
        else
            echo "Cloning repository..."
            git -c http.extraheader="{auth_header}" clone \
                https://github.com/kand1ss/{REMOTE_REPO_NAME}.git {REMOTE_PROJECT_DIR}
        fi
        """
    ],
)

server.shell(
    name="Install Python deps for render_env.py (if missing)",
    commands=[
        f"cd {REMOTE_PROJECT_DIR} && "
        "python3 -c 'import yaml, jinja2' 2>/dev/null || "
        "pip3 install --break-system-packages -r deploy/server-requirements.txt"
    ],
    _sudo=True,
)

server.shell(
    name="Render .env file from values.yaml on remote server",
    commands=[
        f"cd {REMOTE_PROJECT_DIR} && python3 deploy/shared/render_env.py"
    ],
)

server.shell(
    name="Docker Compose Pull & Up",
    commands=[
        f"cd {REMOTE_PROJECT_DIR} && docker compose pull",
        f"cd {REMOTE_PROJECT_DIR} && docker compose up -d --remove-orphans",
    ],
    _env={"TSKEY_AUTH": TSKEY_AUTH},
    _sudo=True,
)
