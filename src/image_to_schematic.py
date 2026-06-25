"""Image to Schematic - Chuyển đổi ảnh thành schematic"""

from PIL import Image
import numpy as np
from typing import Dict, Tuple, List
from loguru import logger
from src.schematic_generator import SchematiGenerator


class ImageToSchematic:
    """Chuyển đổi ảnh thành Minecraft schematic"""

    # Bảng màu Minecraft (RGB)
    MINECRAFT_COLORS = {
        "white": (255, 255, 255),
        "light_gray": (192, 192, 192),
        "gray": (128, 128, 128),
        "black": (0, 0, 0),
        "brown": (139, 69, 19),
        "red": (255, 0, 0),
        "orange": (255, 165, 0),
        "yellow": (255, 255, 0),
        "lime": (0, 255, 0),
        "green": (0, 128, 0),
        "cyan": (0, 255, 255),
        "light_blue": (173, 216, 230),
        "blue": (0, 0, 255),
        "purple": (128, 0, 128),
        "magenta": (255, 0, 255),
        "pink": (255, 192, 203),
    }

    BLOCK_MAPPING = {
        (255, 255, 255): "white_concrete",
        (192, 192, 192): "light_gray_concrete",
        (128, 128, 128): "gray_concrete",
        (0, 0, 0): "black_concrete",
        (139, 69, 19): "brown_concrete",
        (255, 0, 0): "red_concrete",
        (255, 165, 0): "orange_concrete",
        (255, 255, 0): "yellow_concrete",
        (0, 255, 0): "lime_concrete",
        (0, 128, 0): "green_concrete",
        (0, 255, 255): "cyan_concrete",
        (173, 216, 230): "light_blue_concrete",
        (0, 0, 255): "blue_concrete",
        (128, 0, 128): "purple_concrete",
        (255, 0, 255): "magenta_concrete",
        (255, 192, 203): "pink_concrete",
    }

    def __init__(self, width: int = 256, height: int = 128, length: int = 256):
        """Khởi tạo Image to Schematic

        Args:
            width: Chiều rộng schematic
            height: Chiều cao schematic
            length: Chiều dài schematic
        """
        self.width = width
        self.height = height
        self.length = length
        self.generator = SchematiGenerator(width, height, length)
        logger.info("ImageToSchematic initialized")

    def load_image(self, image_path: str) -> Image.Image:
        """Tải ảnh từ file

        Args:
            image_path: Đường dẫn ảnh

        Returns:
            PIL Image object
        """
        try:
            image = Image.open(image_path)
            logger.info(f"Image loaded: {image_path} ({image.size})")
            return image
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            raise

    def find_nearest_color(self, rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Tìm màu Minecraft gần nhất

        Args:
            rgb: Màu RGB cần tìm

        Returns:
            Màu RGB gần nhất từ MINECRAFT_COLORS
        """
        r, g, b = rgb[:3]
        min_distance = float('inf')
        nearest_color = (255, 255, 255)

        for color_rgb in self.BLOCK_MAPPING.keys():
            cr, cg, cb = color_rgb
            distance = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
            if distance < min_distance:
                min_distance = distance
                nearest_color = color_rgb

        return nearest_color

    def convert_image_to_schematic(self, image_path: str, scale: float = 1.0,
                                  height_offset: int = 64) -> Dict:
        """Chuyển đổi ảnh thành schematic

        Args:
            image_path: Đường dẫn ảnh
            scale: Tỷ lệ phóng to (0.5 = nhỏ hơn, 2.0 = lớn hơn)
            height_offset: Độ cao bắt đầu

        Returns:
            Thông tin về schematic được tạo
        """
        # Tải ảnh
        image = self.load_image(image_path)

        # Chuyển đổi sang RGB nếu cần
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize ảnh theo tỷ lệ
        new_width = int(image.width * scale)
        new_height = int(image.height * scale)

        # Đảm bảo ảnh không vượt quá kích thước schematic
        new_width = min(new_width, self.width - 10)
        new_height = min(new_height, self.length - 10)

        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.info(f"Image resized to {new_width}x{new_height}")

        # Chuyển đổi ảnh thành mảng numpy
        image_array = np.array(image)

        # Vẽ ảnh lên schematic
        start_x = (self.width - new_width) // 2
        start_z = (self.length - new_height) // 2

        for y, row in enumerate(image_array):
            for x, pixel in enumerate(row):
                # Tìm màu Minecraft gần nhất
                nearest_color = self.find_nearest_color(pixel)
                block = self.BLOCK_MAPPING.get(nearest_color, "white_concrete")

                # Đặt block
                world_x = start_x + x
                world_z = start_z + y
                world_y = height_offset

                self.generator.set_block(world_x, world_y, world_z, block)

        logger.info(f"Image converted to schematic successfully")

        return {
            "original_size": (image.width, image.height),
            "schematic_size": (new_width, new_height),
            "height_offset": height_offset,
            "blocks_used": new_width * new_height
        }

    def create_3d_relief(self, image_path: str, scale: float = 1.0,
                        max_height: int = 20, height_offset: int = 64) -> Dict:
        """Tạo relief 3D từ ảnh (độ sáng = độ cao)

        Args:
            image_path: Đường dẫn ảnh
            scale: Tỷ lệ phóng to
            max_height: Chiều cao tối đa của relief
            height_offset: Độ cao bắt đầu

        Returns:
            Thông tin về schematic được tạo
        """
        # Tải ảnh
        image = self.load_image(image_path)

        # Chuyển sang grayscale để tính độ sáng
        if image.mode != 'L':
            image = image.convert('L')

        # Resize ảnh
        new_width = int(image.width * scale)
        new_height = int(image.height * scale)
        new_width = min(new_width, self.width - 10)
        new_height = min(new_height, self.length - 10)

        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.info(f"Image resized to {new_width}x{new_height}")

        # Chuyển đổi thành mảng numpy
        image_array = np.array(image)

        # Normalize độ sáng (0-255) thành độ cao (0-max_height)
        height_map = (image_array / 255.0) * max_height

        start_x = (self.width - new_width) // 2
        start_z = (self.length - new_height) // 2

        blocks_used = 0

        # Vẽ relief
        for y, row in enumerate(height_map):
            for x, brightness in enumerate(row):
                height = int(brightness)
                world_x = start_x + x
                world_z = start_z + y

                # Xây dựng cột từ dưới lên
                for h in range(height):
                    world_y = height_offset + h
                    if world_y < height_offset + max_height:
                        self.generator.set_block(world_x, world_y, world_z, "stone")
                        blocks_used += 1

        logger.info(f"3D relief created with {blocks_used} blocks")

        return {
            "original_size": (image.width, image.height),
            "relief_size": (new_width, new_height),
            "max_height": max_height,
            "height_offset": height_offset,
            "blocks_used": blocks_used
        }

    def save_schematic(self, filepath: str, name: str = "From Image") -> None:
        """Lưu schematic

        Args:
            filepath: Đường dẫn lưu
            name: Tên schematic
        """
        metadata = {
            "Name": name,
            "Author": "ImageToSchematic",
        }
        self.generator.save(filepath, metadata)
        logger.info(f"Schematic saved to {filepath}")
