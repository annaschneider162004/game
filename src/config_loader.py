"""Config Loader - Nạp cấu hình từ file YAML"""

import yaml
from typing import Dict, Any
from pathlib import Path
from loguru import logger


class ConfigLoader:
    """Load cấu hình thành phố và nhân vật"""

    def __init__(self, config_dir: str = "configs"):
        """Khởi tạo Config Loader

        Args:
            config_dir: Thư mục chứa file cấu hình
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        logger.info(f"ConfigLoader initialized with directory: {config_dir}")

    def load_config(self, filename: str) -> Dict[str, Any]:
        """Load cấu hình từ file

        Args:
            filename: Tên file cấu hình

        Returns:
            Dictionary cấu hình
        """
        filepath = self.config_dir / filename

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Config loaded from {filename}")
            return config if config else {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {filepath}")
            return {}
        except Exception as e:
            logger.error(f"Error loading config {filename}: {e}")
            return {}

    def save_config(self, config: Dict[str, Any], filename: str) -> None:
        """Lưu cấu hình vào file

        Args:
            config: Dictionary cấu hình
            filename: Tên file
        """
        filepath = self.config_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            logger.info(f"Config saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving config {filename}: {e}")
            raise

    def create_default_configs(self) -> None:
        """Tạo các file cấu hình mặc định"""
        # Cấu hình thành phố
        city_config = {
            "city": {
                "name": "Minecraft City",
                "width": 256,
                "height": 128,
                "length": 256,
                "num_buildings": 15,
                "num_roads": 8,
                "num_parks": 5,
            },
            "building": {
                "min_width": 15,
                "max_width": 30,
                "min_height": 20,
                "max_height": 40,
                "min_depth": 15,
                "max_depth": 30,
                "types": ["residential", "commercial", "industrial"],
            },
            "road": {
                "width": 5,
                "material": "stone",
                "edge_material": "gravel",
            },
            "park": {
                "min_width": 40,
                "max_width": 80,
                "min_length": 40,
                "max_length": 80,
                "tree_density": 0.02,
            },
        }

        # Cấu hình nhân vật
        character_config = {
            "workers": {
                "num_workers": 5,
                "names": [
                    "Alex", "Steve", "Notch", "Herobrine", "Creeper",
                    "Enderman", "Skeleton", "Zombie", "Witch", "Wither",
                ],
                "skill_levels": {
                    "min": 1,
                    "max": 10,
                    "average": 5,
                },
                "speed": {
                    "min": 0.8,
                    "max": 1.2,
                    "default": 1.0,
                },
            },
            "tasks": {
                "blocks_per_tick": 10,
                "energy_cost_per_block": 0.5,
                "rest_recovery": 30.0,
                "max_energy": 100.0,
            },
        }

        # Lưu các file cấu hình
        self.save_config(city_config, "default_city.yaml")
        self.save_config(character_config, "characters.yaml")
        logger.info("Default configuration files created")
