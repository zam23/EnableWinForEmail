# EnableWinForEmail
## 项目简介
`EnableWinForEmail` 是一个用于 Windows 平台的锁屏/解锁监控程序。
当检测到当前会话被解锁时，程序会自动通过 SMTP 发送一封通知邮件。
## 主要功能
- 监听 Windows 会话锁定 (`WTS_SESSION_LOCK`) 和解锁 (`WTS_SESSION_UNLOCK`) 事件
- 监控到电脑解锁后发送邮件通知
- 记录运行日志到 `enable_log.txt`
## 项目结构
- `enable.py`：主程序文件，负责注册窗口、监听会话事件、发送邮件并记录日志。
- `email_config.json`：SMTP 邮件配置文件。
- `enable_log.txt`：程序运行日志，自动生成。
## 依赖
该项目依赖 Windows 专用模块和标准库：
- `pywin32`（提供 `win32gui`、`win32con`、`win32ts`）
- `smtplib`（标准库）
- `email.mime.text.MIMEText`（标准库）
## 配置
请编辑 `email_config.json`，填写你的邮件服务器与账户信息：
```json
{
  "smtp_server": "smtp.qq.com",
  "smtp_port": 587,
  "smtp_user": "your_email@example.com",
  "smtp_password": "your_smtp_password",
  "recipient_email": "recipient@example.com"
}
```
注意：使用 QQ 邮箱时，需要启用 SMTP 服务并使用授权码作为 `smtp_password`。
## 运行方式
在 Windows 环境下运行：
```bash
python enable.py
```
运行后，程序会输出状态信息：
- `程序已启动，开始监控电脑锁定/解锁状态...`
- `电脑已解锁` 或 `电脑已锁定`
按 `Ctrl+C` 可以退出程序。
## 核心逻辑
1. 初始化日志记录并读取 `email_config.json`。
2. 注册一个隐藏窗口，用于接收 Windows 会话变更通知。
3. 通过 `WTSRegisterSessionNotification` 注册当前会话的锁屏/解锁事件。
4. 在消息回调函数 `wndproc` 中处理事件：
   - 解锁时调用 `send_email_notification()` 发送邮件；
   - 锁定时设置状态标志 `is_locked = True`。
5. 通过 `win32gui.PumpWaitingMessages()` 持续处理消息循环。
## 注意事项
- 仅支持 Windows 系统，需安装 `pywin32`。
- `email_config.json` 中必须填写完整的 SMTP 信息，否则邮件发送会失败。
- 程序使用 TLS 加密连接邮件服务器。
- 如果使用的是企业邮箱或严格安全策略邮箱，需确认 SMTP 访问权限和端口是否可用。
## 改进建议
- 增加异常处理后自动重试邮件发送。
- 支持更多邮件服务配置，例如 SSL 端口、非 TLS 连接。
- 将日志输出到控制台和文件同时保留。
- 支持配置文件中设置多个收件人。
- 增加 Windows 服务/后台任务方式运行。
