from typing import List, Dict
import json
from pathlib import Path
from datetime import datetime
from .lottery_history_crawler import LotteryHistoryCrawler


class LotteryChecker:
    """大乐透中奖检查"""

    def __init__(self, data_file: str = None):
        if data_file is None:
            # Get the directory where this file is located
            current_dir = Path(__file__).parent
            # Go up two levels to reach the app root, then to data directory
            data_file = current_dir.parent / 'data' / 'lottery_history.json'
        self.data_file = Path(data_file)
        self.history_data = self.load_history_data()

    def load_history_data(self) -> List[Dict]:
        """加载历史开奖数据"""
        if not self.data_file.exists():
            raise FileNotFoundError(f"开奖数据文件不存在: {self.data_file}")
            
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def update_history_data(self) -> bool:
        """更新历史开奖数据"""
        try:
            crawler = LotteryHistoryCrawler(str(self.data_file))
            
            # 获取最新一期数据
            new_data = crawler.fetch_latest_data()
            if crawler.update_history_file(new_data):
                # 重新加载数据
                self.history_data = self.load_history_data()
                return True
            return False
            
        except Exception as e:
            print(f"更新开奖数据时出错: {str(e)}")
            return False

    def check_numbers(self, ticket_info: Dict) -> Dict:
        """检查彩票中奖情况"""
        period = ticket_info['period']
        
        try:
            # 获取最新一期的期号
            latest_period = max(str(item.get('period')) for item in self.history_data)
            
            # 如果期号大于最新一期，尝试更新数据
            if int(period) > int(latest_period):
                print(f"[信息] 期号 {period} 大于当前最新期号 {latest_period}，尝试更新数据...")
                if self.update_history_data():
                    print("[信息] 数据更新成功，重新获取最新期号...")
                    latest_period = max(str(item.get('period')) for item in self.history_data)
                else:
                    print("[信息] 没有新数据更新")
            
            # 再次检查期号
            if int(period) > int(latest_period):
                return {
                    "status": "pending",
                    "message": f"第{period}期尚未开奖，开奖后将通过邮件通知您",
                    "ticket_info": ticket_info,
                    "latest_period": latest_period
                }

            # 获取对应期号的开奖信息
            draw_info = next((item for item in self.history_data 
                            if str(item.get('period')) == str(period)), None)
            
            if not draw_info:
                return {
                    "status": "error",
                    "message": f"未找到期号 {period} 的开奖信息，请确认彩票期号是否正确，或等待该期开奖",
                    "ticket_info": ticket_info
                }

            # 检查每注号码
            results = []
            for bet_numbers in ticket_info['numbers']:
                # 打印调试信息
                print(f"\n检查号码: {bet_numbers}")
                print(f"开奖号码 - 红球: {draw_info['red_numbers']}, 蓝球: {draw_info['blue_numbers']}")
                
                # 分别处理红球和蓝球
                result = self.check_single_bet(
                    bet_numbers=bet_numbers,
                    draw_red_numbers=draw_info['red_numbers'],
                    draw_blue_numbers=draw_info['blue_numbers']
                )
                results.append({
                    "numbers": bet_numbers,
                    "draw_numbers": draw_info['red_numbers'] + draw_info['blue_numbers'],
                    "match_result": result
                })

            return {
                "status": "success",
                "period": period,
                "draw_date": draw_info.get('draw_date', '未知'),
                "results": results,
                "draw_numbers": draw_info['red_numbers'] + draw_info['blue_numbers']
            }

        except Exception as e:
            print(f"处理开奖数据时出错: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return {
                "status": "error",
                "message": f"处理开奖数据时出错: {str(e)}",
                "ticket_info": ticket_info
            }

    @staticmethod
    def check_single_bet(bet_numbers: List[str], draw_red_numbers: List[str], draw_blue_numbers: List[str]) -> Dict:
        """检查单注号码的中奖情况"""
        try:
            # 标准化号码格式（确保都是两位数格式的字符串）
            def normalize_number(num):
                return f"{int(str(num)):02d}"  # 确保先转为字符串再转为整数
            
            # 分离前区和后区号码，并标准化格式
            bet_front = {normalize_number(n) for n in bet_numbers[:5]}
            bet_back = {normalize_number(n) for n in bet_numbers[5:]}
            draw_front = {normalize_number(n) for n in draw_red_numbers}
            draw_back = {normalize_number(n) for n in draw_blue_numbers}

            # 打印调试信息
            print(f"投注号码（标准化后）- 前区: {bet_front}, 后区: {bet_back}")
            print(f"开奖号码（标准化后）- 前区: {draw_front}, 后区: {draw_back}")

            # 计算匹配数（使用集合运算）
            matched_front = bet_front & draw_front
            matched_back = bet_back & draw_back
            front_matches = len(matched_front)
            back_matches = len(matched_back)

            print(f"匹配结果 - 前区: {front_matches}个 {matched_front}, 后区: {back_matches}个 {matched_back}")

            # 判断中奖等级
            if front_matches == 5 and back_matches == 2:
                prize = "一等奖"
            elif front_matches == 5 and back_matches == 1:
                prize = "二等奖"
            elif (front_matches == 5 and back_matches == 0) or \
                    (front_matches == 4 and back_matches == 2):
                prize = "三等奖"
            elif (front_matches == 4 and back_matches == 1) or \
                    (front_matches == 3 and back_matches == 2):
                prize = "四等奖"
            elif (front_matches == 4 and back_matches == 0) or \
                    (front_matches == 3 and back_matches == 1) or \
                    (front_matches == 2 and back_matches == 2):
                prize = "五等奖"
            elif (front_matches == 3 and back_matches == 0) or \
                    (front_matches == 2 and back_matches == 1) or \
                    (front_matches == 1 and back_matches == 2) or \
                    (front_matches == 0 and back_matches == 2):
                prize = "六等奖"
            else:
                prize = "未中奖"

            # 返回匹配的具体号码，方便前端展示
            matched_front = sorted(list(matched_front))  # 排序以保持稳定显示
            matched_back = sorted(list(matched_back))

            return {
                "front_matches": front_matches,
                "back_matches": back_matches,
                "matched_numbers": {
                    "front": matched_front,
                    "back": matched_back
                },
                "prize": prize
            }

        except Exception as e:
            print(f"[错误] 检查中奖出错: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return {
                "front_matches": 0,
                "back_matches": 0,
                "matched_numbers": {
                    "front": [],
                    "back": []
                },
                "prize": "检查失败",
                "error": str(e)
            }


if __name__ == "__main__":
    # 测试用例
    checker = LotteryChecker()

    # 模拟OCR识别结果
    ticket_info = {
        'name': '超级大乐透',
        'period': '24001',
        'numbers': [
            ['01', '02', '03', '04', '05', '06', '07'],  # 测试号码
            ['11', '12', '13', '14', '15', '10', '11']  # 测试号码
        ]
    }

    # 检查中奖
    result = checker.check_numbers(ticket_info)

    # 打印结果
    print("\n=== 中奖检查结果 ===")
    if result['status'] == 'success':
        print(f"期号: {result['period']}")
        print(f"开奖日期: {result['draw_date']}")
        print("\n投注结果:")
        for i, bet_result in enumerate(result['results'], 1):
            numbers = bet_result['numbers']
            draw_numbers = bet_result['draw_numbers']
            match_result = bet_result['match_result']
            print(f"\n第{i}注:")
            print(f"投注号码: {' '.join(numbers[:5])} + {' '.join(numbers[5:])}")
            print(f"开奖号码: {' '.join(draw_numbers[:5])} + {' '.join(draw_numbers[5:])}")
            print(
                f"中奖情况: {match_result['prize']} (前区匹配{match_result['front_matches']}个, 后区匹配{match_result['back_matches']}个)")
    else:
        print(f"错误: {result['message']}")
