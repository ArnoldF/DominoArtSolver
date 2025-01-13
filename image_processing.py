
import cv2
import numpy as np


class ImageReader:
    _image: cv2.UMat
    _width: int
    _height: int

    def __init__(self, image_path: str):
        self._image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        if self._image is None:
            raise ValueError("Image not found or invalid image path.")

        self._height, self._width = self._image.shape

    @property
    def aspect_ratio(self) -> float:
        return self._width / self._height

    def get_field_brightness(self, grid_size: tuple[int, int]) -> np.ndarray:
        """
        Divide the image into the given number of fields and, for each field,
        compute the average brightness
        """
        # Compute field dimensions
        field_height = self._height // grid_size[0]
        field_width = self._width // grid_size[1]

        brightness_values = []

        for row in range(grid_size[0]):
            for col in range(grid_size[1]):
                start_y = row * field_height
                end_y = start_y + field_height

                start_x = col * field_width
                end_x = start_x + field_width

                field = self._image[start_y:end_y, start_x:end_x]
                average_brightness = np.mean(field)
                brightness_values.append(average_brightness)

        # Normalize brightness to 0-9
        brightness_values = np.array(brightness_values)
        normalized_brightness = 10 * (brightness_values - brightness_values.min()) / np.ptp(brightness_values + 1e-6) - 0.5
        brightness_image = normalized_brightness.reshape(grid_size)

        return brightness_image.tolist()
