import requests
import base64
import json
import re
from typing import List, Dict
from datetime import datetime
import configparser
import os
from pathlib import Path

# 禁用 macOS 的 tkinter 警告
os.environ['TK_SILENCE_DEPRECATION'] = '1'

API_KEY = "请填写你的API_KEY"
SECRET_KEY = "请填写你的SECRET_KEY"

def get_access_token() -> str:
    """获取百度云API access token"""
    url = f"https://aip.baidubce.com/oauth/2.0/token?client_id={API_KEY}&client_secret={SECRET_KEY}&grant_type=client_credentials"
    
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        print("[信息] 正在获取access_token...")
        response = requests.request("POST", url, headers=headers, data=payload)
        
        if response.status_code == 200:
            return str(response.json().get("access_token"))
        print(f"[错误] 获取access_token失败: {response.text}")
        return None
    except Exception as e:
        print(f"[错误] 获取access_token异常: {str(e)}")
        return None

def recognize_lottery_ticket(image_path: str) -> Dict:
    """识别单张彩票图片"""
    print(f"\n[步骤1] 开始处理图片: {image_path}")

    # 获取access_token
    access_token = get_access_token()
    if not access_token:
        return None

    try:
        # 读取图片文件
        with open(image_path, 'rb') as f:
            img = base64.b64encode(f.read()).decode()

        # 调用通用文字识别（高精度版）接口
        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={access_token}"

        payload = {
            'image': img,
            'detect_direction': 'false'
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

        print("[信息] 发送OCR请求...")
        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code != 200:
            print(f"[错误] OCR请求失败: {response.text}")
            return None

        result = response.json()

        if 'error_code' in result:
            print(f"[错误] OCR识别失败: {result['error_msg']}")
            return None

        # 合并所有文本
        all_text = ''.join(item['words'] for item in result.get('words_result', []))
        print(f"[文本] {all_text}")

        # 提取关键信息
        lottery_info = {
            'name': '',
            'period': '',
            'draw_date': '',
            'numbers': [],
            'image_path': image_path,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 识别彩票类型
        if '大乐透' in all_text:
            lottery_info['name'] = '超级大乐透'

        # 识别期号
        period_match = re.search(r'第(\d+)期', all_text)
        if period_match:
            lottery_info['period'] = period_match.group(1)

        # 识别开奖日期
        date_match = re.search(r'(\d{4})年(\d{2})月(\d{2})日开奖', all_text)
        if date_match:
            lottery_info['draw_date'] = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"

        # 识别投注号码
        # 将全角加号转换为半角
        all_text = all_text.replace('＋', '+')

        # 在加号前后各保留15个字符（足够包含一组号码）
        for match in re.finditer(r'\+', all_text):
            pos = match.start()
            # 提取加号前后的文本
            before_text = all_text[max(0, pos - 15):pos]
            after_text = all_text[pos + 1:pos + 16]

            # 提取数字
            front_numbers = re.findall(r'\d{2}', before_text)[-5:]  # 取最后5个两位数
            back_numbers = re.findall(r'\d{2}', after_text)[:2]  # 取前2个两位数

            if len(front_numbers) == 5 and len(back_numbers) == 2:
                try:
                    # 验证号码范围
                    if (all(1 <= int(n) <= 35 for n in front_numbers) and
                            all(1 <= int(n) <= 12 for n in back_numbers)):
                        number_group = front_numbers + back_numbers
                        # 去重检查
                        number_str = ' '.join(number_group)
                        if not any(number_str == ' '.join(nums) for nums in lottery_info['numbers']):
                            lottery_info['numbers'].append(number_group)
                            print(f"[找到] 投注号码: {' '.join(front_numbers)} + {' '.join(back_numbers)}")
                except ValueError:
                    continue

        return lottery_info

    except Exception as e:
        print(f"[错误] 处理过程出错: {str(e)}")
        return None
