"""Stress seed: insert 1000 templates into the DB to test frontend performance.

All rows share the same physical image file (via symlinks). Run from the
backend root directory:

    uv run python tests/stress/seed_templates.py

To remove the seeded data afterwards:

    uv run python tests/stress/seed_templates.py --cleanup
"""

import argparse
import shutil
import sys
from pathlib import Path

# Ensure src/ is importable when run from backend root.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.db.database import SessionLocal, ensure_data_dir  # noqa: E402
from src.models.template import Template  # noqa: E402

TEMPLATES_DIR = Path("data/templates")
BASE_FILENAME = "stress_base.jpg"
SOURCE_IMAGE = Path(__file__).parent / "template.jpg"
COUNT = 1000

KEYWORD_POOL = [
    "reaction",
    "funny",
    "classic",
    "trending",
    "animal",
    "movie",
    "tv",
    "sport",
    "politics",
    "wholesome",
    "dark",
    "surreal",
    "vintage",
    "relatable",
    "cringe",
    "epic",
    "fail",
    "win",
    "dank",
    "based",
]

NAMES = [
    "Distracted Boyfriend",
    "Drake Approves",
    "This Is Fine",
    "Surprised Pikachu",
    "Change My Mind",
    "Two Buttons",
    "Galaxy Brain",
    "Expanding Brain",
    "Buff Doge",
    "Woman Yelling at Cat",
    "Bernie Sanders",
    "Gru's Plan",
    "Panik Kalm",
    "Always Has Been",
    "Stonks",
    "Uno Reverse",
    "Hide the Pain Harold",
    "Leonardo DiCaprio",
    "The Rock Driving",
    "Evil Kermit",
]


def _symlink_filename(i: int) -> str:
    return f"stress_{i:04d}.jpg"


def seed(db) -> None:
    ensure_data_dir()
    base_path = TEMPLATES_DIR / BASE_FILENAME

    # Copy the source image once.
    shutil.copy2(SOURCE_IMAGE, base_path)

    inserted = 0
    for i in range(1, COUNT + 1):
        filename = _symlink_filename(i)
        link = TEMPLATES_DIR / filename

        # Create a symlink to the base image (skip if it already exists).
        if not link.exists() and not link.is_symlink():
            link.symlink_to(BASE_FILENAME)

        name_base = NAMES[(i - 1) % len(NAMES)]
        name = f"{name_base} #{i}"

        # Pick 2–4 varied keywords from the pool.
        kw_indices = [(i + j) % len(KEYWORD_POOL) for j in range(2 + (i % 3))]
        keywords = ",".join(KEYWORD_POOL[k] for k in kw_indices)

        template = Template(name=name, filename=filename, keywords=keywords)
        db.add(template)
        inserted += 1

    db.commit()
    print(f"Inserted {inserted} stress templates.")


def cleanup(db) -> None:
    deleted = db.query(Template).filter(Template.filename.like("stress_%")).delete(
        synchronize_session=False
    )
    db.commit()

    # Remove symlinks and base file.
    for i in range(1, COUNT + 1):
        link = TEMPLATES_DIR / _symlink_filename(i)
        if link.is_symlink() or link.exists():
            link.unlink(missing_ok=True)

    base_path = TEMPLATES_DIR / BASE_FILENAME
    base_path.unlink(missing_ok=True)

    print(f"Removed {deleted} stress templates and associated files.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Stress-seed the templates table.")
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove previously seeded stress templates instead of inserting.",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.cleanup:
            cleanup(db)
        else:
            seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
