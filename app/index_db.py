import enum
from pathlib import Path
from typing import Any
import typer
from libs.cli_utils import CLIUtils
from libs.index_writer import IndexWriter
from libs.database import ImageDatabase
from libs.descriptor import ColorDescriptor
from config import settings


class IndexMethod(enum.StrEnum):
    HIST_GREY: Any = "histgrey"
    HIST_RGB: Any = "histrgb"


class Main:
    def run(
        method: IndexMethod,
        xbins: int = 256,
        ybins: int = 256,
        zbins: int = 256,
    ) -> None:
        image_db: ImageDatabase = ImageDatabase(
            image_dir=settings.DATABASE_IMAGE_DIR,
            index_file=settings.DATABASE_IMAGE_INDEX_FILE,
        )
        bins_name: str = (
            str(xbins)
            if method is IndexMethod.HIST_GREY
            else f"{xbins}x{ybins}x{zbins}"
        )
        desc_file: Path = (
            settings.DATABASE_DESCRIPTOR_DIR
            / f"{settings.DATABASE_IMAGE_INDEX_FILE.stem}_{method.name}_{bins_name}"
        )
        writer: IndexWriter = IndexWriter(index_file=desc_file)

        with typer.progressbar(image_db.all(), length=image_db.count()) as progress:
            for image in progress:
                descriptor: ColorDescriptor = ColorDescriptor(image_file=image.path)
                f_vector: tuple[float, ...]

                if method is IndexMethod.HIST_GREY:
                    f_vector = descriptor.compute_gray_level_histogram(xbins)
                else:
                    f_vector = descriptor.compute_rgb_histogram(xbins, ybins, zbins)

                writer.append(f_vector)

        print(
            "Duration:",
            CLIUtils.get_readable_duration(
                progress.time_per_iteration, image_db.count()
            ),
        )


if __name__ == "__main__":
    typer.run(Main.run)
