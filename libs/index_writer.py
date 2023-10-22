from pathlib import Path

__all__: list[str] = [
    "IndexWriter",
]


class IndexWriter:
    def __init__(self, index_file: Path, *, sep: str = " ") -> None:
        self._index_file: Path = index_file
        self._sep: str = sep
        self._clean_index()

    def _clean_index(self) -> None:
        if self._index_file.exists():
            self._index_file.unlink()

    def append(self, vector: tuple[float, ...]) -> None:
        with self._index_file.open("a", encoding="utf-8") as fd:
            fd.write(self._sep.join(map(str, vector)) + "\n")
