"""Utilities - Những hàm tiện ích hỗ trợ"""

import os
from pathlib import Path
from typing import Tuple, Dict, Any
from loguru import logger


def ensure_output_dir() -> str:
    """Tạo thư mục output nếu không tồn tại

    Returns:
        Đường dẫn thư mục
    """
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return str(output_dir)


def generate_filename(city_name: str, timestamp: bool = True) -> str:
    """Sinh tên file cho schematic

    Args:
        city_name: Tên thành phố
        timestamp: Có thêm timestamp không

    Returns:
        Tên file
    """
    import datetime

    name = city_name.replace(" ", "_").lower()

    if timestamp:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{name}_{ts}.schematic"
    else:
        return f"{name}.schematic"


def format_size(size: int) -> str:
    """Format kích thước file thành đơn vị dễ đọc

    Args:
        size: Kích thước byte

    Returns:
        Cột định dễ đọc (KB, MB, GB)
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"


def calculate_volume(pos1: Tuple[int, int, int], pos2: Tuple[int, int, int]) -> int:
    """Tính thể tích giữa hai điểm

    Args:
        pos1: Vị trí điểm 1 (x, y, z)
        pos2: Vị trí điểm 2 (x, y, z)

    Returns:
        Thể tích
    """
    x1, y1, z1 = pos1
    x2, y2, z2 = pos2

    width = abs(x2 - x1) + 1
    height = abs(y2 - y1) + 1
    length = abs(z2 - z1) + 1

    return width * height * length


def calculate_distance(pos1: Tuple[int, int, int], pos2: Tuple[int, int, int]) -> float:
    """Tính khoảng cách giữa hai điểm

    Args:
        pos1: Vị trí điểm 1 (x, y, z)
        pos2: Vị trí điểm 2 (x, y, z)

    Returns:
        Khoảng cách
    """
    import math

    x1, y1, z1 = pos1
    x2, y2, z2 = pos2

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def setup_logging(log_file: str = None) -> None:
    """Cấu hình logging

    Args:
        log_file: Đường dẫn file log (None để chỉ in console)
    """
    from loguru import logger

    # Xóa default handler
    logger.remove()

    # Thêm console handler
    logger.add(
        lambda msg: print(msg, end=""),
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )

    # Thêm file handler nếu có
    if log_file:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
            level="DEBUG"
        )


def print_header(text: str, width: int = 60) -> None:
    """In header với đường đô sống chạp"""
    print(f"\n{'='*width}")
    print(f"{text.center(width)}")
    print(f"{'='*width}\n")


def print_stats(stats: Dict[str, Any]) -> None:
    """In thống kê dùng đẹp"""
    print(f"\n{'='*60}")
    print(f"{'STATISTICS':^60}")
    print(f"{'='*60}")

    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")

    print(f"\n{'='*60}\n")
