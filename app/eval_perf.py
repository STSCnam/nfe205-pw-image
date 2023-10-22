from pathlib import Path
from typing import Annotated, Optional
import typer
from config import settings
from libs.cli_utils import CLIUtils
from libs.ground_truth import Class, GTEngine
from libs.index_writer import IndexWriter


class Main:
    def run(
        desc_file: Path, class_name: Annotated[Optional[str], typer.Option()] = None
    ) -> None:
        gt: GTEngine = GTEngine(
            class_catalog_file=settings.DATABASE_GT_CLASS_CATALOG_FILE,
            class_index_file=settings.DATABASE_GT_CLASS_INDEX_FILE,
            image_dir=settings.DATABASE_IMAGE_DIR,
            image_index_file=settings.DATABASE_IMAGE_INDEX_FILE,
            desc_file=desc_file,
        )
        n: int = gt.db_engine.image_db.count()
        classes: list[Class]

        if class_meta := gt.catalog.get(class_name):
            classes = [class_meta]
        else:
            classes = list(gt.catalog.all())

        output_file: Path = (
            settings.PR_DIR / f"{desc_file.name}_{n}_"
            f"{'all' if len(classes) > 1 else classes[0].name}.txt"
        )

        with typer.progressbar(classes, length=len(classes)) as progress:
            global_result: list[tuple[float, float]] = []

            for class_meta in progress:
                global_result = Main.merge_pr(
                    global_result,
                    gt.compute_precision_recall(class_set=class_meta, n=n),
                )

            global_result = Main.compute_means(global_result, len(classes))
            Main.save(global_result, output_file)

        print(
            "Duration:",
            CLIUtils.get_readable_duration(progress.time_per_iteration, len(classes)),
        )

    def merge_pr(
        source: list[tuple[float, float]], new: list[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        if not source:
            return new

        for i in range(len(source)):
            p1, r1 = source[i]
            p2, r2 = new[i]
            source[i] = p1 + p2, r1 + r2

        return source

    def compute_means(
        result: list[tuple[float, float]], class_len: int
    ) -> list[tuple[float, float]]:
        for i in range(len(result)):
            p, r = result[i]
            result[i] = p / class_len, r / class_len

        return result

    def compute_f1_score(
        result: list[tuple[float, float]]
    ) -> list[tuple[float, float, float]]:
        for i in range(len(result)):
            p, r = result[i]
            result[i] = p, r, 2 * ((p * r) / p + r)

        return result

    def save(result: list[tuple[float, float]], output_file: Path) -> None:
        writer: IndexWriter = IndexWriter(output_file)

        for pr in result:
            writer.append(pr)


if __name__ == "__main__":
    typer.run(Main.run)
