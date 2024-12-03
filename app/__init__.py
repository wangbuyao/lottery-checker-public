from flask import Flask
from flask_cors import CORS
import os

# 创建 Flask 应用实例
app = Flask(__name__)
CORS(app)

# 配置上传文件存储路径
app.config['UPLOAD_FOLDER'] = 'app/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 确保必要的目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 添加密钥
app.secret_key = 'your-secret-key-here'

# 注册蓝图
from app.views import main
app.register_blueprint(main.bp)
