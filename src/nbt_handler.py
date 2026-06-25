"""NBT Handler - Xử lý định dạng NBT cho file schematic"""

import struct
import gzip
from typing import Dict, Any, List, Tuple
from loguru import logger


class NBTHandler:
    """Handler cho định dạng NBT (Named Binary Tag)"""

    # NBT Tag Types
    TAG_END = 0
    TAG_BYTE = 1
    TAG_SHORT = 2
    TAG_INT = 3
    TAG_LONG = 4
    TAG_FLOAT = 5
    TAG_DOUBLE = 6
    TAG_BYTE_ARRAY = 7
    TAG_STRING = 8
    TAG_LIST = 9
    TAG_COMPOUND = 10
    TAG_INT_ARRAY = 11
    TAG_LONG_ARRAY = 12

    def __init__(self):
        """Khởi tạo NBT Handler"""
        logger.info("NBT Handler initialized")

    def create_schematic_nbt(self, width: int, height: int, length: int,
                            blocks: List[int], metadata: Dict[str, Any]) -> bytes:
        """Tạo NBT data cho file schematic

        Args:
            width: Chiều rộng (X)
            height: Chiều cao (Y)
            length: Chiều dài (Z)
            blocks: Danh sách block IDs
            metadata: Metadata cho schematic

        Returns:
            NBT data dưới dạng bytes
        """
        nbt_data = {
            "Schematic": {
                "Width": (self.TAG_SHORT, width),
                "Height": (self.TAG_SHORT, height),
                "Length": (self.TAG_SHORT, length),
                "Materials": (self.TAG_STRING, "Alpha"),
                "Blocks": (self.TAG_BYTE_ARRAY, bytes(blocks)),
                "Data": (self.TAG_BYTE_ARRAY, bytes([0] * len(blocks))),
            }
        }

        # Thêm metadata nếu có
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, str):
                    nbt_data["Schematic"][key] = (self.TAG_STRING, value)
                elif isinstance(value, int):
                    nbt_data["Schematic"][key] = (self.TAG_INT, value)

        return self._encode_nbt(nbt_data)

    def _encode_nbt(self, data: Dict[str, Any]) -> bytes:
        """Encode NBT data"""
        try:
            buffer = bytearray()

            for key, value in data.items():
                buffer.extend(self._write_tag(key, value))

            buffer.append(self.TAG_END)
            return bytes(buffer)
        except Exception as e:
            logger.error(f"Error encoding NBT: {e}")
            raise

    def _write_tag(self, name: str, value: Tuple) -> bytes:
        """Ghi một tag NBT"""
        tag_type, tag_value = value
        buffer = bytearray()

        buffer.append(tag_type)
        buffer.extend(self._write_string(name))

        if tag_type == self.TAG_BYTE:
            buffer.append(tag_value & 0xFF)
        elif tag_type == self.TAG_SHORT:
            buffer.extend(struct.pack(">h", tag_value))
        elif tag_type == self.TAG_INT:
            buffer.extend(struct.pack(">i", tag_value))
        elif tag_type == self.TAG_LONG:
            buffer.extend(struct.pack(">q", tag_value))
        elif tag_type == self.TAG_FLOAT:
            buffer.extend(struct.pack(">f", tag_value))
        elif tag_type == self.TAG_DOUBLE:
            buffer.extend(struct.pack(">d", tag_value))
        elif tag_type == self.TAG_BYTE_ARRAY:
            buffer.extend(struct.pack(">i", len(tag_value)))
            buffer.extend(tag_value)
        elif tag_type == self.TAG_STRING:
            buffer.extend(self._write_string(tag_value))
        elif tag_type == self.TAG_LIST:
            buffer.extend(self._write_list(tag_value))
        elif tag_type == self.TAG_COMPOUND:
            buffer.extend(self._encode_nbt(tag_value))
            buffer.append(self.TAG_END)

        return bytes(buffer)

    def _write_string(self, s: str) -> bytes:
        """Ghi string NBT"""
        encoded = s.encode('utf-8')
        return struct.pack(">h", len(encoded)) + encoded

    def _write_list(self, items: List[Tuple]) -> bytes:
        """Ghi list NBT"""
        if not items:
            return struct.pack(">bi", self.TAG_END, 0)

        buffer = bytearray()
        tag_type = items[0][0]
        buffer.append(tag_type)
        buffer.extend(struct.pack(">i", len(items)))

        for _, value in items:
            if tag_type == self.TAG_INT:
                buffer.extend(struct.pack(">i", value))
            elif tag_type == self.TAG_STRING:
                buffer.extend(self._write_string(value))

        return bytes(buffer)

    def save_schematic(self, data: bytes, filepath: str) -> None:
        """Lưu schematic vào file"""
        try:
            with gzip.open(filepath, 'wb') as f:
                f.write(data)
            logger.info(f"Schematic saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving schematic: {e}")
            raise
