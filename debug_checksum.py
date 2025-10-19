import os
import sys
import json

# 添加项目根目录和src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.game.data_manager import DataManager, PlayerData, AIData, GameStats, GameSettings, SaveData
import time

def test_checksum_debug():
    """调试校验和问题"""
    # 创建测试数据
    player_data = PlayerData(
        level=1,
        exp=0,
        attack_power=10,
        weapon_tier=1,
        coins=0,
        ai_affinity=10,
        location="新手村",
        max_combo=0,
        max_stamina=100,
        crit_rate=0.05,
        play_time=0.0
    )
    
    ai_data = AIData(
        bond=10,
        mood="neutral",
        total_responses=0,
        personality_type="encouraging",
        learning_data={}
    )
    
    game_stats = GameStats(
        session_start_time=time.time(),
        last_save_time=time.time()
    )
    
    settings = GameSettings()
    
    save_data = SaveData(
        player=player_data,
        ai=ai_data,
        stats=game_stats,
        settings=settings,
        save_time=time.time(),
        save_version="1.0.0"
    )
    
    # 创建DataManager实例
    dm = DataManager("debug_saves")
    
    # 计算校验和
    checksum = dm._calculate_checksum(save_data)
    print(f"计算的校验和: {checksum}")
    
    # 设置校验和
    save_data.checksum = checksum
    
    # 转换为字典进行验证
    save_dict = json.loads(json.dumps(save_data.__dict__, default=lambda o: o.__dict__))
    
    print("保存的数据:")
    print(json.dumps(save_dict, indent=2, ensure_ascii=False))
    
    # 验证校验和
    is_valid = dm._validate_checksum(save_dict)
    print(f"校验和验证结果: {is_valid}")
    
    return is_valid

if __name__ == "__main__":
    test_checksum_debug()