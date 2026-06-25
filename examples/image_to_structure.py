"""Ví dụ: Chuyển đổi ảnh thành cấu trúc Minecraft"""

import sys
from pathlib import Path

# Thêm src vào path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.image_to_schematic import ImageToSchematic
from loguru import logger


def main():
    """Chuyển đổi ảnh thành schematic Minecraft"""

    logger.info("=== Image to Minecraft Structure ===")

    # Khởi tạo converter
    converter = ImageToSchematic(width=256, height=128, length=256)

    # Ví dụ 1: Chuyển đổi ảnh thông thường
    logger.info("\n--- Example 1: Convert image to structure ---")

    image_path = "examples/sample_image.png"  # Thay bằng ảnh thực tế

    # Kiểm tra file ảnh
    if Path(image_path).exists():
        result = converter.convert_image_to_schematic(
            image_path,
            scale=1.0,
            height_offset=64
        )

        logger.info(f"Result: {result}")
        converter.save_schematic("output/image_structure.nbt", "From Image")
    else:
        logger.warning(f"Image not found: {image_path}")
        logger.info("Please provide a valid image file")

    # Ví dụ 2: Tạo relief 3D từ ảnh
    logger.info("\n--- Example 2: Create 3D relief from image ---")

    if Path(image_path).exists():
        result = converter.create_3d_relief(
            image_path,
            scale=0.5,
            max_height=20,
            height_offset=64
        )

        logger.info(f"Relief created: {result}")
        converter.save_schematic("output/image_relief.nbt", "3D Relief")
    else:
        logger.warning(f"Image not found: {image_path}")

    logger.info("\n✅ Image conversion examples completed!")


if __name__ == "__main__":
    main()
