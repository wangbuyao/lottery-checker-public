from celery import Celery
from app.models.ticket import Ticket
from app.utils.lottery_checker import LotteryChecker
from app.utils.notifier import send_notification

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def check_pending_tickets():
    # 获取所有待检查的彩票
    pending_tickets = Ticket.query.filter_by(status='pending').all()
    checker = LotteryChecker()
    
    for ticket in pending_tickets:
        ticket_info = {
            'period': ticket.period,
            'numbers': json.loads(ticket.numbers)
        }
        
        result = checker.check_numbers(ticket_info)
        if result['status'] == 'success':
            # 更新彩票状态
            ticket.status = 'checked'
            ticket.result = json.dumps(result)
            db.session.commit()
            
            # 发送通知
            send_notification(ticket.user_id, ticket.id, result) 