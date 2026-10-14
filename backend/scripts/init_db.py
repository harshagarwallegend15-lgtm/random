"""Apply all models' metadata to the database. Useful for dev / first-time setup.

Run:  python -m scripts.init_db
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import Base, engine
import app.models  # noqa: F401


def main() -> None:
    print("Creating tables on", engine.url)
    Base.metadata.create_all(bind=engine)
    print("Done.")


if __name__ == "__main__":
    main()
