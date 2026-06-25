"""City Builder - Tạo cấu trúc thành phố tự động"""

import random
from typing import Dict, List, Tuple, Any
from loguru import logger
from src.schematic_generator import SchematiGenerator
from src.character_manager import CharacterManager, TaskType


class CityBuilder:
    """Builder tạo các cấu trúc thành phố"""

    def __init__(self, width: int = 256, height: int = 128, length: int = 256):
        """Khởi tạo City Builder

        Args:
            width: Chiều rộng
            height: Chiều cao
            length: Chiều dài
        """
        self.width = width
        self.height = height
        self.length = length
        self.generator = SchematiGenerator(width, height, length)
        self.character_manager = CharacterManager()
        self.structures: List[Dict[str, Any]] = []
        logger.info(f"CityBuilder initialized with size {width}x{height}x{length}")

    def build_building(self, x: int, y: int, z: int, width: int, height: int,
                      depth: int, building_type: str = "residential") -> Dict[str, Any]:
        """Xây dựng một tòa nhà

        Args:
            x, y, z: Vị trí góc
            width: Chiều rộng tòa nhà
            height: Chiều cao tòa nhà
            depth: Chiều sâu tòa nhà
            building_type: Loại tòa nhà (residential, commercial, industrial)

        Returns:
            Thông tin tòa nhà
        """
        building_info = {
            "type": "building",
            "building_type": building_type,
            "pos": (x, y, z),
            "size": (width, height, depth),
            "blocks_used": width * height * depth
        }

        # Chọn vật liệu dựa vào loại
        if building_type == "residential":
            wall_block = "brick"
            floor_block = "wooden_planks"
            roof_block = "brick"
        elif building_type == "commercial":
            wall_block = "stone"
            floor_block = "stone"
            roof_block = "obsidian"
        else:  # industrial
            wall_block = "cobblestone"
            floor_block = "iron_block"
            roof_block = "cobblestone"

        # Vẽ tường ngoài
        self.generator.draw_rectangle(x, y, z, x + width - 1, y + height - 1, z + depth - 1,
                                     wall_block, fill=False)

        # Vẽ sàn nhà
        self.generator.draw_rectangle(x + 1, y + 1, z + 1, x + width - 2, y + 1, z + depth - 2,
                                     floor_block, fill=True)

        # Vẽ mặt sàn (mỗi tầng)
        for floor_y in range(y + 4, y + height - 1, 4):
            self.generator.draw_rectangle(x + 1, floor_y, z + 1, x + width - 2, floor_y,
                                         z + depth - 2, floor_block, fill=True)

        # Vẽ mái nhà
        self.generator.draw_rectangle(x, y + height, z, x + width - 1, y + height,
                                     z + depth - 1, roof_block, fill=True)

        self.structures.append(building_info)
        logger.info(f"Building created at ({x}, {y}, {z}): {building_type}")
        return building_info

    def build_road(self, start: Tuple[int, int, int], end: Tuple[int, int, int],
                  width: int = 5, material: str = "stone") -> Dict[str, Any]:
        """Xây dựng đường

        Args:
            start: Vị trí bắt đầu
            end: Vị trí kết thúc
            width: Chiều rộng đường
            material: Vật liệu

        Returns:
            Thông tin đường
        """
        road_info = {
            "type": "road",
            "start": start,
            "end": end,
            "width": width,
            "material": material
        }

        sx, sy, sz = start
        ex, ey, ez = end
        distance = max(abs(ex - sx), abs(ez - sz))

        # Vẽ đường nối
        for i in range(distance + 1):
            t = i / (distance + 1) if distance > 0 else 0
            x = int(sx + (ex - sx) * t)
            z = int(sz + (ez - sz) * t)
            y = sy

            # Vẽ đường đi
            self.generator.draw_rectangle(x - width // 2, y, z - width // 2,
                                         x + width // 2, y, z + width // 2,
                                         material, fill=True)

            # Vẽ hè (lề đường)
            self.generator.draw_rectangle(x - width // 2 - 1, y, z - width // 2 - 1,
                                         x + width // 2 + 1, y, z + width // 2 + 1,
                                         "gravel", fill=False)

        self.structures.append(road_info)
        logger.info(f"Road created from {start} to {end}")
        return road_info

    def build_park(self, x: int, y: int, z: int, width: int, length: int) -> Dict[str, Any]:
        """Xây dựng công viên

        Args:
            x, y, z: Vị trí góc
            width: Chiều rộng
            length: Chiều dài

        Returns:
            Thông tin công viên
        """
        park_info = {
            "type": "park",
            "pos": (x, y, z),
            "size": (width, length),
            "blocks_used": width * length
        }

        # Nền của công viên
        self.generator.draw_rectangle(x, y, z, x + width - 1, y, z + length - 1,
                                     "grass", fill=True)

        # Cây cảnh (hình cầu nhỏ)
        num_trees = (width * length) // 50
        for _ in range(num_trees):
            tree_x = random.randint(x + 2, x + width - 2)
            tree_z = random.randint(z + 2, z + length - 2)
            tree_height = random.randint(5, 8)

            # Thân cây
            self.generator.draw_rectangle(tree_x, y + 1, tree_z, tree_x, y + tree_height,
                                         tree_z, "oak_wood", fill=True)

            # Tán cây
            self.generator.draw_sphere(tree_x, y + tree_height + 2, tree_z, 3,
                                      "oak_leaves")

        # Lối đi trong công viên
        self.generator.draw_rectangle(x + 1, y, z + length // 2 - 1,
                                     x + width - 1, y, z + length // 2 + 1,
                                     "sand", fill=True)

        self.structures.append(park_info)
        logger.info(f"Park created at ({x}, {y}, {z}): {width}x{length}")
        return park_info

    def build_city_layout(self, config: Dict[str, Any]) -> List:
        """Xây dựng bố cục thành phố tự động

        Args:
            config: Cấu hình thành phố

        Returns:
            Danh sách nhiệm vụ
        """
        tasks = []
        building_id = 0
        road_id = 0
        park_id = 0

        # Tập chính
        main_x, main_z = 50, 50
        self.generator.draw_rectangle(main_x, 64, main_z, main_x + 30, 64,
                                     main_z + 30, "diamond_block", fill=True)

        # Xây dựng tòa nhà
        num_buildings = config.get("num_buildings", 10)
        for i in range(num_buildings):
            bx = random.randint(20, self.width - 40)
            bz = random.randint(20, self.length - 40)
            by = 64
            bw = random.randint(15, 30)
            bh = random.randint(20, 40)
            bd = random.randint(15, 30)

            building_type = random.choice(["residential", "commercial", "industrial"])
            self.build_building(bx, by, bz, bw, bh, bd, building_type)

            # Tạo task cho nhân vật
            blocks = ["stone"] * (bw * bh * bd)
            task_id = f"build_building_{building_id}"
            task = self.character_manager.create_task(
                task_id=task_id,
                task_type=TaskType.BUILD_BUILDING,
                start_pos=(bx, by, bz),
                end_pos=(bx + bw, by + bh, bz + bd),
                blocks=blocks
            )
            tasks.append(task)
            building_id += 1

        # Xây dựng đường phố
        num_roads = config.get("num_roads", 5)
        for i in range(num_roads):
            start_x = random.randint(20, self.width - 40)
            start_z = random.randint(20, self.length - 40)
            end_x = random.randint(20, self.width - 40)
            end_z = random.randint(20, self.length - 40)

            self.build_road((start_x, 64, start_z), (end_x, 64, end_z), width=5)

            task_id = f"build_road_{road_id}"
            distance = max(abs(end_x - start_x), abs(end_z - start_z))
            blocks = ["stone"] * (distance * 5)
            task = self.character_manager.create_task(
                task_id=task_id,
                task_type=TaskType.BUILD_ROAD,
                start_pos=(start_x, 64, start_z),
                end_pos=(end_x, 64, end_z),
                blocks=blocks
            )
            tasks.append(task)
            road_id += 1

        # Xây dựng công viên
        num_parks = config.get("num_parks", 3)
        for i in range(num_parks):
            px = random.randint(20, self.width - 80)
            pz = random.randint(20, self.length - 80)
            pw = random.randint(40, 80)
            pl = random.randint(40, 80)

            self.build_park(px, 64, pz, pw, pl)

            task_id = f"build_park_{park_id}"
            blocks = ["grass"] * (pw * pl)
            task = self.character_manager.create_task(
                task_id=task_id,
                task_type=TaskType.BUILD_PARK,
                start_pos=(px, 64, pz),
                end_pos=(px + pw, 64, pz + pl),
                blocks=blocks
            )
            tasks.append(task)
            park_id += 1

        logger.info(f"City layout created with {building_id} buildings, {road_id} roads, {park_id} parks")
        return tasks

    def create_worker_team(self, num_workers: int = 5) -> None:
        """Tạo nhóm công nhân

        Args:
            num_workers: Số công nhân
        """
        names = [
            "Alex", "Steve", "Notch", "Herobrine", "Creeper",
            "Enderman", "Skeleton", "Zombie", "Witch", "Wither"
        ]

        for i in range(min(num_workers, len(names))):
            char_id = f"worker_{i}"
            name = names[i]
            skill_level = random.randint(1, 10)
            speed = 0.8 + random.random() * 0.4  # 0.8 - 1.2

            self.character_manager.create_character(
                char_id=char_id,
                name=name,
                skill_level=skill_level,
                speed=speed
            )

        logger.info(f"Worker team created with {num_workers} members")

    def simulate_building(self, ticks: int = 100) -> None:
        """Mô phỏng quá trình xây dựng

        Args:
            ticks: Số chu kỳ mô phỏng
        """
        logger.info(f"Starting building simulation for {ticks} ticks")

        for tick in range(ticks):
            # Tự động giao công việc
            self.character_manager.auto_assign_tasks()

            # Thực hiện chu kỳ làm việc
            self.character_manager.work_tick(blocks_per_tick=10)

            # In trạng thái mỗi 20 chu kỳ
            if tick % 20 == 0:
                self.character_manager.print_status()

        logger.info("Building simulation completed")

    def export_schematic(self, filepath: str) -> None:
        """Xuất schematic đi

        Args:
            filepath: Đường dẫn file
        """
        metadata = {
            "Name": "Generated City",
            "Author": "CityBuilder",
            "Buildings": len([s for s in self.structures if s["type"] == "building"]),
            "Roads": len([s for s in self.structures if s["type"] == "road"]),
            "Parks": len([s for s in self.structures if s["type"] == "park"])
        }
        self.generator.save(filepath, metadata)
        logger.info(f"Schematic exported to {filepath}")

    def get_city_statistics(self) -> Dict[str, Any]:
        """Lấy thống kê thành phố"""
        buildings = [s for s in self.structures if s["type"] == "building"]
        roads = [s for s in self.structures if s["type"] == "road"]
        parks = [s for s in self.structures if s["type"] == "park"]

        return {
            "total_buildings": len(buildings),
            "total_roads": len(roads),
            "total_parks": len(parks),
            "total_structures": len(self.structures),
            "team_stats": self.character_manager.get_statistics()
        }
