import os
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.utils.lottery_ocr import recognize_lottery_ticket
from app.utils.lottery_checker import LotteryChecker

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload_ticket():
    try:
        if 'ticket' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
            
        file = request.files['ticket']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
            
        if file and allowed_file(file.filename):
            # 保存文件
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # OCR识别
                print(f"开始OCR识别: {filepath}")  # 添加日志
                ticket_info = recognize_lottery_ticket(filepath)
                print(f"OCR结果: {ticket_info}")  # 添加日志
                
                if not ticket_info:
                    return jsonify({'error': '彩票识别失败'}), 400
                    
                # 检查是否已开奖
                print("开始检查中奖情况")  # 添加日志
                checker = LotteryChecker()
                result = checker.check_numbers(ticket_info)
                print(f"检查结果: {result}")  # 添加日志
                
                return jsonify(result)
            except Exception as e:
                import traceback
                print(f"处理过程中出错: {str(e)}")
                print(traceback.format_exc())  # 打印完整错误堆栈
                raise
            finally:
                # 确保临时文件被删除
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        return jsonify({'error': '不支持的文件类型'}), 400
        
    except Exception as e:
        import traceback
        print(f"Error: {str(e)}")
        print(traceback.format_exc())  # 打印完整错误堆栈
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS