import yaml
from jinja2 import Template
from pathlib import Path

def render_yaml(read_from: Path, save_to: Path):
    values = yaml.safe_load(read_from.read_text())
    env_template = Template("""
        DOMAIN={{ domain }}
        CERTBOT_EMAIL={{ certbot_email }}
        SHORTENER_DB_USER={{ shortener.db.user }}
        SHORTENER_DB_NAME={{ shortener.db.name }}
    """)
    _ = save_to.write_text(env_template.render(**values))
