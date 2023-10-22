from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Generator

from libs.descriptor import DescriptorReader

__all__: list[str] = [
    "ImageMeta",
    "ImageDatabase",
    "SearchEngine",
]


@dataclass
class ImageMeta:
    id: int
    name: str
    path: Path
    score: float | None = None

    def __lt__(self, other: ImageMeta) -> bool:
        return self.score < other.score


class ImageDatabase:
    def __init__(self, image_dir: Path, index_file: Path) -> None:
        self._image_dir: Path = image_dir
        self._index: list[str] = index_file.read_text("utf-8").split()

    def count(self) -> int:
        return len(self._index)

    def all(self) -> Generator[ImageMeta, None, None]:
        for id_, name in enumerate(self._index):
            yield ImageMeta(id=id_, name=name, path=self._image_dir / name)

    def get_by_id(self, id_: int) -> ImageMeta | None:
        try:
            name: str = self._index[id_]
            return ImageMeta(id=id_, name=name, path=self._image_dir / name)
        except IndexError:
            return None

    def get_by_name(self, image_name: str) -> ImageMeta | None:
        try:
            id_: int = self._index.index(image_name)
            return ImageMeta(id=id_, name=image_name, path=self._image_dir / image_name)
        except ValueError:
            return None


class SearchEngine:
    def __init__(self, image_dir: Path, index_file: Path, desc_file: Path) -> None:
        self.image_db: ImageDatabase = ImageDatabase(image_dir, index_file)
        self._desc_reader: DescriptorReader = DescriptorReader(desc_file)

    def search(self, image_name: str, k: int | None = None) -> list[ImageMeta]:
        k = self.image_db.count() if k is None else k
        result: list[ImageMeta] = []
        target: ImageMeta | None = self.image_db.get_by_name(image_name)

        if target:
            t_vector: tuple[float, ...] = self._desc_reader[target.id]

            for browsed in self.image_db.all():
                b_vector: tuple[float, ...] = self._desc_reader[browsed.id]
                browsed.score = self._esim(t_vector, b_vector)
                result.append(browsed)

        result.sort()
        return result[:k]

    def _esim(self, x: tuple[float, ...], y: tuple[float, ...]) -> float:
        return sum((xi - yi) ** 2 for xi, yi in zip(x, y)) ** 0.5
