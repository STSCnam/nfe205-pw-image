from pathlib import Path
from pprint import pp
from typing import Annotated, Optional
import typer
from libs.database import ImageMeta, SearchEngine
from config import settings
from libs.ground_truth import Class, GTCatalog


class Main:
    def run(
        name: str,
        desc_file: Annotated[Path, typer.Option()],
        k: Annotated[int, typer.Option()] = 10,
        class_name: Annotated[Optional[str], typer.Option()] = None,
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
        precision_pct: float = 0.0

        if class_name:
            gt_catalog: GTCatalog = GTCatalog(
                class_file=settings.DATABASE_GT_CLASS_CATALOG_FILE,
                index_file=settings.DATABASE_GT_CLASS_INDEX_FILE,
            )

            if class_meta := gt_catalog.get(class_name):
                precision_pct = Main.get_precision_pct(result, class_meta)

        Main.save(result, precision_pct, output_file)

    def get_precision_pct(result: list[ImageMeta], class_meta: Class) -> float:
        tp: int = sum(1 for image in result if image.name in class_meta)
        return tp / len(result) * 100

    def save(result: list[ImageMeta], precision_pct: float, output_file: Path) -> None:
        content: str = ""

        for image_meta in result:
            content += (
                f"<div>"
                f'<img src="{image_meta.path.resolve()}" alt="distance">'
                f"<p>{image_meta.name} - {image_meta.score:.6f}</p>"
                f"</div>"
            )

        content = (
            f"<body><div>Precision: {precision_pct:.2f}%</div>"
            f'<div style="display: flex;flex-direction: row;flex-wrap: wrap;">'
            f"{content}</div></body>"
        )
        output_file.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    typer.run(Main.run)
