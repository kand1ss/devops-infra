import sys
from pathlib import Path

import yaml
from jinja2 import Template


def render_yaml(read_from: Path, save_to: Path):
    values = yaml.safe_load(read_from.read_text())
    env_template = Template("""
DOMAIN={{ domain }}
CERTBOT_EMAIL={{ certbot_email }}
SHORTENER_IMAGE_TAG={{ shortener.image_tag }}
SHORTENER_DB_USER={{ shortener.db.user }}
SHORTENER_DB_NAME={{ shortener.db.name }}
    """)
    _ = save_to.write_text(env_template.render(**values))


if __name__ == "__main__":
    SCRIPT_DIR = Path(__file__).resolve().parent
    ROOT_DIR = SCRIPT_DIR.parent.parent

    values_path = ROOT_DIR / "values.yaml"
    env_path = ROOT_DIR / ".env"

    if not values_path.exists():
        print(f"Error: {values_path} not found!")
        sys.exit(1)

    render_yaml(read_from=values_path, save_to=env_path)
