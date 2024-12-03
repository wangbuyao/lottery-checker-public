from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.utils.lottery_ocr import recognize_lottery_ticket
from app.utils.lottery_checker import LotteryChecker
from app.models.ticket import Ticket

bp = Blueprint('ticket', __name__)

@bp.route('/upload', methods=['POST'])
@login_required
def upload_ticket():
    if 'ticket' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
        
    file = request.files['ticket']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
        
    # 保存文件
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # OCR识别
    ticket_info = recognize_lottery_ticket(filepath)
    if not ticket_info:
        return jsonify({'error': '彩票识别失败'}), 400
        
    # 保存到数据库
    ticket = Ticket(
        user_id=current_user.id,
        image_path=filepath,
        period=ticket_info['period'],
        numbers=json.dumps(ticket_info['numbers']),
        status='pending'
    )
    db.session.add(ticket)
    db.session.commit()
    
    # 检查是否已开奖
    checker = LotteryChecker()
    result = checker.check_numbers(ticket_info)
    
    if result['status'] == 'success':
        ticket.status = 'checked'
        ticket.result = json.dumps(result)
        db.session.commit()
        return jsonify(result)
    else:
        # 添加到待检查队列
        add_to_check_queue(ticket.id)
        return jsonify({'message': '彩票已保存，开奖后将通知您结果'}) 