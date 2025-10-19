import os
import sys
import json
import pygame

# 添加项目根目录和src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# 初始化pygame
pygame.init()

from src.game.player import Player
from src.ai.ai_manager import AIManager
from src.game.data_manager import DataManager

def final_debug():
    """最终调试存档加载问题"""
    print("=== 创建游戏组件 ===")
    player = Player()
    ai_manager = AIManager("rule_based", enable_learning=True)
    data_manager = DataManager("final_debug_saves")
    
    print("=== 创建新存档 ===")
    save_success = data_manager.create_new_save(player, ai_manager)
    print(f"创建存档结果: {save_success}")
    
    # 读取保存的文件内容
    try:
        with open("final_debug_saves/savegame.json", "r", encoding="utf-8") as f:
            saved_data1 = json.load(f)
        print(f"创建后保存的校验和: {saved_data1.get('checksum', 'N/A')}")
        print("创建后的数据:")
        print(json.dumps(saved_data1, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"读取保存文件失败: {e}")
    
    if save_success:
        print("=== 修改数据 ===")
        player.level = 5
        player.coins = 500
        player.max_combo = 25
        print(f"修改后玩家等级: {player.level}, 金币: {player.coins}, 最大连击: {player.max_combo}")
        
        print("=== 保存游戏 ===")
        save_success = data_manager.save_game(player, ai_manager)
        print(f"保存游戏结果: {save_success}")
        
        # 读取保存的文件内容
        try:
            with open("final_debug_saves/savegame.json", "r", encoding="utf-8") as f:
                saved_data2 = json.load(f)
            print(f"保存后保存的校验和: {saved_data2.get('checksum', 'N/A')}")
            print("保存后的数据:")
            print(json.dumps(saved_data2, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"读取保存文件失败: {e}")
        
        if save_success:
            print("=== 重置数据 ===")
            player.reset()
            ai_manager.reset_ai_state()
            print(f"重置后玩家等级: {player.level}, 金币: {player.coins}, 最大连击: {player.max_combo}")
            
            print("=== 重新加载游戏前检查文件 ===")
            try:
                with open("final_debug_saves/savegame.json", "r", encoding="utf-8") as f:
                    saved_data3 = json.load(f)
                print(f"加载前文件中的校验和: {saved_data3.get('checksum', 'N/A')}")
                print("加载前文件中的数据:")
                print(json.dumps(saved_data3, indent=2, ensure_ascii=False))
                
                # 手动计算校验和
                temp_checksum = saved_data3['checksum']
                saved_data3['checksum'] = ''
                # 移除动态时间戳字段
                if 'stats' in saved_data3 and isinstance(saved_data3['stats'], dict):
                    saved_data3['stats'] = saved_data3['stats'].copy()
                    saved_data3['stats'].pop('session_start_time', None)
                    saved_data3['stats'].pop('last_save_time', None)
                if 'save_time' in saved_data3:
                    saved_data3.pop('save_time', None)
                    
                data_str = json.dumps(saved_data3, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
                import hashlib
                calculated_checksum = hashlib.md5(data_str.encode()).hexdigest()
                print(f"手动计算的校验和: {calculated_checksum}")
                print(f"校验和匹配: {calculated_checksum == temp_checksum}")
                
            except Exception as e:
                print(f"读取保存文件失败: {e}")
            
            print("=== 加载游戏 ===")
            load_success = data_manager.load_game()
            print(f"加载游戏结果: {load_success}")

if __name__ == "__main__":
    final_debug()