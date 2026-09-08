import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

fpath = r'D:\demo\202609\vllm-ascend\code-docs\panorama-root.html'
fname = os.path.basename(fpath)
fsize = os.path.getsize(fpath)

msg = MIMEMultipart()
msg['From'] = '18913980939@163.com'
msg['To'] = '125987347@qq.com'
msg['Subject'] = f'vLLM Ascend panorama-root.html (已补真实函数说明) -'

body_text = f"""vLLM Ascend panorama-root.html 已更新。

文件：{fname}
大小：{fsize/1024:.1f} KB

更新内容：
- 已读取 ascend_forward_context.py / platform.py / ascend_config.py / envs.py / utils.py / meta_registration.py / logger.py / config_utils.py / cpu_binding.py / profiling_config.py / batch_invariant.py / attention/*.py / compilation/*.py / core/*.py 等源码
- 基于源码内容为每个函数撰写了中文功能描述
- 在 HTML 中替换了 226 个 (功能说明) 占位符为真实描述
- 仍有 290 个未补充（主要在 __init__.py 及根模块的注册/工具函数中）

每函数说明 1 句话，基于实际代码逻辑（如：
- set_ascend_forward_context: 上下文管理器：注入 MoE 通信类型、mmrs 融合、layer_idx、mc2_mask 等 forward 状态
- select_moe_comm_method: 统一入口：根据设备型号、并行配置、token 数返回 MoE 通信方法

下一步：继续补全剩余 290 个函数的描述，或继续生成其他模块的 panorama 页面。
"""
msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

# 附件
with open(fpath, 'rb') as f:
    attach = MIMEApplication(f.read(), Name=fname)
attach['Content-Disposition'] = f'attachment; filename="{fname}"'
msg.attach(attach)

server = smtplib.SMTP_SSL('smtp.163.com', 465)
server.login('18913980939@163.com', '<SMTP_PASSWORD>')
server.sendmail('18913980939@163.com', '125987347@qq.com', msg.as_string())
server.quit()
print(f'已发送 {fname} ({fsize/1024:.1f} KB) 作为附件')
print(f'替换统计: 226 个真实描述，290 个待补充')