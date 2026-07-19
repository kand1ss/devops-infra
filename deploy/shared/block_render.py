import os
from pyinfra.operations import files

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


def render_managed_block(
    dest: str,
    block_name: str,
    content: str,
):
    begin_marker = f"# BEGIN pyinfra-managed: {block_name}"
    end_marker = f"# END pyinfra-managed: {block_name}"

    block_text = f"{begin_marker}\n{content.strip()}\n{end_marker}"

    files.block(
        name=f"Managed block '{block_name}' in {dest}",
        path=dest,
        content=block_text,
        marker=f"# {{mark}} pyinfra-managed: {block_name}",
        present=True,
    )
