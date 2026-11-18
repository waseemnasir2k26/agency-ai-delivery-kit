#!/usr/bin/env python3
"""Build: inject shared/footer.html into every page -> dist/<client>/<page>.html (gitignored). Usage: build.py [--root <folder>]"""
import sys
from pathlib import Path

ROOT = Path(sys.argv[sys.argv.index("--root") + 1]).resolve() if "--root" in sys.argv else Path(__file__).resolve().parent.parent
footer = (ROOT / "shared" / "footer.html").read_text(encoding="utf-8").strip()
for page in sorted((ROOT / "sites").glob("*/*.html")):
    out = ROOT / "dist" / page.parent.name / page.name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page.read_text(encoding="utf-8").replace("<!-- FOOTER -->", "<footer>%s</footer>" % footer), encoding="utf-8")
    print("built %s" % out.relative_to(ROOT).as_posix())
