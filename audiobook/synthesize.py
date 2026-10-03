"""Compatibility entry point; the audiobook engine is owned by book-skills."""

import os
import runpy
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
root = Path(os.environ.get("BOOK_SKILLS_ROOT", str(here.parent.parent / "book-skills")))
engine = root / ".github" / "skills" / "audiobook-from-markdown" / "reference" / "synthesize.py"
if not engine.is_file():
    raise SystemExit("Set BOOK_SKILLS_ROOT to your stop-cran/book-skills checkout. See audiobook/README.md.")
sys.path.insert(0, str(engine.parent))
sys.argv = [str(engine), "--project", str(here / "book.json"), *sys.argv[1:]]
runpy.run_path(str(engine), run_name="__main__")
