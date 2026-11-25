"""Render the landing page to docs/ for GitHub Pages (static hosting, no backend).

    python scripts/build_pages.py

Console links (/issuer, /wallet, /customs) can't run on Pages, so they open the hosted demo. Settings > Pages > Deploy from branch > /docs.
"""
import pathlib
import re
import shutil

from jinja2 import Environment, FileSystemLoader

DEMO = "https://passage-demo.onrender.com"  # hosted app; see render.yaml
root = pathlib.Path(__file__).resolve().parent.parent
html = Environment(loader=FileSystemLoader(root / "templates")).get_template("index.html").render(
    request=type("R", (), {"url": type("U", (), {"path": "/"})()})()
)
html = re.sub(r'href="/(issuer|wallet|customs)"', rf'href="{DEMO}/\1" target="_blank" rel="noopener"', html)
html = html.replace('"/static/', '"static/').replace('href="/"', 'href="./"')

out = root / "docs"
shutil.copytree(root / "static", out / "static", dirs_exist_ok=True)
(out / "index.html").write_text(html, encoding="utf-8")
(out / ".nojekyll").touch()
print("wrote docs/index.html")
