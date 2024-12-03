import requests
import json
from datetime import datetime, timedelta
import time
from pathlib import Path
from typing import List, Dict
import os

class LotteryHistoryCrawler:
    """获取大乐透历史开奖数据"""
    
    def __init__(self, data_file: str = None):
        if data_file is None:
            # Get the directory where this file is located
            current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            # Go up two levels to reach the app root, then to data directory
            data_file = current_dir.parent.parent / 'data' / 'lottery_history.json'
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # API配置
        self.url = "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry"
        self.params = {
            'gameNo': '85',        # 大乐透的游戏编号
            'provinceId': '0',
            'pageSize': '30',      # 每页条数
            'isVerify': '1',
            'pageNo': '1'          # 页码
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_latest_data(self) -> Dict:
        """获取最新一期开奖数据"""
        print("[信息] 开始获取最新开奖数据...")
        try:
            self.params['pageNo'] = '1'
            self.params['pageSize'] = '1'
            response = requests.get(self.url, params=self.params, headers=self.headers)
            
            if response.status_code != 200:
                print(f"[错误] 请求失败: {response.status_code}")
                return None
            
            data = response.json()
            if 'value' not in data or 'list' not in data['value'] or not data['value']['list']:
                print("[错误] 未获取到最新开奖数据")
                return None
            
            latest = data['value']['list'][0]
            result = {
                'period': latest['lotteryDrawNum'],
                'draw_date': latest['lotteryDrawTime'].split()[0],
                'red_numbers': latest['lotteryDrawResult'].split()[:5],
                'blue_numbers': latest['lotteryDrawResult'].split()[5:]
            }
            
            print(f"[找到] 最新期号: {result['period']} 开奖号码: {' '.join(result['red_numbers'])} + {' '.join(result['blue_numbers'])}")
            return result
            
        except Exception as e:
            print(f"[错误] 获取最新数据失败: {str(e)}")
            return None

    def update_history_file(self, new_data: Dict) -> bool:
        """更新历史数据文件"""
        try:
            if not new_data:
                return False
                
            # 读取现有数据
            existing_data = []
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # 检查是否已存在该期数据
            if existing_data and str(existing_data[0]['period']) >= str(new_data['period']):
                print(f"[信息] 当前数据已是最新（期号：{new_data['period']}）")
                return False
            
            # 将新数据添加到列表开头
            existing_data.insert(0, new_data)
            
            # 保存更新后的数据
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)
            print(f"[成功] 已更新最新开奖数据（期号：{new_data['period']}）")
            return True
            
        except Exception as e:
            print(f"[错误] 更新数据文件失败: {str(e)}")
            return False

    def fetch_all_history(self) -> List[Dict]:
        """获取所有历史开奖数据（仅在需要完整历史数据时使用）"""
        print("[信息] 开始获取历史开奖数据...")
        all_results = {}
        page = 1
        target_date = datetime(2019, 1, 1)  # 从2019年开始
        
        while True:
            try:
                self.params['pageNo'] = str(page)
                self.params['pageSize'] = '30'
                response = requests.get(self.url, params=self.params, headers=self.headers)
                
                if response.status_code != 200:
                    print(f"[错误] 请求失败: {response.status_code}")
                    break
                
                data = response.json()
                if 'value' not in data or 'list' not in data['value']:
                    break
                
                results = data['value']['list']
                if not results:
                    break
                
                for item in results:
                    try:
                        draw_date = datetime.strptime(item['lotteryDrawTime'].split()[0], '%Y-%m-%d')
                        if draw_date < target_date:
                            break
                        
                        period = item['lotteryDrawNum']
                        numbers = item['lotteryDrawResult'].split()
                        result = {
                            'period': period,
                            'draw_date': item['lotteryDrawTime'].split()[0],
                            'red_numbers': numbers[:5],
                            'blue_numbers': numbers[5:]
                        }
                        
                        all_results[period] = result
                        print(f"[找到] 期号: {period} 开奖号码: {' '.join(result['red_numbers'])} + {' '.join(result['blue_numbers'])}")
                        
                    except (ValueError, KeyError) as e:
                        print(f"[警告] 处理数据出错: {str(e)}")
                        continue

                if draw_date < target_date:
                    break
                
                page += 1
                time.sleep(1)  # 避免请求过于频繁
                
            except Exception as e:
                print(f"[错误] 获取数据失败: {str(e)}")
                break
        
        # 转换为列表格式
        history_list = [
            {
                'period': k,
                'draw_date': v['draw_date'],
                'red_numbers': v['red_numbers'],
                'blue_numbers': v['blue_numbers']
            }
            for k, v in all_results.items()
        ]
        
        # 保存数据
        if history_list:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(history_list, f, ensure_ascii=False, indent=4)
            print(f"\n[成功] 已保存 {len(history_list)} 条历史开奖数据至: {self.data_file}")
        
        return history_list

if __name__ == "__main__":
    print("=== 大乐透历史开奖数据获取 ===")
    crawler = LotteryHistoryCrawler()
    results = crawler.fetch_all_history()
    print("\n=== 程序执行完成 ===") 