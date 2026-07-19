import os
from pyinfra.operations import server, files
from dotenv import load_dotenv

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


server.shell(
    name="Clone GitHub Repository",
    commands=[
        f"""
        if [ -d {REMOTE_PROJECT_DIR}/.git ]; then
            echo "Updating repository..."
            cd {REMOTE_PROJECT_DIR} && git pull
        else
            echo "Cloning repository..."
            git clone https://{GITHUB_TOKEN}@github.com/kand1ss/{REMOTE_REPO_NAME}.git {REMOTE_PROJECT_DIR}
            cd {REMOTE_PROJECT_DIR} && git remote set-url origin https://github.com/kand1ss/{REMOTE_REPO_NAME}.git
        fi
        """
    ],
)

LOCAL_SECRETS_FILE = os.path.join(ROOT_DIR, "secrets")
if os.path.exists(LOCAL_SECRETS_FILE):
    files.put(
        name="Deliver secrets",
        src=LOCAL_SECRETS_FILE,
        dest=REMOTE_PROJECT_DIR,
        mode="600",
    )
else:
    raise RuntimeError("'secrets' directory was not found in root")

server.shell(
    name="Run project",
    commands=[f"cd {REMOTE_PROJECT_DIR} && docker compose up -d --build"],
    _sudo=True,
)
