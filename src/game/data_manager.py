import json
import os
import time
import logging
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class PlayerData:
    """玩家数据结构"""
    level: int = 1
    exp: int = 0
    attack_power: int = 10
    weapon_tier: int = 1
    coins: int = 0
    ai_affinity: int = 10
    location: str = "新手村"
    max_combo: int = 0
    max_stamina: int = 100
    crit_rate: float = 0.05
    play_time: float = 0.0  # 游戏时间（秒）


@dataclass
class AIData:
    """AI数据结构"""
    bond: int = 10
    mood: str = "neutral"
    total_responses: int = 0
    personality_type: str = "encouraging"
    learning_data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.learning_data is None:
            self.learning_data = {}


@dataclass
class GameStats:
    """游戏统计数据"""
    total_attacks: int = 0
    total_damage: int = 0
    total_crits: int = 0
    total_defeats: int = 0
    total_coins_earned: int = 0
    total_time_played: float = 0.0
    session_start_time: float = 0.0
    last_save_time: float = 0.0
    version: str = "1.0.0"


@dataclass
class GameSettings:
    """游戏设置"""
    master_volume: float = 0.7
    sfx_volume: float = 0.8
    music_volume: float = 0.6
    screen_width: int = 800
    screen_height: int = 600
    fullscreen: bool = False
    vsync: bool = True
    show_fps: bool = False
    auto_save: bool = True
    auto_save_interval: int = 300  # 5分钟


@dataclass
class SaveData:
    """存档数据结构"""
    player: PlayerData
    ai: AIData
    stats: GameStats
    settings: GameSettings
    save_time: float = 0.0
    save_version: str = "1.0.0"
    checksum: str = ""


class DataManager:
    """存档管理器 - 负责游戏数据的保存和加载"""

    def __init__(self, save_directory: str = "saves", auto_save_enabled: bool = True):
        self.save_directory = Path(save_directory)
        self.auto_save_enabled = auto_save_enabled
        self.auto_save_timer = 0
        self.last_auto_save = 0

        # 存档文件路径
        self.save_file = self.save_directory / "savegame.json"
        self.backup_file = self.save_directory / "savegame_backup.json"
        self.settings_file = self.save_directory / "settings.json"

        # 当前数据
        self.current_data: Optional[SaveData] = None
        self.settings: GameSettings = GameSettings()

        # 日志
        self.logger = logging.getLogger(__name__)

        # 创建存档目录
        self._ensure_save_directory()

        # 加载设置
        self._load_settings()

        # 统计数据
        self.stats = {
            'saves_loaded': 0,
            'saves_saved': 0,
            'auto_saves': 0,
            'corrupted_saves': 0,
            'last_operation': 'none',
            'last_operation_time': time.time()
        }

    def _ensure_save_directory(self) -> None:
        """确保存档目录存在"""
        try:
            self.save_directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Save directory: {self.save_directory}")
        except Exception as e:
            self.logger.error(f"Failed to create save directory: {e}")

    def create_new_save(self, player, ai_manager) -> bool:
        """
        创建新存档

        Args:
            player: 玩家对象
            ai_manager: AI管理器

        Returns:
            是否创建成功
        """
        try:
            # 提取玩家数据
            player_data = PlayerData(
                level=player.level,
                exp=player.exp,
                attack_power=player.attack_power,
                weapon_tier=player.weapon_tier,
                coins=player.coins,
                ai_affinity=player.ai_affinity,
                location=player.location,
                max_combo=player.max_combo,
                max_stamina=player.max_stamina,
                crit_rate=player.crit_rate,
                play_time=0.0  # 初始化为0
            )

            # 提取AI数据
            ai_data = AIData(
                bond=ai_manager.get_ai_bond(),
                mood=ai_manager.get_current_mood().value,
                total_responses=0,  # 初始化为0
                personality_type=getattr(ai_manager.ai_engine, 'personality_type', 'default'),
                learning_data={}
            )

            # 创建统计数据
            game_stats = GameStats(
                session_start_time=time.time(),
                last_save_time=time.time()
            )

            # 创建存档数据
            self.current_data = SaveData(
                player=player_data,
                ai=ai_data,
                stats=game_stats,
                settings=self.settings,
                save_time=time.time(),
                save_version="1.0.0"
            )

            # 更新保存时间
            self.current_data.save_time = time.time()
            self.current_data.stats.last_save_time = time.time()

            # 计算校验和
            self.current_data.checksum = self._calculate_checksum(self.current_data)

            # 保存存档
            if self.save_game():
                self.logger.info("New save file created successfully")
                return True

        except Exception as e:
            self.logger.error(f"Failed to create new save: {e}")
            self.stats['last_operation'] = 'create_new_save_failed'
            self.stats['last_operation_time'] = time.time()

        return False

    def save_game(self, player=None, ai_manager=None, force: bool = False) -> bool:
        """
        保存游戏

        Args:
            player: 玩家对象（可选）
            ai_manager: AI管理器（可选）
            force: 是否强制保存

        Returns:
            是否保存成功
        """
        if not self.current_data:
            self.logger.warning("No current data to save")
            return False

        try:
            # 更新数据
            if player:
                self._update_player_data(player)
            if ai_manager:
                self._update_ai_data(ai_manager)

            # 更新保存时间
            self.current_data.save_time = time.time()
            self.current_data.stats.last_save_time = time.time()

            # 计算校验和
            self.current_data.checksum = self._calculate_checksum(self.current_data)

            # 创建备份
            if self.save_file.exists():
                self._create_backup()

            # 保存主文件
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.current_data), f, ensure_ascii=False, indent=2)

            # 更新统计
            self.stats['saves_saved'] += 1
            self.stats['last_operation'] = 'save'
            self.stats['last_operation_time'] = time.time()

            if not force:
                self.last_auto_save = time.time()

            self.logger.info(f"Game saved successfully at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save game: {e}")
            self.stats['last_operation'] = 'save_failed'
            self.stats['last_operation_time'] = time.time()
            return False

    def load_game(self) -> bool:
        """
        加载游戏

        Returns:
            是否加载成功
        """
        try:
            # 检查存档文件是否存在
            if not self.save_file.exists():
                self.logger.info("No save file found")
                return False

            # 读取存档文件
            with open(self.save_file, 'r', encoding='utf-8') as f:
                save_dict = json.load(f)
            
            # 打印加载的数据用于调试
            # print(f"Loaded data: {save_dict}")

            # 验证存档版本
            if not self._validate_save_version(save_dict.get('save_version', '1.0.0')):
                self.logger.warning("Save version mismatch")
                return False

            # 验证校验和
            if not self._validate_checksum(save_dict):
                self.logger.warning("Save file checksum validation failed")
                self.stats['corrupted_saves'] += 1
                return False

            # 解析存档数据
            self.current_data = SaveData(
                player=PlayerData(**save_dict['player']),
                ai=AIData(**save_dict['ai']),
                stats=GameStats(**save_dict['stats']),
                settings=GameSettings(**save_dict['settings']),
                save_time=save_dict['save_time'],
                save_version=save_dict['save_version'],
                checksum=save_dict['checksum']
            )

            # 更新统计
            self.stats['saves_loaded'] += 1
            self.stats['last_operation'] = 'load'
            self.stats['last_operation_time'] = time.time()

            self.logger.info(f"Game loaded successfully (saved at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.current_data.save_time))})")
            return True

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in save file: {e}")
            self.stats['corrupted_saves'] += 1
            return False
        except KeyError as e:
            self.logger.error(f"Missing required field in save file: {e}")
            self.stats['corrupted_saves'] += 1
            return False
        except Exception as e:
            self.logger.error(f"Failed to load game: {e}")
            return False

    def try_load_backup(self) -> bool:
        """
        尝试加载备份存档

        Returns:
            是否加载成功
        """
        if not self.backup_file.exists():
            return False

        try:
            # 临时重命名备份文件
            temp_backup = self.backup_file.with_suffix('.json.temp')
            self.backup_file.rename(temp_backup)

            # 复制备份为主存档
            import shutil
            shutil.copy2(temp_backup, self.save_file)

            # 尝试加载
            success = self.load_game()

            if success:
                self.logger.info("Backup save loaded successfully")
            else:
                # 如果失败，恢复原状
                self.save_file.unlink()
                temp_backup.rename(self.backup_file)

            return success

        except Exception as e:
            self.logger.error(f"Failed to load backup save: {e}")
            return False

    def apply_loaded_data(self, player, ai_manager) -> bool:
        """
        将加载的数据应用到游戏对象

        Args:
            player: 玩家对象
            ai_manager: AI管理器

        Returns:
            是否应用成功
        """
        if not self.current_data:
            return False

        try:
            # 应用玩家数据
            player.level = self.current_data.player.level
            player.exp = self.current_data.player.exp
            player.attack_power = self.current_data.player.attack_power
            player.weapon_tier = self.current_data.player.weapon_tier
            player.coins = self.current_data.player.coins
            player.ai_affinity = self.current_data.player.ai_affinity
            player.location = self.current_data.player.location
            player.max_combo = self.current_data.player.max_combo
            player.max_stamina = self.current_data.player.max_stamina
            player.crit_rate = self.current_data.player.crit_rate

            # 重新计算升级所需经验
            player.next_exp = player.calc_exp_needed(player.level)

            # 应用AI数据
            if hasattr(ai_manager.ai_engine, 'bond'):
                ai_manager.ai_engine.bond = self.current_data.ai.bond

            # 应用设置
            self.settings = self.current_data.settings

            self.logger.info("Loaded data applied successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to apply loaded data: {e}")
            return False

    def delete_save(self) -> bool:
        """
        删除存档

        Returns:
            是否删除成功
        """
        try:
            if self.save_file.exists():
                self.save_file.unlink()
            if self.backup_file.exists():
                self.backup_file.unlink()

            self.current_data = None
            self.logger.info("Save file deleted")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete save: {e}")
            return False

    def _update_player_data(self, player) -> None:
        """更新玩家数据"""
        if self.current_data:
            self.current_data.player.level = player.level
            self.current_data.player.exp = player.exp
            self.current_data.player.attack_power = player.attack_power
            self.current_data.player.weapon_tier = player.weapon_tier
            self.current_data.player.coins = player.coins
            self.current_data.player.ai_affinity = player.ai_affinity
            self.current_data.player.location = player.location
            self.current_data.player.max_combo = player.max_combo
            self.current_data.player.max_stamina = player.max_stamina
            self.current_data.player.crit_rate = player.crit_rate
            # 更新play_time字段
            self.current_data.player.play_time = getattr(player, 'play_time', self.current_data.player.play_time)

    def _update_ai_data(self, ai_manager) -> None:
        """更新AI数据"""
        if self.current_data:
            self.current_data.ai.bond = ai_manager.get_ai_bond()
            self.current_data.ai.mood = ai_manager.get_current_mood().value
            # 只有在total_responses存在时才增加（但不在创建新存档时增加）
            # 注意：这个计数器应该在适当的时候增加，而不是每次保存都增加
            # 在这个实现中，我们暂时不自动增加这个计数器

    def _create_backup(self) -> None:
        """创建备份"""
        try:
            if self.save_file.exists():
                import shutil
                shutil.copy2(self.save_file, self.backup_file)
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")

    def _calculate_checksum(self, data: SaveData) -> str:
        """计算校验和"""
        data_dict = asdict(data)
        
        # 移除动态时间戳字段以确保校验和一致性
        if 'stats' in data_dict and isinstance(data_dict['stats'], dict):
            data_dict['stats'] = data_dict['stats'].copy()
            data_dict['stats'].pop('session_start_time', None)
            data_dict['stats'].pop('last_save_time', None)
        
        if 'save_time' in data_dict:
            data_dict.pop('save_time', None)
            
        # 移除校验和字段本身，避免循环依赖
        if 'checksum' in data_dict:
            data_dict.pop('checksum', None)
            
        # 使用与验证时相同的排序方式
        data_str = json.dumps(data_dict, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        checksum = hashlib.md5(data_str.encode()).hexdigest()
        return checksum

    def _validate_checksum(self, save_dict: Dict[str, Any]) -> bool:
        """验证校验和"""
        try:
            saved_checksum = save_dict.get('checksum', '')
            if not saved_checksum:
                return False  # 没有校验和

            # 创建一个副本用于计算校验和，避免修改原始数据
            temp_dict = save_dict.copy()
            
            # 移除动态时间戳字段以确保校验和一致性
            if 'stats' in temp_dict and isinstance(temp_dict['stats'], dict):
                temp_dict['stats'] = temp_dict['stats'].copy()
                temp_dict['stats'].pop('session_start_time', None)
                temp_dict['stats'].pop('last_save_time', None)
            
            if 'save_time' in temp_dict:
                temp_dict.pop('save_time', None)
            
            # 移除校验和字段
            temp_dict.pop('checksum', None)
            
            # 使用与计算校验和时相同的排序方式
            data_str = json.dumps(temp_dict, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
            calculated_checksum = hashlib.md5(data_str.encode()).hexdigest()

            return calculated_checksum == saved_checksum

        except Exception as e:
            self.logger.error(f"Checksum validation error: {e}")
            return False

    def _validate_save_version(self, version: str) -> bool:
        """验证存档版本"""
        try:
            # 当前支持的版本
            supported_versions = ['1.0.0']
            return version in supported_versions
        except Exception:
            return False

    def _load_settings(self) -> None:
        """加载设置"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings_dict = json.load(f)
                self.settings = GameSettings(**settings_dict)
                self.logger.info("Settings loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            # 使用默认设置

    def save_settings(self) -> bool:
        """保存设置"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.settings), f, ensure_ascii=False, indent=2)
            self.logger.info("Settings saved successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            return False

    def auto_save_check(self, player=None, ai_manager=None) -> None:
        """自动保存检查"""
        if not self.auto_save_enabled or not self.settings.auto_save:
            return

        current_time = time.time()
        time_since_last_save = current_time - self.last_auto_save

        if time_since_last_save >= self.settings.auto_save_interval:
            if self.save_game(player, ai_manager):
                self.stats['auto_saves'] += 1
                self.logger.debug("Auto-save completed")

    def get_save_info(self) -> Dict[str, Any]:
        """获取存档信息"""
        if not self.current_data:
            return {'has_save': False}

        return {
            'has_save': True,
            'save_time': self.current_data.save_time,
            'save_version': self.current_data.save_version,
            'player_level': self.current_data.player.level,
            'play_time': self.current_data.player.play_time,
            'location': self.current_data.player.location,
            'file_size': self.save_file.stat().st_size if self.save_file.exists() else 0
        }

    def get_data_manager_stats(self) -> Dict[str, Any]:
        """获取数据管理器统计信息"""
        return self.stats.copy()

    def export_save_data(self, export_path: str) -> bool:
        """
        导出存档数据

        Args:
            export_path: 导出路径

        Returns:
            是否导出成功
        """
        if not self.current_data:
            return False

        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)

            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.current_data), f, ensure_ascii=False, indent=2)

            self.logger.info(f"Save data exported to {export_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export save data: {e}")
            return False

    def import_save_data(self, import_path: str) -> bool:
        """
        导入存档数据

        Args:
            import_path: 导入路径

        Returns:
            是否导入成功
        """
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                return False

            # 读取导入文件
            with open(import_file, 'r', encoding='utf-8') as f:
                import_dict = json.load(f)

            # 验证导入数据
            if not self._validate_save_version(import_dict.get('save_version', '1.0.0')):
                return False

            # 创建备份当前存档
            if self.save_file.exists():
                backup_timestamp = int(time.time())
                backup_name = f"savegame_backup_{backup_timestamp}.json"
                backup_path = self.save_directory / backup_name
                import shutil
                shutil.copy2(self.save_file, backup_path)

            # 导入数据
            self.current_data = SaveData(
                player=PlayerData(**import_dict['player']),
                ai=AIData(**import_dict['ai']),
                stats=GameStats(**import_dict['stats']),
                settings=GameSettings(**import_dict['settings']),
                save_time=time.time(),
                save_version=import_dict['save_version'],
                checksum=import_dict['checksum']
            )

            # 保存导入的数据
            return self.save_game(force=True)

        except Exception as e:
            self.logger.error(f"Failed to import save data: {e}")
            return False

    def cleanup_old_backups(self, max_backups: int = 5) -> None:
        """清理旧备份文件"""
        try:
            backup_files = list(self.save_directory.glob("savegame_backup_*.json"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            for backup_file in backup_files[max_backups:]:
                backup_file.unlink()
                self.logger.debug(f"Deleted old backup: {backup_file}")

        except Exception as e:
            self.logger.error(f"Failed to cleanup old backups: {e}")

    def reset_stats(self) -> None:
        """重置统计数据"""
        self.stats = {
            'saves_loaded': 0,
            'saves_saved': 0,
            'auto_saves': 0,
            'corrupted_saves': 0,
            'last_operation': 'none',
            'last_operation_time': time.time()
        }