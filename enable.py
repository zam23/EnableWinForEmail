import win32gui
import win32con
import win32ts
import smtplib
from email.mime.text import MIMEText
import time
import os
import sys
import logging
import json
from datetime import datetime

# 配置日志
exe_path = os.path.dirname(os.path.abspath(sys.argv[0]))
log_file = os.path.join(exe_path, 'enable_log.txt')
import os
import sys

# 手动定义会话事件常量（放在代码开头）
WTS_SESSION_LOCK = 0x7  # 会话锁定
WTS_SESSION_UNLOCK = 0x8  # 会话解锁

if not hasattr(win32con, 'WM_WTSSESSION_CHANGE'):
    win32con.WM_WTSSESSION_CHANGE = 0x02B1

# 获取当前可执行文件目录
if getattr(sys, 'frozen', False):
    # 打包后的环境
    exe_dir = os.path.dirname(sys.executable)
else:
    # 开发环境
    exe_dir = os.path.dirname(os.path.abspath(__file__))

log_path = os.path.join(exe_dir, 'enable_log.txt')
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.info("Application started successfully. Logging initialized.")

# 加载邮件配置
with open(os.path.join(exe_dir, 'email_config.json'), 'r') as f:
    email_config = json.load(f)

# 邮件配置
SMTP_SERVER = email_config['smtp_server']
SMTP_PORT = email_config['smtp_port']
SMTP_USER = email_config['smtp_user']
SMTP_PASSWORD = email_config['smtp_password']
RECIPIENT_EMAIL = email_config['recipient_email']

# 全局变量，记录锁定状态
is_locked = False

def send_email_notification():
    """发送电脑解锁通知邮件"""
    try:
        subject = "电脑已解锁通知"
        body = f"您的电脑已于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 被解锁。"
        
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = RECIPIENT_EMAIL
        
        # 连接到SMTP服务器并发送邮件
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # 启用TLS加密
            # 添加调试输出
            server.set_debuglevel(1)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logging.info("解锁通知邮件已发送")
        print("解锁通知邮件已发送")
        
    except Exception as e:
        logging.error(f"发送邮件失败: {str(e)}")
        print(f"发送邮件失败: {str(e)}")

def wndproc(hwnd, msg, wparam, lparam):
    global is_locked
    event = None
    try:
        """窗口消息处理函数"""
        if msg == win32con.WM_WTSSESSION_CHANGE:
            event = wparam
        
        # 检测到会话解锁事件
        if event == WTS_SESSION_UNLOCK:
            logging.info("检测到电脑解锁事件")
            print("电脑已解锁")
            send_email_notification()
            is_locked = False
            
        # 检测到会话锁定事件
        elif event == WTS_SESSION_LOCK:
            logging.info("检测到电脑锁定事件")
            print("电脑已锁定")
            is_locked = True
            
    except Exception as e:
        logging.error("Error in wndproc:", exc_info=True)
    return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

def main():
    """主函数"""
    logging.info("程序已启动，开始监控电脑锁定/解锁状态")
    print("程序已启动，开始监控电脑锁定/解锁状态...")
    print("按Ctrl+C退出程序")
    
    # 注册窗口类
    wc = win32gui.WNDCLASS()
    wc.lpfnWndProc = wndproc
    wc.hInstance = win32gui.GetModuleHandle(None)
    wc.lpszClassName = "UnlockMonitorClass"
    class_atom = win32gui.RegisterClass(wc)
    
    # 创建窗口
    hwnd = win32gui.CreateWindow(
        class_atom,
        "Unlock Monitor",
        0,
        0, 0, 0, 0,
        0,
        0,
        wc.hInstance,
        None
    )
    
    # 注册会话通知
    win32ts.WTSRegisterSessionNotification(
        hwnd,
        win32ts.NOTIFY_FOR_THIS_SESSION
    )
    
    try:
        # 消息循环
        while True:
            win32gui.PumpWaitingMessages()
            time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("用户中断程序")
        print("\n程序已退出")
    finally:
        # 取消注册会话通知
        win32ts.WTSUnRegisterSessionNotification(hwnd)

if __name__ == "__main__":
    main()
