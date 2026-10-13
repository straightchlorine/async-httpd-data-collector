"""Sets page.meta["lastmod"] to the date of the last git commit that touched the page source.

The sitemap uses it as <lastmod>. With a shallow checkout (every file would get the
newest commit date) it stays empty, so the sitemap has no lastmod instead of a wrong one.
"""

import functools
import os
import subprocess


def _git(root, *args):
    out = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else ""


@functools.lru_cache(maxsize=None)
def _lastmod(root, path):
    if _git(root, "rev-parse", "--is-shallow-repository") != "false":
        return ""
    return _git(root, "log", "-1", "--format=%cs", "--", path)


def on_page_markdown(markdown, page, config, files):
    # not on_page_context: mkdocs renders sitemap.xml before that event
    root = os.path.dirname(os.path.abspath(config.config_file_path))
    rel = os.path.relpath(os.path.join(config.docs_dir, page.file.src_path), root)
    page.meta["lastmod"] = _lastmod(root, rel)
    return markdown
