import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

pages = [
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-attention.html', 'attention'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-core.html', 'core'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-models.html', 'models'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-ops.html', 'ops'),
]

for fpath, name in pages:
    fname = os.path.basename(fpath)
    fsize = os.path.getsize(fpath)

    msg = MIMEMultipart()
    msg['From'] = '18913980939@163.com'
    msg['To'] = '125987347@qq.com'
    msg['Subject'] = f'vLLM Ascend panorama-{name}.html (函数说明已补)'

    body_text = f"""vLLM Ascend panorama-{name}.html 已更新。

文件：{fname}
大小：{fsize/1024:.1f} KB

更新内容：
- 已基于源码阅读，为每个函数的 item-desc span 填入中文功能描述
- 部分未匹配的函数以 (参见源码:funcname) 形式保留为占位标记
- 主要描述来源：源码 docstring、函数名启发、类成员模式
"""
    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

    with open(fpath, 'rb') as f:
        attach = MIMEApplication(f.read(), Name=fname)
    attach['Content-Disposition'] = f'attachment; filename="{fname}"'
    msg.attach(attach)

    server = smtplib.SMTP_SSL('smtp.163.com', 465)
    server.login('18913980939@163.com', '<SMTP_PASSWORD>')
    server.sendmail('18913980939@163.com', '125987347@qq.com', msg.as_string())
    server.quit()
    print(f'已发送 {fname} ({fsize/1024:.1f} KB)')