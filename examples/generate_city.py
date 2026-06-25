"""Ví dụ: Tạo thành phố Minecraft"""

import sys
from pathlib import Path

# Thêm src vào path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_loader import ConfigLoader
from src.city_builder import CityBuilder
from src.schematic_generator import SchematiGenerator
from loguru import logger


def main():
    """Tạo thành phố Minecraft từ cấu hình"""

    logger.info("=== Minecraft City Generator ===")

    # Tải cấu hình
    config_loader = ConfigLoader()
    city_config = config_loader.load_config("configs/default_city.yaml")

    logger.info(f"City Config: {city_config}")

    # Lấy thông tin thành phố
    city_info = city_config.get("city", {})
    building_info = city_config.get("building", {})
    road_info = city_config.get("road", {})
    park_info = city_config.get("park", {})

    # Tạo city builder
    width = city_info.get("width", 256)
    height = city_info.get("height", 128)
    length = city_info.get("length", 256)

    logger.info(f"Creating city with size: {width}x{height}x{length}")

    city_builder = CityBuilder(width, height, length)

    # Tạo nền tảng
    logger.info("Creating foundation...")
    city_builder.create_foundation()

    # Tạo đường
    num_roads = city_info.get("num_roads", 8)
    road_width = road_info.get("width", 5)

    logger.info(f"Creating {num_roads} roads...")
    for i in range(num_roads):
        city_builder.add_road(f"Road_{i}", road_width)

    # Tạo tòa nhà
    num_buildings = city_info.get("num_buildings", 15)
    min_width = building_info.get("min_width", 15)
    max_width = building_info.get("max_width", 30)
    min_height = building_info.get("min_height", 20)
    max_height = building_info.get("max_height", 40)

    logger.info(f"Creating {num_buildings} buildings...")
    for i in range(num_buildings):
        city_builder.add_building(
            f"Building_{i}",
            min_width, max_width,
            min_height, max_height
        )

    # Tạo công viên
    num_parks = city_info.get("num_parks", 5)
    logger.info(f"Creating {num_parks} parks...")
    for i in range(num_parks):
        city_builder.add_park(f"Park_{i}")

    # Lưu schematic
    output_path = "output/minecraft_city.nbt"
    logger.info(f"Saving city to {output_path}...")
    city_builder.save(output_path)

    logger.info("✅ City created successfully!")
    logger.info(f"Output: {output_path}")


if __name__ == "__main__":
    main()
