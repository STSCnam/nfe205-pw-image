import os
from pathlib import Path
from typing import Final

DATABASE_IMAGE_DIR: Final[Path] = Path(os.environ["DATABASE_IMAGE_DIR"])
DATABASE_IMAGE_INDEX_FILE: Final[Path] = Path(os.environ["DATABASE_IMAGE_INDEX_FILE"])
DATABASE_GT_CLASS_CATALOG_FILE: Final[Path] = Path(
    os.environ["DATABASE_GT_CLASS_INDEX_FILE"]
)
DATABASE_GT_CLASS_INDEX_FILE: Final[Path] = Path(
    os.environ["DATABASE_GT_CLASS_IMAGE_INDEX_FILE"]
)
DATABASE_DESCRIPTOR_DIR: Final[Path] = Path(os.environ["DATABASE_DESCRIPTOR_DIR"])
PR_DIR: Final[Path] = Path(os.environ["PR_DIR"])
SEARCH_DIR: Final[Path] = Path(os.environ["SEARCH_DIR"])
