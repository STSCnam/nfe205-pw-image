from pathlib import Path
from PIL import Image, PyAccess
from PIL.Image import Image as ImageType

__all__: list[str] = [
    "ColorDescriptor",
    "DescriptorReader",
]


class ColorDescriptor:
    def __init__(self, image_file: Path) -> None:
        self._image: ImageType = Image.open(image_file)

    def compute_gray_level_histogram(self, bins: int = 256) -> tuple[float, ...]:
        """Compute the gray level histogram of the image.
        As the color has a single axis, we can use it as the index of the frequency vector.

        Note:
            The size of the frequency vector equals the bins number.
            Each point of the frequency vector is a float64.

        Args:
            bins (Optional): The bins number to reduce the vector size.
                Default to 256 (max).

        Returns:
            tuple[float, ...]: The color frequency vector.
        """

        gray_frequency: list[int] = [0] * bins
        self._image = self._image.convert("L")
        pixels: PyAccess = self._image.load()
        width, height = self._image.size

        for y in range(width * height):
            x, y = y % width, y // width
            # Normalize color axis according to the bins and using it as the color index
            color_index: int = (bins * pixels[x, y]) // 256
            gray_frequency[color_index] += 1

        return tuple(map(lambda f: f / (width * height), gray_frequency))

    def compute_rgb_histogram(
        self,
        r_bins: int = 256,
        g_bins: int = 256,
        b_bins: int = 256,
    ) -> tuple[float, ...]:
        """Compute the RGB histogram of the image.
        To flatten the cubic RGB space into a single dimension we use the linear formula
        `z(ay + b) + c` so we can compute the color index of the frequency vector.

        Note:
            The size of the frequency vector equals the product of the 3 bins axis.
            Each point of the frequency vector is a float64.

        Args:
            r_bins (Optional): The bins number of the R axis to reduce the vector size.
                Default to 256 (max).
            g_bins (Optional): The bins number of the G axis to reduce the vector size.
                Default to 256 (max).
            b_bins (Optional): The bins number of the B axis to reduce the vector size.
                Default to 256 (max).

        Returns:
            tuple[float, ...]: The color frequency vector.
        """

        rgb_frequency: list[int] = [0] * r_bins * g_bins * b_bins
        self._image = self._image.convert("RGB")
        pixels: PyAccess = self._image.load()
        width, height = self._image.size

        for y in range(width * height):
            x, y = y % width, y // width
            r, g, b = pixels[x, y]
            # Normalize color axes according to the bins
            r, g, b = (r_bins * r) // 256, (g_bins * g) // 256, (b_bins * b) // 256
            # Compute the color index
            color_index = (r * g_bins + g) * b_bins + b
            rgb_frequency[color_index] += 1

        return tuple(map(lambda f: f / (width * height), rgb_frequency))


class DescriptorReader(list):
    def __init__(self, desc_file: Path) -> None:
        super().__init__(
            [
                tuple(map(float, v.split()))
                for v in desc_file.read_text("utf-8").splitlines()
            ]
        )
