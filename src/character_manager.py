"""Character Manager - Quản lý nhiều nhân vật bot xây dựng"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from loguru import logger
import random
from datetime import datetime


class TaskType(Enum):
    """Loại công việc"""
    BUILD_BUILDING = "build_building"
    BUILD_ROAD = "build_road"
    BUILD_PARK = "build_park"
    DECORATION = "decoration"
    LANDSCAPING = "landscaping"


@dataclass
class Task:
    """Một nhiệm vụ xây dựng"""
    task_id: str
    task_type: TaskType
    start_pos: Tuple[int, int, int]
    end_pos: Tuple[int, int, int]
    blocks: List[str]
    progress: float = 0.0
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: datetime = None
    completed_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Character:
    """Một nhân vật bot xây dựng"""
    char_id: str
    name: str
    skill_level: int = 1  # 1-10
    speed: float = 1.0  # Tốc độ xây dựng
    current_task: Task = None
    completed_tasks: List[str] = None
    position: Tuple[int, int, int] = (0, 0, 0)
    energy: float = 100.0
    max_energy: float = 100.0

    def __post_init__(self):
        if self.completed_tasks is None:
            self.completed_tasks = []

    def can_work(self) -> bool:
        """Kiểm tra xem nhân vật có thể làm việc không"""
        return self.energy >= 10.0

    def work(self, task: Task, blocks_per_tick: int = 1) -> float:
        """Thực hiện công việc

        Args:
            task: Nhiệm vụ cần thực hiện
            blocks_per_tick: Số block đặt mỗi lần

        Returns:
            Tiến độ hiện tại
        """
        if not self.can_work():
            logger.warning(f"Character {self.name} is too tired to work")
            return task.progress

        # Tính toán tiến độ
        work_amount = blocks_per_tick * self.speed * (self.skill_level / 10)
        total_blocks = len(task.blocks)
        progress_increase = work_amount / total_blocks

        task.progress = min(task.progress + progress_increase, 1.0)
        self.energy -= 5.0  # Tiêu tốn năng lượng

        if task.progress >= 1.0:
            task.status = "completed"
            task.completed_at = datetime.now()
            self.completed_tasks.append(task.task_id)
            logger.info(f"Character {self.name} completed task {task.task_id}")
            self.energy = min(self.energy + 20, self.max_energy)  # Phục hồi
        else:
            task.status = "in_progress"

        return task.progress

    def rest(self, amount: float = 30.0) -> None:
        """Nhân vật nghỉ ngơi"""
        self.energy = min(self.energy + amount, self.max_energy)
        logger.info(f"Character {self.name} rested. Energy: {self.energy}")

    def move_to(self, x: int, y: int, z: int) -> None:
        """Di chuyển đến vị trí"""
        self.position = (x, y, z)


class CharacterManager:
    """Quản lý nhóm nhân vật bot"""

    def __init__(self):
        """Khởi tạo Character Manager"""
        self.characters: Dict[str, Character] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[Task] = []
        logger.info("CharacterManager initialized")

    def create_character(self, char_id: str, name: str, skill_level: int = 1,
                        speed: float = 1.0) -> Character:
        """Tạo một nhân vật mới

        Args:
            char_id: ID của nhân vật
            name: Tên nhân vật
            skill_level: Cấp độ kỹ năng (1-10)
            speed: Tốc độ xây dựng

        Returns:
            Character object
        """
        character = Character(
            char_id=char_id,
            name=name,
            skill_level=max(1, min(10, skill_level)),
            speed=speed
        )
        self.characters[char_id] = character
        logger.info(f"Character created: {name} (ID: {char_id})")
        return character

    def create_task(self, task_id: str, task_type: TaskType, start_pos: Tuple[int, int, int],
                   end_pos: Tuple[int, int, int], blocks: List[str]) -> Task:
        """Tạo một nhiệm vụ xây dựng

        Args:
            task_id: ID của nhiệm vụ
            task_type: Loại nhiệm vụ
            start_pos: Vị trí bắt đầu
            end_pos: Vị trí kết thúc
            blocks: Danh sách block cần sử dụng

        Returns:
            Task object
        """
        task = Task(
            task_id=task_id,
            task_type=task_type,
            start_pos=start_pos,
            end_pos=end_pos,
            blocks=blocks
        )
        self.tasks[task_id] = task
        self.task_queue.append(task)
        logger.info(f"Task created: {task_id} ({task_type.value})")
        return task

    def assign_task(self, char_id: str, task_id: str) -> bool:
        """Giao nhiệm vụ cho nhân vật

        Args:
            char_id: ID của nhân vật
            task_id: ID của nhiệm vụ

        Returns:
            True nếu thành công, False nếu thất bại
        """
        if char_id not in self.characters:
            logger.error(f"Character {char_id} not found")
            return False

        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False

        character = self.characters[char_id]
        task = self.tasks[task_id]

        if character.current_task is not None and character.current_task.status == "in_progress":
            logger.warning(f"Character {char_id} is still working on another task")
            return False

        character.current_task = task
        task.status = "in_progress"
        character.move_to(*task.start_pos)
        logger.info(f"Task {task_id} assigned to {character.name}")
        return True

    def auto_assign_tasks(self) -> None:
        """Tự động giao việc cho các nhân vật"""
        available_characters = [c for c in self.characters.values()
                               if c.current_task is None or c.current_task.status == "completed"]
        pending_tasks = [t for t in self.task_queue if t.status == "pending"]

        for task in pending_tasks:
            if not available_characters:
                break
            character = available_characters.pop(0)
            self.assign_task(character.char_id, task.task_id)

    def work_tick(self, blocks_per_tick: int = 5) -> None:
        """Một chu kỳ làm việc - tất cả nhân vật làm việc

        Args:
            blocks_per_tick: Số block mỗi nhân vật đặt mỗi chu kỳ
        """
        for character in self.characters.values():
            if character.current_task and character.current_task.status == "in_progress":
                character.work(character.current_task, blocks_per_tick)
            elif character.energy < character.max_energy:
                character.rest()

    def get_statistics(self) -> Dict[str, Any]:
        """Lấy thống kê hiện tại"""
        total_characters = len(self.characters)
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks.values() if t.status == "completed")
        in_progress_tasks = sum(1 for t in self.tasks.values() if t.status == "in_progress")

        return {
            "total_characters": total_characters,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "characters": [
                {
                    "name": c.name,
                    "skill_level": c.skill_level,
                    "energy": c.energy,
                    "completed_tasks": len(c.completed_tasks)
                }
                for c in self.characters.values()
            ]
        }

    def print_status(self) -> None:
        """In trạng thái hiện tại"""
        stats = self.get_statistics()
        print(f"\n{'='*60}")
        print(f"Team Status - {len(self.characters)} Characters")
        print(f"{'='*60}")
        for char in stats["characters"]:
            print(f"  {char['name']:<15} | Skill: {char['skill_level']}/10 | Energy: {char['energy']:.1f}% | Tasks: {char['completed_tasks']}")
        print(f"\nTasks: {stats['in_progress_tasks']} in progress, {stats['completed_tasks']}/{stats['total_tasks']} completed")
        print(f"{'='*60}\n")
