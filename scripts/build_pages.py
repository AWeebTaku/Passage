"""Render the landing page to docs/ for GitHub Pages (static hosting, no backend).

    python scripts/build_pages.py

Console links (/issuer, /wallet, /customs) can't work on Pages, so they point
at the repo's run instructions instead. Settings > Pages > Deploy from branch > /docs.
"""
import pathlib
import re
import shutil

from jinja2 import Environment, FileSystemLoader

REPO = "https://github.com/AWeebTaku/Passage"
root = pathlib.Path(__file__).resolve().parent.parent
html = Environment(loader=FileSystemLoader(root / "templates")).get_template("index.html").render(
    request=type("R", (), {"url": type("U", (), {"path": "/"})()})()
)
html = re.sub(r'href="/(issuer|wallet|customs)"', f'href="{REPO}#4-run-the-backend"', html)
html = html.replace('"/static/', '"static/').replace('href="/"', 'href="./"')
html = html.replace("Try the demo", "Run it locally")

out = root / "docs"
shutil.copytree(root / "static", out / "static", dirs_exist_ok=True)
(out / "index.html").write_text(html, encoding="utf-8")
(out / ".nojekyll").touch()
print("wrote docs/index.html")
