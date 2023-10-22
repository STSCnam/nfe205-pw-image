from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Generator
from libs.database import ImageMeta, SearchEngine

__all__: list[str] = [
    "Class",
    "GTCatalog",
    "GTEngine",
]


@dataclass(frozen=True)
class Class(list):
    id: int
    name: str
    size: int = field(init=False)
    image_catalog: InitVar[list[str]]

    def __post_init__(self, image_catalog: list[str]) -> None:
        super().__init__(image_catalog)
        object.__setattr__(self, "size", len(self))


class GTCatalog:
    def __init__(self, class_file: Path, index_file: Path) -> None:
        self._class_catalog: list[str] = class_file.read_text("utf-8").split()
        self._index: list[list[str]] = [
            seq.split() for seq in index_file.read_text("utf-8").splitlines()
        ]

    def count(self) -> int:
        return len(self._class_catalog)

    def all(self) -> Generator[Class, None, None]:
        for id_, name in enumerate(self._class_catalog):
            yield Class(id=id_, name=name, image_catalog=self._index[id_])

    def get(self, class_name: str) -> Class | None:
        try:
            id_: int = self._class_catalog.index(class_name)
            return Class(id=id_, name=class_name, image_catalog=self._index[id_])
        except (IndexError, ValueError):
            return None


class GTEngine:
    def __init__(
        self,
        class_catalog_file: Path,
        class_index_file: Path,
        image_dir: Path,
        image_index_file: Path,
        desc_file: Path,
    ) -> None:
        self.db_engine: SearchEngine = SearchEngine(
            image_dir=image_dir, index_file=image_index_file, desc_file=desc_file
        )
        self.catalog: GTCatalog = GTCatalog(
            class_file=class_catalog_file, index_file=class_index_file
        )

    def compute_precision_recall(
        self, class_set: Class, n: int | None = None
    ) -> list[tuple[float, float]]:
        n = self.db_engine.image_db.count() if not n else n
        whole_result: list[ImageMeta] = self.db_engine.search(class_set[0], n)
        pr_seq: list[tuple[float, float]] = []

        for k in range(1, n + 1):
            k_result: list[ImageMeta] = whole_result[:k]
            tp: int = sum(1 for i in k_result if i.name in class_set)
            pr_seq.append((tp / len(k_result), tp / len(class_set)))

        return pr_seq
