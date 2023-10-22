from pathlib import Path
from pprint import pp
from typing import Annotated, Optional
import typer
from libs.database import ImageMeta, SearchEngine
from config import settings


class Main:
    def run(
        name: str,
        desc_file: Annotated[Path, typer.Option()],
        k: Annotated[int, typer.Option()] = 10,
    ) -> None:
        output_file: Path = (
            settings.SEARCH_DIR / f"{desc_file.name}_{name.split('.')[0]}_{k}.html"
        )
        searcher: SearchEngine = SearchEngine(
            image_dir=settings.DATABASE_IMAGE_DIR,
            index_file=settings.DATABASE_IMAGE_INDEX_FILE,
            desc_file=desc_file,
        )
        result: list[ImageMeta] = searcher.search(image_name=name, k=k)
        Main.save(result, output_file)

    def save(result: list[ImageMeta], output_file: Path) -> None:
        content: str = ""

        for image_meta in result:
            content += (
                f"<div>"
                f'<img src="{image_meta.path.resolve()}" alt="distance">'
                f"<p>{image_meta.name} - {image_meta.score:.6f}</p>"
                f"</div>"
            )

        content = f'<body style="display: flex;flex-direction: row;flex-wrap: wrap;">{content}</body>'
        output_file.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    typer.run(Main.run)
