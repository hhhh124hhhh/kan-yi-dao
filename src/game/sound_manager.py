import pygame
import random
import math
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass


class SoundType(Enum):
    """音效类型枚举"""
    SLASH = "slash"
    CRIT = "crit"
    LEVEL_UP = "level_up"
    COMBO = "combo"
    COIN = "coin"
    STAMINA_LOW = "stamina_low"
    ENEMY_HIT = "enemy_hit"
    ENEMY_DEFEAT = "enemy_defeat"
    BUTTON_CLICK = "button_click"
    UI_HOVER = "ui_hover"
    ERROR = "error"


@dataclass
class SoundEffect:
    """音效数据结构"""
    name: str
    sound_type: SoundType
    volume: float = 1.0
    pitch_variation: float = 0.0
    play_count: int = 0
    last_play_time: float = 0.0
    min_interval: float = 0.0


class SoundManager:
    """音效管理器 - 负责游戏中的所有音效播放和管理"""

    def __init__(self, sample_rate: int = 22050, buffer_size: int = 1024):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.enabled = True
        self.master_volume = 0.7
        self.sfx_volume = 0.8
        self.music_volume = 0.6

        # 初始化pygame.mixer
        try:
            pygame.mixer.pre_init(frequency=sample_rate, size=-16, channels=2, buffer=buffer_size)
            pygame.mixer.init()
            self.logger = logging.getLogger(__name__)
            self.logger.info("Sound system initialized successfully")
        except pygame.error as e:
            self.logger.error(f"Failed to initialize sound system: {e}")
            self.enabled = False

        # 音效存储
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.sound_effects: List[SoundEffect] = []

        # 音频通道管理
        self.available_channels = 8
        self.channels = []
        self._initialize_channels()

        # 统计数据
        self.stats = {
            'sounds_played': 0,
            'sounds_failed': 0,
            'total_play_time': 0.0,
            'most_played_sound': '',
            'last_update_time': time.time()
        }

        # 初始化音效
        self._initialize_sound_effects()

    def _initialize_channels(self) -> None:
        """初始化音频通道"""
        try:
            # 设置可用通道数
            pygame.mixer.set_num_channels(self.available_channels)

            # 创建通道引用
            for i in range(self.available_channels):
                channel = pygame.mixer.Channel(i)
                self.channels.append(channel)

        except Exception as e:
            self.logger.error(f"Failed to initialize audio channels: {e}")

    def _initialize_sound_effects(self) -> None:
        """初始化音效定义"""
        sound_definitions = [
            SoundEffect("slash", SoundType.SLASH, volume=0.8, pitch_variation=0.1, min_interval=0.05),
            SoundEffect("crit", SoundType.CRIT, volume=1.0, pitch_variation=0.05, min_interval=0.1),
            SoundEffect("level_up", SoundType.LEVEL_UP, volume=0.9, min_interval=1.0),
            SoundEffect("combo", SoundType.COMBO, volume=0.7, pitch_variation=0.15, min_interval=0.2),
            SoundEffect("coin", SoundType.COIN, volume=0.6, min_interval=0.05),
            SoundEffect("stamina_low", SoundType.STAMINA_LOW, volume=0.8, min_interval=2.0),
            SoundEffect("enemy_hit", SoundType.ENEMY_HIT, volume=0.7, pitch_variation=0.1, min_interval=0.1),
            SoundEffect("enemy_defeat", SoundType.ENEMY_DEFEAT, volume=0.9, min_interval=1.0),
            SoundEffect("button_click", SoundType.BUTTON_CLICK, volume=0.5, min_interval=0.05),
            SoundEffect("ui_hover", SoundType.UI_HOVER, volume=0.3, min_interval=0.02),
            SoundEffect("error", SoundType.ERROR, volume=0.8, min_interval=0.5)
        ]

        self.sound_effects = sound_definitions

    def load_sounds(self) -> None:
        """加载音效文件"""
        if not self.enabled:
            return

        # 尝试加载实际音效文件
        sound_files = {
            "slash": "sounds/slash.wav",
            "crit": "sounds/crit.wav",
            "level_up": "sounds/level_up.wav",
            "combo": "sounds/combo.wav",
            "coin": "sounds/coin.wav",
            "stamina_low": "sounds/stamina_low.wav",
            "enemy_hit": "sounds/enemy_hit.wav",
            "enemy_defeat": "sounds/enemy_defeat.wav",
            "button_click": "sounds/button_click.wav",
            "ui_hover": "sounds/ui_hover.wav",
            "error": "sounds/error.wav"
        }

        loaded_count = 0
        for name, path in sound_files.items():
            if self._load_sound_file(name, path):
                loaded_count += 1

        self.logger.info(f"Loaded {loaded_count} sound files")

        # 如果没有加载到任何音效文件，创建程序生成音效
        if loaded_count == 0:
            self._create_generated_sounds()

    def _load_sound_file(self, name: str, path: str) -> bool:
        """
        加载单个音效文件

        Args:
            name: 音效名称
            path: 文件路径

        Returns:
            是否加载成功
        """
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
            self.logger.debug(f"Loaded sound: {name} from {path}")
            return True
        except Exception as e:
            self.logger.debug(f"Failed to load sound {name} from {path}: {e}")
            return False

    def _create_generated_sounds(self) -> None:
        """创建程序生成的音效（当无法加载文件时使用）"""
        self.logger.info("Creating generated sound effects")

        # 生成各种音效
        self.sounds["slash"] = self._generate_slash_sound()
        self.sounds["crit"] = self._generate_crit_sound()
        self.sounds["level_up"] = self._generate_level_up_sound()
        self.sounds["combo"] = self._generate_combo_sound()
        self.sounds["coin"] = self._generate_coin_sound()
        self.sounds["stamina_low"] = self._generate_stamina_low_sound()
        self.sounds["enemy_hit"] = self._generate_enemy_hit_sound()
        self.sounds["enemy_defeat"] = self._generate_enemy_defeat_sound()
        self.sounds["button_click"] = self._generate_button_click_sound()
        self.sounds["ui_hover"] = self._generate_ui_hover_sound()
        self.sounds["error"] = self._generate_error_sound()

    def _generate_slash_sound(self) -> pygame.mixer.Sound:
        """生成砍击音效"""
        duration = 0.1
        sample_rate = self.sample_rate
        samples = int(duration * sample_rate)

        # 生成噪音波形
        noise = [random.uniform(-0.3, 0.3) for _ in range(samples)]

        # 应用包络（快速衰减）
        for i in range(samples):
            envelope = max(0, 1 - (i / samples) * 3)
            noise[i] *= envelope

        # 添加低频成分
        for i in range(samples):
            low_freq = 0.1 * math.sin(2 * math.pi * 100 * i / sample_rate)
            noise[i] += low_freq

        return self._create_sound_from_array(noise)

    def _generate_crit_sound(self) -> pygame.mixer.Sound:
        """生成暴击音效"""
        duration = 0.3
        sample_rate = self.sample_rate
        samples = int(duration * sample_rate)

        # 生成高频金属声
        sound = []
        for i in range(samples):
            # 高频正弦波
            high_freq = 0.3 * math.sin(2 * math.pi * 2000 * i / sample_rate)
            # 中频和谐波
            mid_freq = 0.2 * math.sin(2 * math.pi * 800 * i / sample_rate)

            # 包络
            envelope = max(0, 1 - (i / samples) * 2)

            sample = (high_freq + mid_freq) * envelope
            sound.append(sample)

        return self._create_sound_from_array(sound)

    def _generate_level_up_sound(self) -> pygame.mixer.Sound:
        """生成升级音效"""
        duration = 0.8
        sample_rate = self.sample_rate
        samples = int(duration * sample_rate)

        # 生成上升的音调
        sound = []
        for i in range(samples):
            # 频率从低到高
            freq = 400 + (1200 * i / samples)
            sample = 0.3 * math.sin(2 * math.pi * freq * i / sample_rate)

            # 包络（淡入淡出）
            if i < samples // 10:
                envelope = i / (samples // 10)  # 淡入
            elif i > samples * 9 // 10:
                envelope = (samples - i) / (samples // 10)  # 淡出
            else:
                envelope = 1.0

            sound.append(sample * envelope)

        return self._create_sound_from_array(sound)

    def _generate_combo_sound(self) -> pygame.mixer.Sound:
        """生成连击音效"""
        duration = 0.15
        sample_rate = self.sample_rate
        samples = int(duration * sample_rate)

        # 生成快速打击声
        sound = []
        for i in range(samples):
            # 多个频率叠加
            freq1 = 0.2 * math.sin(2 * math.pi * 600 * i / sample_rate)
            freq2 = 0.15 * math.sin(2 * math.pi * 1200 * i / sample_rate)

            # 短促的包络
            envelope = max(0, 1 - (i / samples) * 4)

            sample = (freq1 + freq2) * envelope
            sound.append(sample)

        return self._create_sound_from_array(sound)

    def _generate_coin_sound(self) -> pygame.mixer.Sound:
        """生成金币音效"""
        duration = 0.2
        sample_rate = self.sample_rate
        samples = int(duration * sample_rate)

        # 生成清脆的金属声
        sound = []
        for i in range(samples):
            # 高频金属声
            freq = 0.25 * math.sin(2 * math.pi * 3000 * i / sample_rate)

            # 添加谐波
            harmonic = 0.1 * math.sin(2 * math.pi * 6000 * i / sample_rate)

            # 快速衰减
            envelope = max(0, 1 - (i / samples) * 5)

            sample = (freq + harmonic) * envelope
            sound.append(sample)

        return self._create_sound_from_array(sound)

    def _generate_stamina_low_sound(self) -> pygame.mixer.Sound:
        """生成体力不足音效"""
        duration = 0.4
        sample_rate = self.sample_rate
        samples = int(duration * sample_rate)

        # 生成低频警告声
        sound = []
        for i in range(samples):
            # 低频脉冲
            freq = 0.3 * math.sin(2 * math.pi * 200 * i / sample_rate)

            # 脉冲包络
            pulse = math.sin(2 * math.pi * 4 * i / sample_rate)
            envelope = max(0, pulse) * (1 - i / samples)

            sample = freq * envelope
            sound.append(sample)

        return self._create_sound_from_array(sound)

    def _generate_enemy_hit_sound(self) -> pygame.mixer.Sound:
        """生成敌人受击音效"""
        duration = 0.12
        sample_rate = self.sample_rate
        samples = int(duration * sample_rate)

        # 生成沉闷的打击声
        sound = []
        for i in range(samples):
            # 低频成分
            low_freq = 0.4 * math.sin(2 * math.pi * 150 * i / sample_rate)

            # 噪音成分
            noise = 0.2 * random.uniform(-1, 1)

            # 快速衰减
            envelope = max(0, 1 - (i / samples) * 3)

            sample = (low_freq + noise) * envelope
            sound.append(sample)

        return self._create_sound_from_array(sound)

    def _generate_enemy_defeat_sound(self) -> pygame.mixer.Sound:
        """生成敌人 defeat 音效"""
        duration = 0.6
        sample_rate = self.sample_rate
        samples = int(duration * sample_rate)

        # 生成下降的音调
        sound = []
        for i in range(samples):
            # 频率从高到低
            freq = 800 - (400 * i / samples)
            sample = 0.3 * math.sin(2 * math.pi * freq * i / sample_rate)

            # 包络
            envelope = 1 - (i / samples)

            # 添加噪音
            noise = 0.1 * random.uniform(-1, 1) * envelope

            sound.append((sample + noise) * envelope)

        return self._create_sound_from_array(sound)

    def _generate_button_click_sound(self) -> pygame.mixer.Sound:
        """生成按钮点击音效"""
        duration = 0.05
        sample_rate = self.sample_rate
        samples = int(duration * sample_rate)

        # 生成短促的点击声
        sound = []
        for i in range(samples):
            # 高频点击
            freq = 0.2 * math.sin(2 * math.pi * 4000 * i / sample_rate)

            # 极短的包络
            envelope = max(0, 1 - (i / samples) * 10)

            sound.append(freq * envelope)

        return self._create_sound_from_array(sound)

    def _generate_ui_hover_sound(self) -> pygame.mixer.Sound:
        """生成UI悬停音效"""
        duration = 0.03
        sample_rate = self.sample_rate
        samples = int(duration * sample_rate)

        # 生成轻微的嗡嗡声
        sound = []
        for i in range(samples):
            # 中频
            freq = 0.1 * math.sin(2 * math.pi * 1000 * i / sample_rate)

            # 快速淡出
            envelope = max(0, 1 - (i / samples) * 5)

            sound.append(freq * envelope)

        return self._create_sound_from_array(sound)

    def _generate_error_sound(self) -> pygame.mixer.Sound:
        """生成错误音效"""
        duration = 0.3
        sample_rate = self.sample_rate
        samples = int(duration * sample_rate)

        # 生成错误提示声
        sound = []
        for i in range(samples):
            # 不和谐的频率组合
            freq1 = 0.2 * math.sin(2 * math.pi * 300 * i / sample_rate)
            freq2 = 0.15 * math.sin(2 * math.pi * 450 * i / sample_rate)

            # 包络
            envelope = max(0, 1 - (i / samples) * 2)

            sample = (freq1 + freq2) * envelope
            sound.append(sample)

        return self._create_sound_from_array(sound)

    def _create_sound_from_array(self, samples: List[float]) -> pygame.mixer.Sound:
        """
        从采样数组创建pygame Sound对象

        Args:
            samples: 采样数据

        Returns:
            pygame Sound对象
        """
        try:
            # 转换为16位整数
            int_samples = [int(sample * 32767) for sample in samples]

            # 创建字节数组
            sound_array = bytearray()
            for sample in int_samples:
                # 立体声，左右声道相同
                sound_array.extend(sample.to_bytes(2, byteorder='little', signed=True))
                sound_array.extend(sample.to_bytes(2, byteorder='little', signed=True))

            # 创建Sound对象
            sound = pygame.mixer.Sound(buffer=sound_array)
            return sound

        except Exception as e:
            self.logger.error(f"Failed to create sound from array: {e}")
            # 返回静音
            return pygame.mixer.Sound(buffer=bytearray(1024))

    def play_sound(self, sound_name: str, volume_override: Optional[float] = None) -> bool:
        """
        播放音效

        Args:
            sound_name: 音效名称
            volume_override: 音量覆盖

        Returns:
            是否播放成功
        """
        if not self.enabled:
            return False

        # 查找音效定义
        sound_effect = None
        for effect in self.sound_effects:
            if effect.name == sound_name:
                sound_effect = effect
                break

        if not sound_effect:
            self.logger.warning(f"Sound effect not found: {sound_name}")
            return False

        # 检查最小播放间隔
        current_time = time.time()
        if current_time - sound_effect.last_play_time < sound_effect.min_interval:
            return False

        # 获取音效对象
        if sound_name not in self.sounds:
            self.logger.warning(f"Sound file not loaded: {sound_name}")
            return False

        sound = self.sounds[sound_name]

        try:
            # 查找可用通道
            available_channel = self._get_available_channel()
            if not available_channel:
                self.logger.warning("No available audio channels")
                return False

            # 计算音量
            if volume_override is not None:
                volume = volume_override
            else:
                volume = sound_effect.volume

            # 应用音调变化（通过播放速度实现）
            if sound_effect.pitch_variation > 0:
                pitch_shift = 1.0 + random.uniform(-sound_effect.pitch_variation, sound_effect.pitch_variation)
                # 注意：pygame.mixer.Sound不支持音调变化，这里只记录
                pass

            # 设置音量并播放
            final_volume = volume * self.sfx_volume * self.master_volume
            sound.set_volume(final_volume)
            available_channel.play(sound)

            # 更新统计
            sound_effect.play_count += 1
            sound_effect.last_play_time = current_time
            self.stats['sounds_played'] += 1
            self.stats['most_played_sound'] = sound_name

            return True

        except Exception as e:
            self.logger.error(f"Failed to play sound {sound_name}: {e}")
            self.stats['sounds_failed'] += 1
            return False

    def _get_available_channel(self) -> Optional[pygame.mixer.Channel]:
        """获取可用的音频通道"""
        for channel in self.channels:
            if not channel.get_busy():
                return channel
        return None

    def play_sound_3d(self, sound_name: str, source_pos: Tuple[float, float, float],
                     listener_pos: Tuple[float, float, float]) -> bool:
        """
        播放3D定位音效

        Args:
            sound_name: 音效名称
            source_pos: 音源位置 (x, y, z)
            listener_pos: 听者位置 (x, y, z)

        Returns:
            是否播放成功
        """
        # 计算距离
        dx = source_pos[0] - listener_pos[0]
        dy = source_pos[1] - listener_pos[1]
        dz = source_pos[2] - listener_pos[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)

        # 计算音量衰减（距离越远音量越小）
        max_distance = 500
        if distance >= max_distance:
            return False

        volume = max(0, 1 - (distance / max_distance))

        return self.play_sound(sound_name, volume_override=volume)

    def stop_all_sounds(self) -> None:
        """停止所有音效"""
        try:
            pygame.mixer.stop()
        except Exception as e:
            self.logger.error(f"Failed to stop sounds: {e}")

    def set_master_volume(self, volume: float) -> None:
        """
        设置主音量

        Args:
            volume: 音量 (0.0 - 1.0)
        """
        self.master_volume = max(0.0, min(1.0, volume))

    def set_sfx_volume(self, volume: float) -> None:
        """
        设置音效音量

        Args:
            volume: 音量 (0.0 - 1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))

    def set_music_volume(self, volume: float) -> None:
        """
        设置音乐音量

        Args:
            volume: 音量 (0.0 - 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def enable_sound(self, enabled: bool) -> None:
        """
        启用/禁用音效

        Args:
            enabled: 是否启用
        """
        self.enabled = enabled
        if not enabled:
            self.stop_all_sounds()

    def get_sound_stats(self) -> Dict[str, Any]:
        """获取音效统计信息"""
        # 找出播放次数最多的音效
        most_played = max(self.sound_effects, key=lambda x: x.play_count, default=None)

        stats = self.stats.copy()
        if most_played:
            stats['most_played_sound'] = most_played.name
            stats['most_played_count'] = most_played.play_count

        # 添加音效列表信息
        stats['loaded_sounds'] = list(self.sounds.keys())
        stats['total_sound_effects'] = len(self.sound_effects)
        stats['available_channels'] = len([c for c in self.channels if not c.get_busy()])

        return stats

    def reset_stats(self) -> None:
        """重置统计数据"""
        self.stats = {
            'sounds_played': 0,
            'sounds_failed': 0,
            'total_play_time': 0.0,
            'most_played_sound': '',
            'last_update_time': time.time()
        }

        # 重置音效播放计数
        for effect in self.sound_effects:
            effect.play_count = 0
            effect.last_play_time = 0.0

    def cleanup(self) -> None:
        """清理资源"""
        try:
            self.stop_all_sounds()
            pygame.mixer.quit()
            self.logger.info("Sound system cleaned up")
        except Exception as e:
            self.logger.error(f"Error during sound cleanup: {e}")