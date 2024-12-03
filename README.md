# 大乐透彩票验证系统

一个基于 Flask 的网页应用，用于验证大乐透彩票中奖情况。

## 功能特点

- 支持彩票图片上传和OCR识别
- 自动识别彩票期号和投注号码
- 实时获取最新开奖数据
- 自动匹配中奖号码并显示中奖结果
- 支持多注号码同时验证
- 响应式设计，支持手机访问

## 技术栈

- Python 3.9+
- Flask (Web框架)
- OpenCV (图像处理)
- 百度OCR API (文字识别)
- Bootstrap 5 (前端框架)

## 安装说明

1. 克隆项目
```bash
git clone https://github.com/wangbuyao/lottery-checker-public.git
cd lottery-checker-public
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置百度OCR API
### 获取API密钥
1. 访问[百度智能云](https://cloud.baidu.com/)
2. 注册/登录百度账号
3. 点击右上角"控制台"
4. 在左侧菜单选择"文字识别OCR"，或直接访问[文字识别控制台](https://console.bce.baidu.com/ai/#/ai/ocr/overview/index)
5. 点击"创建应用"：
   - 应用名称：自定义，如"彩票识别"
   - 接口选择：文字识别 > 通用文字识别（高精度版）
   - 选择"服务器端"
6. 创建完成后，在应用列表中找到刚创建的应用
7. 查看并记录 API Key 和 Secret Key

### 配置项目
1. 复制配置文件模板：
```bash
cp config.ini.example config.ini
```

2. 编辑 config.ini，填入您的API密钥：
```ini
[BaiduOCR]
API_KEY = 您的API_Key
SECRET_KEY = 您的Secret_Key
```

5. 运行应用
```bash
python run.py
```

访问 http://localhost:5001 即可使用

## 使用说明

1. 点击上传按钮选择彩票图片
2. 系统自动识别彩票信息
3. 显示中奖结果

## 注意事项

- 请确保上传的彩票图片清晰可读
- 支持的彩票类型：大乐透
- 建议使用最新版本的Chrome或Firefox浏览器
- **重要**：请勿将您的 API 密钥提交到 Git 仓库
- 百度智能云OCR服务有免费使用额度，请注意查看具体额度信息

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request

## 安全提示

- 请妥善保管您的 API 密钥
- 建议在百度智能云控制台中设置 API 调用次数限制
- 定期检查 API 调用记录
- 不要在公共场合泄露配置文件
- 如果不小心泄露了密钥，请立即在百度智能云控制台重置密钥