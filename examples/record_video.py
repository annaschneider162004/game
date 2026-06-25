"""Ví dụ: Quay video Minecraft tự động"""

import sys
from pathlib import Path
import numpy as np

# Thêm src vào path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.video_recorder import VideoRecorder
from loguru import logger


def create_sample_image():
    """Tạo ảnh mẫu cho ví dụ"""
    # Tạo ảnh gradient
    width, height = 800, 600
    image = np.zeros((height, width, 3), dtype=np.uint8)

    # Tạo gradient
    for y in range(height):
        for x in range(width):
            image[y, x] = [
                int(255 * x / width),
                int(255 * y / height),
                int(255 * (1 - (x + y) / (width + height)))
            ]

    # Lưu ảnh
    import cv2
    output_path = "output/sample_image.png"
    cv2.imwrite(output_path, image)
    logger.info(f"Sample image created: {output_path}")
    return output_path


def main():
    """Quay video Minecraft tự động"""

    logger.info("=== Minecraft Video Recorder ===")

    # Tạo thư mục output
    Path("output").mkdir(exist_ok=True)

    # Khởi tạo video recorder
    recorder = VideoRecorder(output_dir="output")

    # Tạo ảnh mẫu
    sample_image = create_sample_image()

    # Ví dụ 1: Video xoay quanh ảnh
    logger.info("\n--- Example 1: Rotating view ---")

    rotating_frames = recorder.create_rotating_view(
        sample_image,
        rotation_speed=3.0,
        duration=5,
        fps=30
    )

    if rotating_frames:
        recorder.save_video(rotating_frames, "rotating_view.mp4", fps=30)
        logger.info("✅ Rotating view video created")

    # Ví dụ 2: Video với hiệu ứng zoom
    logger.info("\n--- Example 2: Zoom effect ---")

    zoom_frames = recorder.create_zoom_effect(
        sample_image,
        zoom_factor=2.0,
        duration=5,
        fps=30
    )

    if zoom_frames:
        recorder.save_video(zoom_frames, "zoom_effect.mp4", fps=30)
        logger.info("✅ Zoom effect video created")

    # Ví dụ 3: Video chuyển tiếp
    logger.info("\n--- Example 3: Transition effect ---")

    transition_frames = recorder.create_transition(
        sample_image,
        sample_image,  # Ảnh thứ 2 (trong ví dụ này dùng ảnh giống nhau)
        duration=3,
        fps=30
    )

    if transition_frames:
        recorder.save_video(transition_frames, "transition_effect.mp4", fps=30)
        logger.info("✅ Transition effect video created")

    # Ví dụ 4: Thêm text overlay
    logger.info("\n--- Example 4: Text overlay ---")

    text_frames = recorder.add_text_overlay(
        rotating_frames[:30],  # Lấy 30 frame đầu
        text="Minecraft City Builder",
        font_size=2.0,
        color=(255, 255, 255)
    )

    if text_frames:
        recorder.save_video(text_frames, "with_text.mp4", fps=30)
        logger.info("✅ Video with text overlay created")

    logger.info("\n✅ All video examples completed!")
    logger.info("Output videos are in 'output' directory")


if __name__ == "__main__":
    main()
