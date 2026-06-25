"""Schematic Generator - Core generator cho file schematic"""

import numpy as np
from typing import Dict, List, Tuple, Any
from loguru import logger
from src.nbt_handler import NBTHandler


class SchematiGenerator:
    """Generator chính cho schematic Minecraft"""

    # Block IDs thường dùng
    BLOCKS = {
        "air": 0,
        "stone": 1,
        "dirt": 3,
        "cobblestone": 4,
        "oak_wood": 5,
        "oak_leaves": 18,
        "glass": 20,
        "sand": 12,
        "gravel": 13,
        "gold_ore": 14,
        "iron_ore": 15,
        "iron_block": 42,
        "diamond_ore": 56,
        "diamond_block": 57,
        "wooden_planks": 5,
        "brick": 45,
        "bookshelf": 47,
        "mossy_cobblestone": 48,
        "obsidian": 49,
    }

    def __init__(self, width: int = 256, height: int = 128, length: int = 256):
        """Khởi tạo Schematic Generator

        Args:
            width: Chiều rộng (X)
            height: Chiều cao (Y)
            length: Chiều dài (Z)
        """
        self.width = width
        self.height = height
        self.length = length
        self.nbt_handler = NBTHandler()
        self.blocks = np.zeros(width * height * length, dtype=np.uint8)
        logger.info(f"SchematiGenerator initialized: {width}x{height}x{length}")

    def set_block(self, x: int, y: int, z: int, block_type: str) -> None:
        """Đặt một block tại vị trí

        Args:
            x, y, z: Tọa độ
            block_type: Tên block
        """
        if 0 <= x < self.width and 0 <= y < self.height and 0 <= z < self.length:
            index = y * self.length * self.width + z * self.width + x
            block_id = self.BLOCKS.get(block_type, 0)
            self.blocks[index] = block_id

    def draw_rectangle(self, x1: int, y1: int, z1: int, x2: int, y2: int,
                      z2: int, block_type: str, fill: bool = True) -> None:
        """Vẽ hình chữ nhật

        Args:
            x1, y1, z1: Tọa độ góc 1
            x2, y2, z2: Tọa độ góc 2
            block_type: Loại block
            fill: Vẽ đầy hay chỉ viền
        """
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        min_z, max_z = min(z1, z2), max(z1, z2)

        if fill:
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    for z in range(min_z, max_z + 1):
                        self.set_block(x, y, z, block_type)
        else:
            # Vẽ viền
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    self.set_block(x, y, min_z, block_type)
                    self.set_block(x, y, max_z, block_type)
            for x in range(min_x, max_x + 1):
                for z in range(min_z, max_z + 1):
                    self.set_block(x, min_y, z, block_type)
                    self.set_block(x, max_y, z, block_type)
            for y in range(min_y, max_y + 1):
                for z in range(min_z, max_z + 1):
                    self.set_block(min_x, y, z, block_type)
                    self.set_block(max_x, y, z, block_type)

    def draw_line(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int,
                 block_type: str) -> None:
        """Vẽ đường thẳng từ điểm 1 đến điểm 2"""
        steps = max(abs(x2 - x1), abs(y2 - y1), abs(z2 - z1)) + 1
        for i in range(steps):
            t = i / steps
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)
            z = int(z1 + (z2 - z1) * t)
            self.set_block(x, y, z, block_type)

    def draw_sphere(self, cx: int, cy: int, cz: int, radius: int,
                   block_type: str) -> None:
        """Vẽ hình cầu"""
        for x in range(cx - radius, cx + radius + 1):
            for y in range(cy - radius, cy + radius + 1):
                for z in range(cz - radius, cz + radius + 1):
                    dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2)
                    if dist <= radius:
                        self.set_block(x, y, z, block_type)

    def clear(self) -> None:
        """Xóa tất cả blocks"""
        self.blocks = np.zeros(self.width * self.height * self.length, dtype=np.uint8)
        logger.info("Schematic cleared")

    def generate(self, metadata: Dict[str, Any] = None) -> bytes:
        """Sinh NBT data từ blocks

        Returns:
            NBT data dưới dạng bytes
        """
        if metadata is None:
            metadata = {"Name": "Generated City", "Author": "MCGen"}

        return self.nbt_handler.create_schematic_nbt(
            self.width, self.height, self.length, self.blocks.tolist(), metadata
        )

    def save(self, filepath: str, metadata: Dict[str, Any] = None) -> None:
        """Lưu schematic vào file

        Args:
            filepath: Đường dẫn file
            metadata: Metadata cho schematic
        """
        nbt_data = self.generate(metadata)
        self.nbt_handler.save_schematic(nbt_data, filepath)
        logger.info(f"Schematic saved successfully to {filepath}")
