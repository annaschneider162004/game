"""Video Recorder - Quay video Minecraft tự động"""

import os
import subprocess
import cv2
import numpy as np
from typing import Tuple, List, Optional
from pathlib import Path
from loguru import logger


class VideoRecorder:
    """Quay video từ schematic Minecraft"""

    def __init__(self, output_dir: str = "output"):
        """Khởi tạo Video Recorder

        Args:
            output_dir: Thư mục lưu video
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.video_writer = None
        logger.info(f"VideoRecorder initialized with output directory: {output_dir}")

    def create_video_from_frames(self, frames: List[np.ndarray], output_path: str,
                                fps: int = 30, codec: str = 'mp4v') -> None:
        """Tạo video từ danh sách frame

        Args:
            frames: Danh sách numpy array (frame)
            output_path: Đường dẫn file video
            fps: Frame per second
            codec: Codec video (mp4v, XVID, MJPG)
        """
        if not frames:
            logger.error("No frames provided")
            return

        # Lấy kích thước frame
        height, width = frames[0].shape[:2]

        # Tạo VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*codec)
        self.video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        if not self.video_writer.isOpened():
            logger.error(f"Failed to create video writer for {output_path}")
            return

        # Ghi frame
        for i, frame in enumerate(frames):
            self.video_writer.write(frame)
            if (i + 1) % 10 == 0:
                logger.debug(f"Written {i + 1}/{len(frames)} frames")

        # Giải phóng tài nguyên
        self.video_writer.release()
        logger.info(f"Video saved to {output_path}")

    def create_rotating_view(self, image_path: str, rotation_speed: float = 2.0,
                            duration: int = 10, fps: int = 30) -> List[np.ndarray]:
        """Tạo view xoay quanh hình ảnh

        Args:
            image_path: Đường dẫn ảnh
            rotation_speed: Tốc độ xoay (độ/frame)
            duration: Thời lượng video (giây)
            fps: Frame per second

        Returns:
            Danh sách frame
        """
        # Đọc ảnh
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Failed to load image: {image_path}")
            return []

        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        frames = []

        # Tính số frame
        num_frames = int(duration * fps)

        for frame_idx in range(num_frames):
            # Tính góc xoay
            angle = (frame_idx * rotation_speed) % 360

            # Ma trận xoay
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))

            frames.append(rotated_image)

        logger.info(f"Created {num_frames} rotating frames")
        return frames

    def create_zoom_effect(self, image_path: str, zoom_factor: float = 1.5,
                          duration: int = 5, fps: int = 30) -> List[np.ndarray]:
        """Tạo hiệu ứng zoom in/out

        Args:
            image_path: Đường dẫn ảnh
            zoom_factor: Hệ số zoom
            duration: Thời lượng video (giây)
            fps: Frame per second

        Returns:
            Danh sách frame
        """
        # Đọc ảnh
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Failed to load image: {image_path}")
            return []

        height, width = image.shape[:2]
        frames = []

        # Tính số frame
        num_frames = int(duration * fps)

        for frame_idx in range(num_frames):
            # Tính tỷ lệ zoom
            progress = frame_idx / num_frames
            current_zoom = 1.0 + (zoom_factor - 1.0) * progress

            # Tính kích thước mới
            new_height = int(height * current_zoom)
            new_width = int(width * current_zoom)

            # Resize ảnh
            zoomed = cv2.resize(image, (new_width, new_height))

            # Tính vị trí cắt
            y_start = (new_height - height) // 2
            x_start = (new_width - width) // 2

            # Cắt ảnh
            if new_height > height and new_width > width:
                cropped = zoomed[y_start:y_start+height, x_start:x_start+width]
            else:
                # Pad ảnh nếu zoom out
                cropped = np.zeros((height, width, 3), dtype=np.uint8)
                y_offset = (height - new_height) // 2
                x_offset = (width - new_width) // 2
                cropped[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = zoomed

            frames.append(cropped)

        logger.info(f"Created {num_frames} zoom frames")
        return frames

    def create_transition(self, image1_path: str, image2_path: str,
                         duration: int = 3, fps: int = 30) -> List[np.ndarray]:
        """Tạo hiệu ứng chuyển tiếp giữa hai ảnh

        Args:
            image1_path: Đường dẫn ảnh đầu tiên
            image2_path: Đường dẫn ảnh thứ hai
            duration: Thời lượng hiệu ứng (giây)
            fps: Frame per second

        Returns:
            Danh sách frame
        """
        # Đọc ảnh
        image1 = cv2.imread(image1_path)
        image2 = cv2.imread(image2_path)

        if image1 is None or image2 is None:
            logger.error("Failed to load transition images")
            return []

        # Đảm bảo cùng kích thước
        height, width = image1.shape[:2]
        image2 = cv2.resize(image2, (width, height))

        frames = []
        num_frames = int(duration * fps)

        for frame_idx in range(num_frames):
            # Tính alpha blending
            alpha = frame_idx / num_frames
            blended = cv2.addWeighted(image1, 1 - alpha, image2, alpha, 0)
            frames.append(blended)

        logger.info(f"Created {num_frames} transition frames")
        return frames

    def add_text_overlay(self, frames: List[np.ndarray], text: str,
                        font_size: float = 1.0, color: Tuple[int, int, int] = (255, 255, 255),
                        position: Tuple[int, int] = None) -> List[np.ndarray]:
        """Thêm text overlay vào frames

        Args:
            frames: Danh sách frame
            text: Nội dung text
            font_size: Kích thước font
            color: Màu RGB
            position: Vị trí text (x, y), None = center

        Returns:
            Danh sách frame có text overlay
        """
        result_frames = []
        font = cv2.FONT_HERSHEY_SIMPLEX

        for frame in frames:
            frame_copy = frame.copy()
            height, width = frame.shape[:2]

            # Tính vị trí nếu không cho
            if position is None:
                text_size = cv2.getTextSize(text, font, font_size, 2)[0]
                position = ((width - text_size[0]) // 2, (height + text_size[1]) // 2)

            # Chuyển BGR sang RGB nếu cần
            color_bgr = (color[2], color[1], color[0])

            # Thêm text
            cv2.putText(frame_copy, text, position, font, font_size, color_bgr, 2)
            result_frames.append(frame_copy)

        logger.info(f"Added text overlay to {len(result_frames)} frames")
        return result_frames

    def add_watermark(self, frames: List[np.ndarray], watermark_path: str,
                     position: str = "bottom-right", opacity: float = 0.7) -> List[np.ndarray]:
        """Thêm watermark vào video

        Args:
            frames: Danh sách frame
            watermark_path: Đường dẫn ảnh watermark
            position: Vị trí watermark (top-left, top-right, bottom-left, bottom-right)
            opacity: Độ trong suốt (0-1)

        Returns:
            Danh sách frame có watermark
        """
        watermark = cv2.imread(watermark_path, cv2.IMREAD_UNCHANGED)
        if watermark is None:
            logger.error(f"Failed to load watermark: {watermark_path}")
            return frames

        result_frames = []

        for frame in frames:
            frame_copy = frame.copy()
            frame_height, frame_width = frame.shape[:2]
            watermark_height, watermark_width = watermark.shape[:2]

            # Tính vị trí watermark
            if position == "top-left":
                x, y = 10, 10
            elif position == "top-right":
                x = frame_width - watermark_width - 10
                y = 10
            elif position == "bottom-left":
                x = 10
                y = frame_height - watermark_height - 10
            else:  # bottom-right
                x = frame_width - watermark_width - 10
                y = frame_height - watermark_height - 10

            # Thêm watermark với opacity
            roi = frame_copy[y:y+watermark_height, x:x+watermark_width]
            if watermark.shape[2] == 4:  # RGBA
                alpha = watermark[:, :, 3] / 255.0
                for c in range(3):
                    roi[:, :, c] = roi[:, :, c] * (1 - alpha * opacity) + watermark[:, :, c] * (alpha * opacity)
            else:
                roi[:] = cv2.addWeighted(roi, 1 - opacity, watermark, opacity, 0)

            frame_copy[y:y+watermark_height, x:x+watermark_width] = roi
            result_frames.append(frame_copy)

        logger.info(f"Added watermark to {len(result_frames)} frames")
        return result_frames

    def save_video(self, frames: List[np.ndarray], filename: str, fps: int = 30) -> str:
        """Lưu video

        Args:
            frames: Danh sách frame
            filename: Tên file video
            fps: Frame per second

        Returns:
            Đường dẫn file video
        """
        output_path = str(self.output_dir / filename)
        self.create_video_from_frames(frames, output_path, fps)
        return output_path

    def combine_videos(self, video_list: List[str], output_path: str) -> None:
        """Kết hợp nhiều video thành một

        Args:
            video_list: Danh sách đường dẫn video
            output_path: Đường dẫn file video output
        """
        try:
            # Sử dụng ffmpeg để kết hợp video
            concat_filter = "concat=n={}:v=1:a=0".format(len(video_list))
            inputs = " ".join([f"-i {v}" for v in video_list])

            cmd = f"ffmpeg {inputs} -filter_complex {concat_filter} -y {output_path}"
            subprocess.run(cmd, shell=True, check=True)
            logger.info(f"Videos combined and saved to {output_path}")
        except Exception as e:
            logger.error(f"Error combining videos: {e}")
